"""
report_manager.py
-----------------
Orquestrador principal do módulo reportManager.

Responsabilidades:
  1. Localizar / receber os resultados dos testes (JSON ou texto).
  2. Delegar a análise ao ResultParser.
  3. Delegar a geração do PDF ao PDFBuilder.
  4. Garantir que o arquivo seja salvo em ./reports/ com o nome correto.
  5. Nunca sobrescrever relatórios anteriores.

Uso como script standalone:
    python -m src.infrastructure.reportManager.report_manager \
        --results .report.json

Uso programático (ex.: conftest.py):
    from src.infrastructure.reportManager import ReportManager
    rm = ReportManager()
    rm.generate(results_path=".report.json")
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .pdf_builder import PDFBuilder
from .result_parser import ParsedResults, ResultParser


class ReportManager:
    """
    Gera relatórios PDF a partir dos resultados da suíte de testes.

    Parâmetros
    ----------
    reports_dir : str | Path, opcional
        Diretório onde os relatórios serão salvos.
        Padrão: ``<raiz_do_projeto>/reports``
    """

    def __init__(self, reports_dir: str | Path | None = None) -> None:
        if reports_dir is None:
            # Sobe três níveis a partir de reportManager/ → raiz do projeto
            reports_dir = Path(__file__).resolve().parents[3] / "reports"
        self._reports_dir = Path(reports_dir)
        self._parser = ResultParser()
        self._builder = PDFBuilder()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generate(
        self,
        results_path: str | Path | None = None,
        results_dict: dict | None = None,
        parsed_results: ParsedResults | None = None,
    ) -> Path:
        """
        Gera o relatório PDF e retorna o caminho do arquivo criado.

        Formas de fornecer os resultados (em ordem de prioridade):
          1. ``parsed_results`` — ``ParsedResults`` já construído externamente.
          2. ``results_dict``   — dicionário no formato pytest-json-report.
          3. ``results_path``   — caminho para arquivo .json ou .txt.

        Raises
        ------
        ValueError
            Se nenhuma fonte de resultados for fornecida.
        FileNotFoundError
            Se o caminho informado não existir.
        """
        results = self._resolve_results(results_path, results_dict, parsed_results)
        output_path = self._build_output_path()
        self._builder.build(results, output_path)
        return output_path

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _resolve_results(
        self,
        results_path: Optional[str | Path],
        results_dict: Optional[dict],
        parsed_results: Optional[ParsedResults],
    ) -> ParsedResults:
        if parsed_results is not None:
            return parsed_results

        if results_dict is not None:
            return self._parser.parse_dict(results_dict)

        if results_path is not None:
            path = Path(results_path)
            if path.suffix.lower() == ".json":
                return self._parser.parse_json(path)
            else:
                return self._parser.parse_text(path)

        raise ValueError(
            "Nenhuma fonte de resultados fornecida ao ReportManager.\n"
            "Use results_path, results_dict ou parsed_results."
        )

    def _build_output_path(self) -> Path:
        """
        Gera o nome do arquivo seguindo o padrão HH-mm-ss-DD-MM-YYYY.pdf.
        Garante unicidade adicionando sufixo _N se o arquivo já existir.
        """
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now()
        base_name = now.strftime("%H-%M-%S-%d-%m-%Y")
        output_path = self._reports_dir / f"{base_name}.pdf"

        # Evita sobrescrever relatórios existentes (ex.: execuções no mesmo segundo)
        counter = 1
        while output_path.exists():
            output_path = self._reports_dir / f"{base_name}_{counter}.pdf"
            counter += 1

        return output_path


# ---------------------------------------------------------------------------
# Ponto de entrada via linha de comando
# ---------------------------------------------------------------------------

def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="Gera relatório PDF a partir dos resultados do pytest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemplos:\n"
            "  python -m src.infrastructure.reportManager.report_manager "
            "--results .report.json\n"
            "  python -m src.infrastructure.reportManager.report_manager "
            "--results output.txt --reports-dir custom_reports/"
        ),
    )
    parser.add_argument(
        "--results",
        metavar="FILE",
        required=True,
        help="Caminho para o arquivo de resultados (.json ou .txt)",
    )
    parser.add_argument(
        "--reports-dir",
        metavar="DIR",
        default=None,
        help="Diretório de saída dos relatórios (padrão: ./reports)",
    )
    args = parser.parse_args()

    rm = ReportManager(reports_dir=args.reports_dir)
    try:
        output = rm.generate(results_path=args.results)
        print(f"[ReportManager] Relatório gerado: {output}")
        sys.exit(0)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ReportManager] ERRO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
