"""
Atlassian Document Format (ADF) to Plain Text Converter
Converts Jira's rich text ADF JSON format into readable plain text.
"""

from __future__ import annotations
from typing import Any, List

def adf_to_text(adf: Any) -> str:
    """
    Convert Atlassian Document Format (ADF) JSON into plain text.
    
    ADF is Jira's rich text format (used for descriptions, comments, etc).
    This function recursively walks the ADF tree and extracts plain text,
    preserving paragraph and line breaks.
    
    Args:
        adf: ADF JSON object or None
    
    Returns:
        str: Plain text with normalized whitespace and line breaks
    
    Example:
        Input ADF: {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]}
        Output: "Hello"
    """
    if not adf:
        return ""

    chunks: List[str] = []

    def walk(node: Any) -> None:
        """Recursively traverse ADF tree and extract text."""
        if node is None:
            return

        if isinstance(node, dict):
            ntype = node.get("type")

            # Text node - WHY: Contains actual text content
            if ntype == "text":
                text = node.get("text", "")
                if text:
                    chunks.append(text)
                return

            # Hard break - WHY: Represents line breaks in formatted text
            if ntype == "hardBreak":
                chunks.append("\n")
                return

            # Traverse children - WHY: Most ADF nodes are containers with content
            content = node.get("content")
            if isinstance(content, list):
                # Add paragraph separation - WHY: These block elements should be on separate lines
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
