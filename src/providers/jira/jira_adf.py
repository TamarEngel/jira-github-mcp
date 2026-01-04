# src/providers/jira_adf.py
from __future__ import annotations
from typing import Any, List

def adf_to_text(adf: Any) -> str:
    """
    Convert Atlassian Document Format (ADF) JSON into plain text.
    Best-effort: extracts text nodes, keeps line breaks between paragraphs.
    """
    if not adf:
        return ""

    chunks: List[str] = []

    def walk(node: Any) -> None:
        if node is None:
            return

        if isinstance(node, dict):
            ntype = node.get("type")

            # Text node
            if ntype == "text":
                text = node.get("text", "")
                if text:
                    chunks.append(text)
                return

            # Hard break
            if ntype == "hardBreak":
                chunks.append("\n")
                return

            # Traverse children
            content = node.get("content")
            if isinstance(content, list):
                # Add paragraph separation
                if ntype in ("paragraph", "heading", "listItem"):
                    before_len = len(chunks)
                    for child in content:
                        walk(child)
                    # add newline if something was added in this block
                    if len(chunks) > before_len:
                        chunks.append("\n")
                else:
                    for child in content:
                        walk(child)
            return

        if isinstance(node, list):
            for item in node:
                walk(item)

    walk(adf)

    # Clean up
    text = "".join(chunks)
    # normalize excessive newlines
    lines = [ln.rstrip() for ln in text.splitlines()]
    # remove empty trailing lines
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines).strip()
