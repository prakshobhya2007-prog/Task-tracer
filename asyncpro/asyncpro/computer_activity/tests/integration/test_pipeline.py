"""
Integration Test for End-to-End Activity Intelligence Pipeline.
Verifies synthetic generator -> firewall -> queue -> SQLite -> sessionizer -> feature extractor -> anomaly detector -> hybrid retrieval -> constrained interpreter.
"""
import os
import pytest
from computer_activity.collectors.common.synthetic import SyntheticEventGenerator
from computer_activity.core.anomaly.detector import AnomalyDetector
from computer_activity.core.embeddings.provider import EmbeddingsProvider
from computer_activity.core.features.extractor import FeatureExtractor
from computer_activity.core.graph.behaviour_graph import BehaviourGraph
from computer_activity.core.inference.interpreter import ConstrainedInterpreter
from computer_activity.core.privacy.firewall import PrivacyFirewall
from computer_activity.core.retrieval.hybrid import HybridRetriever
from computer_activity.core.sessionization.engine import Sessionizer
from computer_activity.storage.migrations.runner import MigrationRunner
from computer_activity.storage.repositories.episode_repository import EpisodeRepository
from computer_activity.storage.repositories.event_repository import EventRepository
from computer_activity.storage.repositories.insight_repository import InsightRepository
from computer_activity.storage.sqlite.database import Database


def test_full_intelligence_pipeline(tmp_path):
    db_file = os.path.join(tmp_path, "test_activity.db")
    db = Database(db_file)
    runner = MigrationRunner(db)
    runner.run_migrations()

    event_repo = EventRepository(db)
    episode_repo = EpisodeRepository(db)
    insight_repo = InsightRepository(db)
    firewall = PrivacyFirewall()

    # 1. Generate synthetic debugging loop events
    raw_events = SyntheticEventGenerator.generate_cpp_debugging_scenario()
    assert len(raw_events) > 0

    # 2. Process through Privacy Firewall
    safe_events = [fw_evt for evt in raw_events if (fw_evt := firewall.process_event(evt))]
    assert len(safe_events) == len(raw_events)

    # 3. Store in SQLite
    event_repo.save_batch(safe_events)
    loaded_events = event_repo.get_recent_events()
    assert len(loaded_events) == len(safe_events)

    # 4. Sessionize into Episodes
    sessionizer = Sessionizer()
    episodes = sessionizer.sessionize(safe_events)
    assert len(episodes) >= 1

    for ep in episodes:
        episode_repo.save_episode(ep)

    # 5. Extract Deterministic Features
    feats = FeatureExtractor.extract_features(episodes[0], safe_events)
    assert feats["failure_count"] == 2.0

    # 6. Anomaly Detection
    detector = AnomalyDetector()
    score, reasons = detector.evaluate_episode(episodes[0], feats)
    assert score > 0.3
    assert len(reasons) > 0

    # 7. Behaviour Graph & Embeddings
    graph = BehaviourGraph()
    graph.ingest_episode(episodes[0], safe_events)
    emb_provider = EmbeddingsProvider()

    # 8. Hybrid Retrieval & Constrained Interpretation
    retriever = HybridRetriever(event_repo, episode_repo, graph, emb_provider)
    evidence_pkg = retriever.retrieve("debugging C++ crash")
    assert evidence_pkg.has_sufficient_evidence

    interpreter = ConstrainedInterpreter(insight_repo=insight_repo)
    insight = interpreter.interpret(evidence_pkg)

    # 9. Validate Insight Schema Rules
    assert insight.observation != ""
    assert insight.inference != ""
    assert insight.confidence_score > 0.0
    assert len(insight.evidence) > 0
    assert insight.unknown_disclaimer != ""
