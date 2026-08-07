"""Convert paper/HUMAN-AI_draft_tr.md to PDF.

Usage:
    python experiments/export_thesis_pdf.py
    python experiments/export_thesis_pdf.py --output paper/HUMAN-AI_draft_tr.pdf
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MD = ROOT / "paper" / "HUMAN-AI_draft_tr.md"
DEFAULT_PDF = ROOT / "paper" / "HUMAN-AI_draft_tr.pdf"

# Windows Arial supports Turkish; fallback paths
FONT_CANDIDATES = [
    (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
    (Path(r"C:\Windows\Fonts\segoeui.ttf"), Path(r"C:\Windows\Fonts\segoeuib.ttf")),
    (Path(r"C:\Windows\Fonts\calibri.ttf"), Path(r"C:\Windows\Fonts\calibrib.ttf")),
]


def find_fonts() -> tuple[Path, Path]:
    for regular, bold in FONT_CANDIDATES:
        if regular.exists():
            bold_path = bold if bold.exists() else regular
            return regular, bold_path
    raise FileNotFoundError("No Unicode TTF font found under C:\\Windows\\Fonts")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text.strip()


def parse_blocks(lines: list[str]) -> list[tuple[str, str | list[list[str]]]]:
    """Return list of (kind, content). kind: title, h2, h3, p, hr, code, table."""
    blocks: list[tuple[str, str | list[list[str]]]] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.startswith("# "):
            blocks.append(("title", strip_md_inline(line[2:])))
            i += 1
            continue

        if line.startswith("## "):
            blocks.append(("h2", strip_md_inline(line[3:])))
            i += 1
            continue

        if line.startswith("### "):
            blocks.append(("h3", strip_md_inline(line[4:])))
            i += 1
            continue

        if line.strip() == "---":
            blocks.append(("hr", ""))
            i += 1
            continue

        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].rstrip())
                i += 1
            blocks.append(("code", "\n".join(code_lines)))
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and re.match(r"^\|[-:\s|]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and "|" in lines[i]:
                if re.match(r"^\|[-:\s|]+\|$", lines[i].strip()):
                    i += 1
                    continue
                cells = [strip_md_inline(c.strip()) for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            blocks.append(("table", rows))
            continue

        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#") and lines[i].strip() != "---":
            if lines[i].strip().startswith("```") or ("|" in lines[i] and i + 1 < len(lines) and "|" in lines[i + 1]):
                break
            para.append(lines[i].rstrip())
            i += 1
        blocks.append(("p", " ".join(strip_md_inline(x) for x in para)))

    return blocks


class ThesisPDF:
    def __init__(self, font_regular: Path, font_bold: Path):
        from fpdf import FPDF

        self.pdf = FPDF(format="A4", unit="mm")
        self.pdf.set_margins(left=20, top=20, right=20)
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self.pdf.add_page()
        self.pdf.add_font("Body", "", str(font_regular))
        self.pdf.add_font("Body", "B", str(font_bold))
        self.pdf.set_font("Body", size=11)

    def _write(self, text: str, size: int = 11, style: str = "", lh: float = 6.0):
        self.pdf.set_font("Body", style=style, size=size)
        self.pdf.multi_cell(self.pdf.epw, lh, text)

    def render(self, blocks: list[tuple[str, str | list[list[str]]]]):
        for kind, content in blocks:
            if kind == "title":
                self.pdf.ln(4)
                self._write(str(content), size=16, style="B", lh=8)
                self.pdf.ln(2)
            elif kind == "h2":
                self.pdf.ln(5)
                self._write(str(content), size=13, style="B", lh=7)
                self.pdf.ln(1)
            elif kind == "h3":
                self.pdf.ln(3)
                self._write(str(content), size=11.5, style="B", lh=6.5)
            elif kind == "hr":
                self.pdf.ln(2)
                y = self.pdf.get_y()
                self.pdf.set_draw_color(180, 180, 180)
                self.pdf.line(self.pdf.l_margin, y, self.pdf.l_margin + self.pdf.epw, y)
                self.pdf.ln(4)
            elif kind == "code":
                self.pdf.set_fill_color(245, 245, 245)
                self._write(str(content), size=9, lh=5)
                self.pdf.ln(2)
            elif kind == "table":
                self._table(content)  # type: ignore[arg-type]
            elif kind == "p":
                self._write(str(content), size=11, lh=6)
                self.pdf.ln(1.5)

    def _table(self, rows: list[list[str]]):
        if not rows:
            return
        col_count = max(len(r) for r in rows)
        usable = self.pdf.epw
        col_w = usable / col_count
        self.pdf.set_font("Body", size=9)
        for ri, row in enumerate(rows):
            row = row + [""] * (col_count - len(row))
            x0 = self.pdf.l_margin
            y0 = self.pdf.get_y()
            max_h = 0
            for cell in row:
                lines = self.pdf.multi_cell(col_w, 5, cell, split_only=True)
                h = max(5, 5 * len(lines))
                max_h = max(max_h, h)
            if y0 + max_h > self.pdf.h - self.pdf.b_margin:
                self.pdf.add_page()
                y0 = self.pdf.get_y()
            for ci, cell in enumerate(row):
                x = x0 + ci * col_w
                self.pdf.set_xy(x, y0)
                if ri == 0:
                    self.pdf.set_fill_color(230, 230, 230)
                    self.pdf.rect(x, y0, col_w, max_h, style="DF")
                else:
                    self.pdf.rect(x, y0, col_w, max_h)
                self.pdf.set_xy(x + 1, y0 + 1)
                self.pdf.multi_cell(col_w - 2, 5, cell)
            self.pdf.set_xy(x0, y0 + max_h)

        self.pdf.ln(3)

    def save(self, path: Path):
        self.pdf.output(str(path))


def main():
    parser = argparse.ArgumentParser(description="Export Turkish thesis markdown to PDF")
    parser.add_argument("--input", type=Path, default=DEFAULT_MD)
    parser.add_argument("--output", type=Path, default=DEFAULT_PDF)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        from fpdf import FPDF  # noqa: F401
    except ImportError:
        print("Installing fpdf2...", file=sys.stderr)
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2", "-q"])

    font_regular, font_bold = find_fonts()
    text = args.input.read_text(encoding="utf-8")
    blocks = parse_blocks(text.splitlines())
    doc = ThesisPDF(font_regular, font_bold)
    doc.render(blocks)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.output)
    print(f"PDF saved: {args.output}")


if __name__ == "__main__":
    main()
