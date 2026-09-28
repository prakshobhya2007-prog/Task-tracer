"""
FastAPI Local Intelligence API.
Exposes clean internal API endpoints for dashboard views, natural-language query,
pause controls, and privacy management.
"""
from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from computer_activity.collectors.common.synthetic import SyntheticEventGenerator
from computer_activity.core.anomaly.detector import AnomalyDetector
from computer_activity.core.domain.events import CanonicalEvent
from computer_activity.core.domain.insights import InsightEnvelope
from computer_activity.core.embeddings.provider import EmbeddingsProvider
from computer_activity.core.features.extractor import FeatureExtractor
from computer_activity.core.graph.behaviour_graph import BehaviourGraph
from computer_activity.core.ingestion.queue import IngestionQueue
from computer_activity.core.inference.interpreter import ConstrainedInterpreter
from computer_activity.core.privacy.firewall import PrivacyFirewall
from computer_activity.core.retrieval.hybrid import HybridRetriever
from computer_activity.core.sessionization.engine import Sessionizer
from computer_activity.storage.migrations.runner import MigrationRunner
from computer_activity.storage.repositories.episode_repository import EpisodeRepository
from computer_activity.storage.repositories.event_repository import EventRepository
from computer_activity.storage.repositories.insight_repository import InsightRepository
from computer_activity.storage.repositories.retention_repository import RetentionRepository
from computer_activity.storage.sqlite.database import Database

# Initialize core services
db = Database("computer_activity.db")
migration_runner = MigrationRunner(db)
migration_runner.run_migrations()

event_repo = EventRepository(db)
episode_repo = EpisodeRepository(db)
insight_repo = InsightRepository(db)
retention_repo = RetentionRepository(db)

firewall = PrivacyFirewall()
ingestion_queue = IngestionQueue()
sessionizer = Sessionizer()
feature_extractor = FeatureExtractor()
anomaly_detector = AnomalyDetector()
graph = BehaviourGraph()
embeddings_provider = EmbeddingsProvider()

retriever = HybridRetriever(event_repo, episode_repo, graph, embeddings_provider)
interpreter = ConstrainedInterpreter(insight_repo=insight_repo)

app = FastAPI(
    title="AI Computer Activity Intelligence Platform API",
    description="Local-first, evidence-driven activity intelligence service.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NaturalLanguageQueryRequest(BaseModel):
    query: str


class PauseRequest(BaseModel):
    pause: bool


@app.get("/api/collection/status")
def get_collection_status() -> Dict[str, Any]:
    metrics = ingestion_queue.get_metrics()
    return {
        "status": "Paused" if firewall.is_paused else "Monitoring",
        "is_paused": firewall.is_paused,
        "excluded_applications": list(firewall.excluded_applications),
        "metrics": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/collection/pause")
def toggle_pause(req: PauseRequest) -> Dict[str, Any]:
    firewall.update_settings(is_paused=req.pause)
    return {
        "status": "Paused" if firewall.is_paused else "Monitoring",
        "is_paused": firewall.is_paused,
    }


@app.get("/api/timeline")
def get_timeline(limit: int = 100) -> Dict[str, Any]:
    events = event_repo.get_recent_events(limit=limit)
    episodes = episode_repo.get_recent_episodes(limit=20)
    return {
        "events": [e.to_dict() for e in events],
        "episodes": [ep.to_dict() for ep in episodes],
    }


@app.get("/api/episodes")
def get_episodes(limit: int = 50) -> List[Dict[str, Any]]:
    episodes = episode_repo.get_recent_episodes(limit=limit)
    return [ep.to_dict() for ep in episodes]


@app.get("/api/insights")
def get_insights(limit: int = 50) -> List[Dict[str, Any]]:
    insights = insight_repo.get_recent_insights(limit=limit)
    return [ins.to_dict() for ins in insights]


@app.get("/api/anomalies")
def get_anomalies() -> List[Dict[str, Any]]:
    episodes = episode_repo.get_recent_episodes(limit=20)
    anomalies = []
    for ep in episodes:
        feats = feature_extractor.extract_features(ep, [])
        score, reasons = anomaly_detector.evaluate_episode(ep, feats)
        if score > 0.3:
            anomalies.append({
                "episode_id": ep.episode_id,
                "start_time": ep.start_time,
                "score": score,
                "reasons": reasons,
                "applications": ep.applications,
                "switch_count": ep.switch_count,
            })
    return anomalies


@app.get("/api/graph")
def get_graph() -> Dict[str, Any]:
    return graph.to_dict()


@app.post("/api/query")
def process_query(req: NaturalLanguageQueryRequest) -> Dict[str, Any]:
    evidence_package = retriever.retrieve(req.query)
    insight = interpreter.interpret(evidence_package)
    return {
        "query": req.query,
        "evidence_package": evidence_package.to_dict(),
        "insight": insight.to_dict(),
    }


@app.post("/api/data/delete")
def delete_data(scope: str = Query("today")) -> Dict[str, Any]:
    if scope == "all":
        res = retention_repo.delete_all_data()
    else:
        res = retention_repo.clear_today()
    return {"status": "success", "scope": scope, "result": res}


@app.get("/api/data/export")
def export_data() -> Dict[str, Any]:
    return retention_repo.export_all_data()


@app.post("/api/replay/run")
def run_replay_scenario(scenario: str = Query("cpp_debugging_loop")) -> Dict[str, Any]:
    if scenario == "context_switching":
        raw_events = SyntheticEventGenerator.generate_context_switching_scenario()
    else:
        raw_events = SyntheticEventGenerator.generate_cpp_debugging_scenario()

    # Pass events through Ingestion & Firewall -> Save to DB -> Sessionize
    processed_events = []
    for evt in raw_events:
        safe_evt = firewall.process_event(evt)
        if safe_evt:
            processed_events.append(safe_evt)

    event_repo.save_batch(processed_events)

    # Sessionize and calculate features
    episodes = sessionizer.sessionize(processed_events)
    for ep in episodes:
        episode_repo.save_episode(ep)
        ep_events = [e for e in processed_events if e.event_id in ep.event_ids]
        graph.ingest_episode(ep, ep_events)

    # Generate insight
    evidence_pkg = retriever.retrieve(scenario)
    insight = interpreter.interpret(evidence_pkg)

    return {
        "status": "success",
        "scenario": scenario,
        "events_count": len(processed_events),
        "episodes_count": len(episodes),
        "insight": insight.to_dict(),
    }


# Serve UI static files if ui directory contains index.html
ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_dir):
    @app.get("/")
    def read_index():
        idx_file = os.path.join(ui_dir, "index.html")
        if os.path.exists(idx_file):
            return FileResponse(idx_file)
        return JSONResponse({"status": "API online", "docs": "/docs"})

    app.mount("/static", StaticFiles(directory=ui_dir), name="static")
