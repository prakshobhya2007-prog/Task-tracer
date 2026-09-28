"""
Core Domain Entities: Application, Process, File, Domain, Workspace.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ApplicationEntity:
    name: str
    category: str = "general"
    dwell_time_seconds: float = 0.0
    focus_count: int = 0


@dataclass
class ProcessEntity:
    pid: int
    name: str
    executable: str
    instance_id: str
    exit_code: Optional[int] = None


@dataclass
class FileEntity:
    path: str
    sanitized_path: str
    extension: str
    modification_count: int = 0


@dataclass
class DomainEntity:
    domain: str
    visit_count: int = 0


@dataclass
class WorkspaceEntity:
    workspace_id: str
    name: str
    path: str
    files: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    processes: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
