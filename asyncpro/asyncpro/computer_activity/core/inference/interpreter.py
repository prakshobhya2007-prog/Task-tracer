"""
Constrained Evidence Interpreter.
Binds Hybrid Retrieval evidence packages to Inference Providers,
enforcing prompt guards, schema validation, and evidence ledger recording.
"""
from typing import Optional
from computer_activity.core.domain.insights import InsightEnvelope
from computer_activity.core.inference.provider import InferenceProvider, MockLLMProvider
from computer_activity.core.retrieval.hybrid import EvidencePackage
from computer_activity.security.prompt_guard.guard import PromptGuard
from computer_activity.storage.repositories.insight_repository import InsightRepository


class ConstrainedInterpreter:
    """Interprets evidence packages using schema-validated LLM inference."""

    def __init__(
        self,
        provider: Optional[InferenceProvider] = None,
        insight_repo: Optional[InsightRepository] = None,
    ):
        self.provider = provider or MockLLMProvider()
        self.insight_repo = insight_repo

    def interpret(self, evidence_package: EvidencePackage) -> InsightEnvelope:
        """Processes evidence package and returns schema-validated insight."""
        if not evidence_package.has_sufficient_evidence:
            insight = InsightEnvelope(
                observation="No relevant activity events found in store.",
                inference="Insufficient evidence to generate an activity inference.",
                confidence_score=0.0,
                evidence=[],
                unknown_disclaimer="Explicitly insufficient evidence available in telemetry database.",
                detector="constrained_interpreter_v1",
            )
            if self.insight_repo:
                self.insight_repo.save_insight(insight)
            return insight

        # 1. Format payload securely with PromptGuard
        payload_data = evidence_package.to_dict()
        safe_prompt_payload = PromptGuard.format_evidence_payload(payload_data)

        # 2. Invoke Inference Provider
        insight = self.provider.interpret_evidence(safe_prompt_payload, evidence_package.query)

        # 3. Attach exact event IDs and episode IDs to Evidence Ledger
        insight.event_ids = [e.event_id for e in evidence_package.retrieved_events]
        insight.episode_ids = [ep.episode_id for ep in evidence_package.retrieved_episodes]

        # 4. Save to Insight Repository ledger if available
        if self.insight_repo:
            self.insight_repo.save_insight(insight)

        return insight
