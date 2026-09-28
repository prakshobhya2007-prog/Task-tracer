"""
Workflow Completion & State Machine Engine.
Tracks workflows as INITIATED -> ACTIVE -> REPEATED -> BLOCKED -> RESUMED -> COMPLETED.
"""
from enum import Enum
from typing import Dict, List
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.episodes import EpisodeEnvelope


class WorkflowState(str, Enum):
    INITIATED = "INITIATED"
    ACTIVE = "ACTIVE"
    REPEATED = "REPEATED"
    BLOCKED = "BLOCKED"
    RESUMED = "RESUMED"
    COMPLETED = "COMPLETED"


class WorkflowTracker:
    """Tracks state and completion criteria of activity workflows."""

    @staticmethod
    def evaluate_workflow_state(episode: EpisodeEnvelope, events: List[CanonicalEvent]) -> Dict[str, str]:
        if episode.failure_count > 0 and episode.success_count == 0:
            state = WorkflowState.BLOCKED
            reason = f"Blocked by {episode.failure_count} unresolved execution failure(s)."
        elif episode.failure_count > 0 and episode.success_count > 0:
            state = WorkflowState.COMPLETED
            reason = "Workflow resumed and completed successfully after resolving failure."
        elif episode.success_count > 0 or any("git commit" in e.resource.lower() for e in events if e.resource):
            state = WorkflowState.COMPLETED
            reason = "Successful completion signal observed (clean exit / commit)."
        elif episode.switch_count > 10:
            state = WorkflowState.REPEATED
            reason = "High repetition / navigation cycle observed."
        else:
            state = WorkflowState.ACTIVE
            reason = "Active in-progress episode."

        return {
            "state": state.value,
            "reason": reason,
        }
