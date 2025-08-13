from __future__ import annotations

from typing import Any

try:
    from y_py import YDoc
except Exception:  # pragma: no cover
    YDoc = None  # type: ignore


def _collect_text(node: Any) -> str:
    txt = []
    if isinstance(node, dict):
        t = node.get("text")
        if isinstance(t, str):
            txt.append(t)
        for key in ("content", "children"):
            child = node.get(key)
            if isinstance(child, list):
                for c in child:
                    txt.append(_collect_text(c))
    elif isinstance(node, list):
        for c in node:
            txt.append(_collect_text(c))
    return " ".join([t for t in txt if t])


def decode_prosemirror_text_from_update(update: bytes) -> str:
    if YDoc is None:
        return ""
    try:
        with YDoc() as ydoc:
            with ydoc.begin_transaction() as txn:  # type: ignore
                ydoc.apply_update(update)
                frag = ydoc.get_xml_fragment("prosemirror")
                try:
                    data = frag.to_json(txn)  # type: ignore
                except Exception:
                    return ""
        return _collect_text(data)
    except Exception:
        return ""

