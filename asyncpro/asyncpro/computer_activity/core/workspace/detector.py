"""
Workspace & Project Context Detection Engine.
Infers workspace context from file paths, working directories, git repository metadata, and process arguments.
"""
import os
from typing import Dict, List, Optional
from computer_activity.core.domain.events import CanonicalEvent


class WorkspaceDetector:
    """Detects active project workspace from file paths and process working directories."""

    @staticmethod
    def infer_workspace(events: List[CanonicalEvent]) -> Optional[str]:
        path_counts: Dict[str, int] = {}
        
        for evt in events:
            if evt.resource and ("/" in evt.resource or "\\" in evt.resource):
                normalized = evt.resource.replace("\\", "/")
                parts = normalized.split("/")
                # Find candidate project folder
                if len(parts) >= 2:
                    project_dir = parts[1] if parts[0] == "~" else parts[0]
                    if project_dir not in [".", "..", "", "home", "usr", "tmp", "Users"]:
                        path_counts[project_dir] = path_counts.get(project_dir, 0) + 1

        if path_counts:
            top_project = max(path_counts.items(), key=lambda x: x[1])[0]
            return top_project

        return "default_workspace"
