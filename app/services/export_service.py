from __future__ import annotations

import re
from dataclasses import dataclass

from fpdf import FPDF

from app.models.history import GeneratedPost
from app.schemas.templates import template_label
from app.services.generator import GenerationResult
from app.services.topic_service import platform_label

ALLOWED_FORMATS = ("txt", "md", "pdf")

MEDIA_TYPES = {
    "txt": "text/plain; charset=utf-8",
    "md": "text/markdown; charset=utf-8",
    "pdf": "application/pdf",
}

_EXTENSIONS = {
    "txt": "txt",
    "md": "md",
    "pdf": "pdf",
}


@dataclass(frozen=True, slots=True)
class ExportDocument:
    topic: str
    content: str
    platform_label: str
    template_label: str
    voice_name: str = ""


def document_from_generation(
    result: GenerationResult,
    *,
    voice_name: str = "",
) -> ExportDocument:
    return ExportDocument(
        topic=result.topic,
        content=result.content,
        platform_label=platform_label(result.platform),
        template_label=template_label(result.template),
        voice_name=voice_name,
    )


def document_from_history(post: GeneratedPost) -> ExportDocument:
    return ExportDocument(
        topic=post.topic,
        content=post.content,
        platform_label=post.platform_label,
        template_label=post.template_label,
        voice_name=post.voice_name,
    )


def download_filename(topic: str, fmt: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    slug = slug[:60] or "post"
    return f"{slug}.{_EXTENSIONS[fmt]}"


def render_export(document: ExportDocument, fmt: str) -> bytes:
    if fmt == "txt":
        return _render_txt(document)
    if fmt == "md":
        return _render_markdown(document)
    if fmt == "pdf":
        return _render_pdf(document)
    raise ValueError(f"Unsupported export format: {fmt}")


def _render_txt(document: ExportDocument) -> bytes:
    header = f"{document.topic}\n{document.platform_label} · {document.template_label}"
    if document.voice_name:
        header += f"\n{document.voice_name}"
    body = f"{header}\n\n{document.content.strip()}\n"
    return body.encode("utf-8")


def _render_markdown(document: ExportDocument) -> bytes:
    lines = [
        f"# {document.topic}",
        "",
        f"- Platform: {document.platform_label}",
        f"- Template: {document.template_label}",
    ]
    if document.voice_name:
        lines.append(f"- Voice: {document.voice_name}")
    lines.extend(["", document.content.strip(), ""])
    return "\n".join(lines).encode("utf-8")


def _render_pdf(document: ExportDocument) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_title(_pdf_text(document.topic)[:70])

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 8, _pdf_text(document.topic))
    pdf.ln(2)
    pdf.set_font("Helvetica", size=10)
    meta = f"{document.platform_label}  |  {document.template_label}"
    if document.voice_name:
        meta += f"  |  {document.voice_name}"
    pdf.multi_cell(0, 6, _pdf_text(meta))
    pdf.ln(4)
    pdf.set_draw_color(216, 204, 184)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, _pdf_text(document.content.strip()))
    return bytes(pdf.output())


def _pdf_text(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("latin-1", "replace").decode("latin-1")
