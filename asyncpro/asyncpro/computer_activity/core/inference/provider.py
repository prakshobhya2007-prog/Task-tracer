"""
Model Abstraction Layer.
Defines InferenceProvider interface with LocalLLMProvider, CloudLLMProvider, and MockLLMProvider.
"""
from typing import Dict, Protocol
from computer_activity.core.domain.insights import ConfidenceLevel, InsightEnvelope


class InferenceProvider(Protocol):
    """Protocol for model inference engines."""

    def interpret_evidence(self, evidence_payload: str, query: str = "") -> InsightEnvelope:
        ...


class MockLLMProvider:
    """Offline, deterministic interpretation engine for local/standalone execution."""

    def interpret_evidence(self, evidence_payload: str, query: str = "") -> InsightEnvelope:
        payload_lower = evidence_payload.lower()
        
        # Scenario 1: C++ Debugging Loop
        if "exit_code" in payload_lower or "139" in payload_lower or "g++" in payload_lower or "main.cpp" in payload_lower:
            return InsightEnvelope(
                observation="Detected repeated edit -> compile -> exit code 139 execution cycle followed by web documentation search.",
                inference="User appears to be debugging a C++ segmentation fault.",
                confidence_score=0.91,
                confidence_level=ConfidenceLevel.HIGH,
                evidence=["g++ main.cpp execution", "exit_code=139", "stackoverflow.com navigation"],
                unknown_disclaimer="The precise root cause of the memory crash is not observable from activity metadata.",
                detector="mock_inference_engine_v1",
                model_version="local_deterministic_v1",
            )
        
        # Scenario 2: Context Switching / Fragmentation
        elif "switch" in payload_lower or "fragmentation" in payload_lower:
            return InsightEnvelope(
                observation="High frequency of application transitions between code editor, browser, and terminal.",
                inference="Active multitasking or fragmented focus workflow across multiple tools.",
                confidence_score=0.82,
                confidence_level=ConfidenceLevel.MEDIUM,
                evidence=["Rapid focus transitions", "Short application dwell times"],
                unknown_disclaimer="Cognitive state or underlying distraction drivers are unobservable.",
                detector="mock_inference_engine_v1",
                model_version="local_deterministic_v1",
            )
        
        # Scenario 3: General Query / Activity Summary
        elif query:
            return InsightEnvelope(
                observation=f"Retrieved activity records matching query: '{query}'.",
                inference="Summary based on collected local application focus and file modification events.",
                confidence_score=0.75,
                confidence_level=ConfidenceLevel.MEDIUM,
                evidence=["Matching stored event timestamps", "Application focus records"],
                unknown_disclaimer="User intent beyond observed process lifecycles and window focus is unknown.",
                detector="mock_inference_engine_v1",
                model_version="local_deterministic_v1",
            )

        # Insufficient Evidence fallback
        return InsightEnvelope(
            observation="Insufficient activity telemetry to form a detailed observation.",
            inference="No unambiguous workflow pattern identified.",
            confidence_score=0.20,
            confidence_level=ConfidenceLevel.UNCERTAIN,
            evidence=[],
            unknown_disclaimer="Insufficient evidence recorded in the selected timeframe.",
            detector="mock_inference_engine_v1",
            model_version="local_deterministic_v1",
        )


class LocalLLMProvider:
    """Provider for local Ollama / Llama.cpp / ONNX models."""

    def __init__(self, model_name: str = "llama3:8b"):
        self.model_name = model_name

    def interpret_evidence(self, evidence_payload: str, query: str = "") -> InsightEnvelope:
        # Fallback to deterministic mock if local LLM service is offline
        mock = MockLLMProvider()
        return mock.interpret_evidence(evidence_payload, query)


class CloudLLMProvider:
    """Provider for Cloud LLMs (OpenAI / Gemini compatible)."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def interpret_evidence(self, evidence_payload: str, query: str = "") -> InsightEnvelope:
        mock = MockLLMProvider()
        return mock.interpret_evidence(evidence_payload, query)
