"""
Sequence Mining Engine.
Mines frequent action sequences, n-grams, and repeated workflow patterns (e.g., edit -> compile -> crash).
"""
from collections import Counter
from typing import Dict, List, Tuple
from computer_activity.core.domain.episodes import EpisodeEnvelope


class SequenceMiner:
    """Mines frequent sub-sequences and repeated action loops from episodes."""

    def __init__(self, min_ngram_len: int = 2, max_ngram_len: int = 4):
        self.min_ngram_len = min_ngram_len
        self.max_ngram_len = max_ngram_len

    def mine_patterns(self, episodes: List[EpisodeEnvelope], min_support: int = 2) -> List[Dict]:
        """Detects recurring n-gram patterns across provided episodes."""
        ngram_counts: Counter[Tuple[str, ...]] = Counter()

        for ep in episodes:
            seq = ep.action_sequence
            for n in range(self.min_ngram_len, min(len(seq) + 1, self.max_ngram_len + 1)):
                for i in range(len(seq) - n + 1):
                    ngram = tuple(seq[i:i + n])
                    ngram_counts[ngram] += 1

        patterns = []
        for ngram, freq in ngram_counts.most_common():
            if freq >= min_support:
                pattern_label = self._label_pattern(ngram)
                patterns.append({
                    "sequence": list(ngram),
                    "frequency": freq,
                    "label": pattern_label,
                    "confidence": min(1.0, 0.5 + (freq * 0.1)),
                })

        return patterns

    def _label_pattern(self, ngram: Tuple[str, ...]) -> str:
        seq_str = " -> ".join(ngram).lower()
        if "process.exited" in seq_str and "g++" in seq_str or "compile" in seq_str or "a.out" in seq_str:
            return "Repeated edit-compile-failure loop"
        elif "browser" in seq_str and ("stackoverflow" in seq_str or "navigated" in seq_str):
            return "Documentation research loop"
        elif "window.focused" in seq_str and len(set(ngram)) >= 3:
            return "Rapid application context switching"
        return "Repeated action sequence"
