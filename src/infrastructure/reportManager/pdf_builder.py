"""
pdf_builder.py
--------------
Constrói o arquivo PDF do relatório de execução de testes usando reportlab.

Recebe um ``ParsedResults`` e escreve o PDF no caminho informado.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .result_parser import ParsedResults, TestCategoryResult


# ---------------------------------------------------------------------------
# Paleta de cores
# ---------------------------------------------------------------------------

_GREEN = colors.HexColor("#27ae60")
_RED = colors.HexColor("#e74c3c")
_ORANGE = colors.HexColor("#e67e22")
_DARK = colors.HexColor("#2c3e50")
_LIGHT_GRAY = colors.HexColor("#ecf0f1")
_MID_GRAY = colors.HexColor("#bdc3c7")
_WHITE = colors.white

_CATEGORY_LABELS = {
    "unit": "UNIT TESTS",
    "integration": "INTEGRATION TESTS",
    "e2e": "E2E TESTS",
}


class PDFBuilder:
    """
    Constrói o PDF de relatório a partir de um ``ParsedResults``.

    Uso:
        builder = PDFBuilder()
        builder.build(results, output_path="reports/14-32-10-28-05-2026.pdf")
    """

    def __init__(self) -> None:
        self._styles = getSampleStyleSheet()
        self._custom_styles = self._build_styles()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def build(self, results: ParsedResults, output_path: str | Path) -> Path:
        """
        Gera o PDF e salva em ``output_path``.

        Retorna o ``Path`` do arquivo criado.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = self._build_story(results)
        doc.build(story)
        return output_path

    # ------------------------------------------------------------------
    # Estilos
    # ------------------------------------------------------------------

    def _build_styles(self) -> dict:
        return {
            "title": ParagraphStyle(
                "ReportTitle",
                parent=self._styles["Title"],
                fontSize=22,
                textColor=_DARK,
                spaceAfter=6,
                fontName="Helvetica-Bold",
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=self._styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#7f8c8d"),
                spaceAfter=4,
            ),
            "section_header": ParagraphStyle(
                "SectionHeader",
                parent=self._styles["Heading2"],
                fontSize=13,
                textColor=_WHITE,
                fontName="Helvetica-Bold",
                spaceBefore=14,
                spaceAfter=6,
                backColor=_DARK,
                leftIndent=-12,
                rightIndent=-12,
                leading=20,
            ),
            "label": ParagraphStyle(
                "Label",
                parent=self._styles["Normal"],
                fontSize=10,
                textColor=_DARK,
                fontName="Helvetica",
            ),
            "footer": ParagraphStyle(
                "Footer",
                parent=self._styles["Normal"],
                fontSize=8,
                textColor=_MID_GRAY,
                alignment=1,
            ),
        }

    # ------------------------------------------------------------------
    # Construção do story
    # ------------------------------------------------------------------

    def _build_story(self, results: ParsedResults) -> list:
        story: list = []

        # ---- Cabeçalho ----
        story.append(Paragraph("Relatório de Execução de Testes", self._custom_styles["title"]))
        now = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
        story.append(Paragraph(f"Data: {now}", self._custom_styles["subtitle"]))
        story.append(HRFlowable(width="100%", thickness=2, color=_DARK, spaceAfter=10))

        # ---- Resumo geral ----
        story += self._build_summary_table(results)
        story.append(Spacer(1, 14))

        # ---- Seção por categoria ----
        for cat in results.categories:
            story += self._build_category_section(cat)

        # ---- Rodapé ----
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=_MID_GRAY))
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                "Relatório gerado automaticamente pelo ReportManager · test_framework_QA3",
                self._custom_styles["footer"],
            )
        )

        return story

    # ------------------------------------------------------------------
    # Tabela de resumo geral
    # ------------------------------------------------------------------

    def _build_summary_table(self, results: ParsedResults) -> list:
        total_tests = sum(c.total for c in results.categories)
        total_passed = sum(c.passed for c in results.categories)
        total_failed = sum(c.failed + c.errors for c in results.categories)
        failure_rate = (total_failed / total_tests * 100) if total_tests > 0 else 0.0
        total_duration = results.total_duration

        data = [
            ["Total de Testes", "Aprovados", "Falhas", "Taxa de Falha", "Duração"],
            [
                str(total_tests),
                str(total_passed),
                str(total_failed),
                f"{failure_rate:.2f}%",
                f"{total_duration:.2f}s" if total_duration > 0 else "—",
            ],
        ]

        col_widths = [3.2 * cm, 3.2 * cm, 3.0 * cm, 3.5 * cm, 3.5 * cm]

        table = Table(data, colWidths=col_widths, hAlign="LEFT")
        table.setStyle(
            TableStyle([
                # Cabeçalho
                ("BACKGROUND", (0, 0), (-1, 0), _DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_LIGHT_GRAY, _WHITE]),
                ("FONTSIZE", (0, 1), (-1, -1), 11),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica-Bold"),
                # Colorir célula de falhas
                ("TEXTCOLOR", (2, 1), (2, 1), _RED if total_failed > 0 else _GREEN),
                ("TEXTCOLOR", (3, 1), (3, 1), _RED if failure_rate > 0 else _GREEN),
                ("TEXTCOLOR", (1, 1), (1, 1), _GREEN),
                ("BOX", (0, 0), (-1, -1), 1, _MID_GRAY),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, _MID_GRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        return [Paragraph("Resumo Geral", self._custom_styles["subtitle"]), Spacer(1, 4), table]

    # ------------------------------------------------------------------
    # Seção de categoria
    # ------------------------------------------------------------------

    def _build_category_section(self, cat: TestCategoryResult) -> list:
        story: list = []

        label = _CATEGORY_LABELS.get(cat.category, cat.category.upper())
        failure_color = _RED if (cat.failed + cat.errors) > 0 else _GREEN
        failure_rate_str = f"{cat.failure_rate:.2f}%"

        # Cabeçalho da seção
        story.append(Paragraph(f"  {label}", self._custom_styles["section_header"]))

        # Tabela de métricas
        rows = [
            ["Métrica", "Valor"],
            ["Total de testes", str(cat.total)],
            ["Testes aprovados", str(cat.passed)],
            ["Testes falhos", str(cat.failed + cat.errors)],
            ["Taxa de falha", failure_rate_str],
        ]
        if cat.duration > 0:
            rows.append(["Duração da execução", f"{cat.duration:.3f}s"])

        col_widths = [8 * cm, 8 * cm]
        table = Table(rows, colWidths=col_widths, hAlign="LEFT")

        cell_styles = [
            # Cabeçalho
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), _WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_LIGHT_GRAY, _WHITE]),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 1, _MID_GRAY),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, _MID_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]

        # Colorir linha de falhas e taxa
        failed_row_idx = 3   # "Testes falhos"
        rate_row_idx = 4     # "Taxa de falha"
        passed_row_idx = 2   # "Testes aprovados"

        cell_styles += [
            ("TEXTCOLOR", (1, failed_row_idx), (1, failed_row_idx), failure_color),
            ("FONTNAME", (1, failed_row_idx), (1, failed_row_idx), "Helvetica-Bold"),
            ("TEXTCOLOR", (1, rate_row_idx), (1, rate_row_idx), failure_color),
            ("FONTNAME", (1, rate_row_idx), (1, rate_row_idx), "Helvetica-Bold"),
            ("TEXTCOLOR", (1, passed_row_idx), (1, passed_row_idx), _GREEN),
            ("FONTNAME", (1, passed_row_idx), (1, passed_row_idx), "Helvetica-Bold"),
        ]

        table.setStyle(TableStyle(cell_styles))
        story.append(table)

        # Lista de testes falhos (se houver)
        if cat.failed_tests:
            story.append(Spacer(1, 6))
            story.append(
                Paragraph(
                    "<b>Testes com falha:</b>",
                    self._custom_styles["label"],
                )
            )
            for test_id in cat.failed_tests:
                story.append(
                    Paragraph(
                        f"  • <font color='#e74c3c'>{test_id}</font>",
                        self._custom_styles["label"],
                    )
                )

        story.append(Spacer(1, 8))
        return story
