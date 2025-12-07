"""Auto-load compatibility helpers before the app starts."""

from __future__ import annotations

import sys
from pathlib import Path

def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "app").is_dir():
            return parent
    return candidate.parents[4]

project_root = _find_repo_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.torchvision_compat import ensure_functional_tensor_alias

ensure_functional_tensor_alias()
