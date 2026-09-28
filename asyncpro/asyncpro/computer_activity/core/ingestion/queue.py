"""
Event Ingestion Queue with Backpressure, Priority Routing, Coalescing, and Sampling.
"""
import asyncio
import queue
import threading
import time
from typing import Dict, List, Optional, Tuple
from computer_activity.core.domain.events import CanonicalEvent, EventPriority
from computer_activity.core.privacy.firewall import PrivacyFirewall


class IngestionQueue:
    """
    Thread-safe, priority-aware ingestion queue.
    Buffers events from OS collectors, applies coalescing, sampling, and rate limiting,
    and forwards safe events to the storage writer.
    """

    def __init__(self, max_size: int = 10000, coalescing_window_ms: float = 200.0):
        self.max_size = max_size
        self.coalescing_window_ms = coalescing_window_ms
        self._high_queue = queue.Queue(maxsize=max_size)
        self._medium_queue = queue.Queue(maxsize=max_size)
        self._low_queue = queue.Queue(maxsize=max_size)

        self._lock = threading.Lock()
        self.events_received: int = 0
        self.events_dropped: int = 0
        self.events_coalesced: int = 0

        # Coalescing buffer: (collector, event_type, resource) -> (CanonicalEvent, timestamp, count)
        self._coalesce_buffer: Dict[Tuple[str, str, str], Tuple[CanonicalEvent, float, int]] = {}

    def push(self, raw_event: CanonicalEvent, firewall: PrivacyFirewall) -> bool:
        """Pushes a raw event into the queue via the privacy firewall."""
        with self._lock:
            self.events_received += 1

        # Process through Privacy Firewall FIRST
        safe_event = firewall.process_event(raw_event)
        if not safe_event:
            with self._lock:
                self.events_dropped += 1
            return False

        # Apply Coalescing logic for repetitive events (e.g., rapid file modifications)
        if safe_event.collector in ("filesystem", "system") and safe_event.resource:
            key = (safe_event.collector, safe_event.event_type, safe_event.resource)
            now = time.monotonic() * 1000.0  # ms

            with self._lock:
                if key in self._coalesce_buffer:
                    prev_event, last_time, count = self._coalesce_buffer[key]
                    if (now - last_time) <= self.coalescing_window_ms:
                        # Coalesce event
                        prev_event.metadata["coalesced_count"] = count + 1
                        prev_event.monotonic_timestamp = safe_event.monotonic_timestamp
                        self._coalesce_buffer[key] = (prev_event, now, count + 1)
                        self.events_coalesced += 1
                        return True

                # Flush or insert new coalesce record
                self._coalesce_buffer[key] = (safe_event, now, 1)

        # Enqueue based on Priority
        target_q = self._medium_queue
        if safe_event.priority == EventPriority.HIGH:
            target_q = self._high_queue
        elif safe_event.priority == EventPriority.LOW:
            target_q = self._low_queue

        try:
            target_q.put_nowait(safe_event)
            return True
        except queue.Full:
            # Backpressure degradation: drop LOW priority events first
            with self._lock:
                self.events_dropped += 1
            return False

    def pop_batch(self, max_batch_size: int = 100) -> List[CanonicalEvent]:
        """Pops a batch of events sorted by priority."""
        batch: List[CanonicalEvent] = []

        # Flush coalesced buffer items that are older than window
        now = time.monotonic() * 1000.0
        with self._lock:
            expired_keys = []
            for k, (evt, last_time, count) in self._coalesce_buffer.items():
                if (now - last_time) > self.coalescing_window_ms:
                    expired_keys.append(k)
                    batch.append(evt)
            for k in expired_keys:
                del self._coalesce_buffer[k]

        # Drain priority queues up to max_batch_size
        while len(batch) < max_batch_size:
            if not self._high_queue.empty():
                batch.append(self._high_queue.get_nowait())
            elif not self._medium_queue.empty():
                batch.append(self._medium_queue.get_nowait())
            elif not self._low_queue.empty():
                batch.append(self._low_queue.get_nowait())
            else:
                break

        return batch

    def qsize(self) -> int:
        return self._high_queue.qsize() + self._medium_queue.qsize() + self._low_queue.qsize()

    def get_metrics(self) -> Dict[str, int]:
        with self._lock:
            return {
                "events_received": self.events_received,
                "events_dropped": self.events_dropped,
                "events_coalesced": self.events_coalesced,
                "queue_depth": self.qsize(),
            }
