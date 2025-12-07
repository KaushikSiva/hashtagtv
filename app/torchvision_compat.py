"""Helpers that re-expose the old torchvision import path on newer installations."""

from __future__ import annotations

import sys
from importlib import import_module
from types import ModuleType

__all__ = ["ensure_functional_tensor_alias"]


def ensure_functional_tensor_alias() -> None:
    """Create a fake torchvision.transforms.functional_tensor module if needed."""
    module_name = "torchvision.transforms.functional_tensor"
    if module_name in sys.modules:
        return

    try:
        import_module(module_name)
        return
    except ModuleNotFoundError:
        pass

    try:
        source = import_module("torchvision.transforms._functional_tensor")
    except ModuleNotFoundError:
        return

    alias = ModuleType(module_name)
    for attr in dir(source):
        if attr.startswith("__") and attr != "__all__":
            continue
        setattr(alias, attr, getattr(source, attr))
    alias.__all__ = getattr(source, "__all__", [])
    sys.modules[module_name] = alias
