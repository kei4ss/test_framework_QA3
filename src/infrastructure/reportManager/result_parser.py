"""
result_parser.py
----------------
Responsável por ler e interpretar os resultados produzidos pelo pytest
(via --json-report ou saída padrão capturada) e organizar as informações
por categoria: unit, integration e e2e.

Fontes de dados suportadas:
  1. Arquivo JSON gerado por pytest-json-report  (primária)
  2. Arquivo .txt com saída capturada do pytest    (fallback)
  3. Dicionário já estruturado passado diretamente  (API programática)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------

@dataclass
class TestCategoryResult:
    """Resultado consolidado para uma categoria de testes."""

    category: str          # "unit" | "integration" | "e2e"
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    duration: float = 0.0  # segundos
    failed_tests: List[str] = field(default_factory=list)

    @property
    def failure_rate(self) -> float:
        """Percentual de falhas sobre o total executado."""
        if self.total == 0:
            return 0.0
        return (self.failed + self.errors) / self.total * 100


@dataclass
class ParsedResults:
    """Resultado completo da suíte, dividido por categoria."""

    unit: TestCategoryResult = field(
        default_factory=lambda: TestCategoryResult(category="unit")
    )
    integration: TestCategoryResult = field(
        default_factory=lambda: TestCategoryResult(category="integration")
    )
    e2e: TestCategoryResult = field(
        default_factory=lambda: TestCategoryResult(category="e2e")
    )
    total_duration: float = 0.0

    @property
    def categories(self) -> List[TestCategoryResult]:
        return [self.unit, self.integration, self.e2e]


# ---------------------------------------------------------------------------
# Mapeamento de caminho → categoria
# ---------------------------------------------------------------------------

_CATEGORY_PATTERNS: Dict[str, str] = {
    "unit":        r"tests[/\\]unit[/\\]",
    "integration": r"tests[/\\]integration[/\\]",
    "e2e":         r"tests[/\\]e2e[/\\]",
}


def _resolve_category(node_id: str) -> Optional[str]:
    """Retorna a categoria de um teste com base no seu node_id do pytest."""
    for category, pattern in _CATEGORY_PATTERNS.items():
        if re.search(pattern, node_id, re.IGNORECASE):
            return category
    return None


# ---------------------------------------------------------------------------
# Parser principal
# ---------------------------------------------------------------------------

class ResultParser:
    """
    Analisa os resultados dos testes e retorna um ``ParsedResults``.

    Uso típico:
        parser = ResultParser()
        results = parser.parse_json("reports/.report.json")
    """

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def parse_json(self, json_path: str | Path) -> ParsedResults:
        """
        Lê o arquivo JSON gerado por pytest-json-report e extrai os dados.

        O arquivo é produzido ao rodar:
            pytest --json-report --json-report-file=<json_path>
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de resultados JSON não encontrado: {path}\n"
                "Execute pytest com a opção --json-report primeiro."
            )

        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)

        return self._parse_json_data(data)

    def parse_dict(self, data: dict) -> ParsedResults:
        """Aceita um dicionário já carregado (útil para testes unitários)."""
        return self._parse_json_data(data)

    def parse_text(self, text_path: str | Path) -> ParsedResults:
        """
        Fallback: lê a saída textual do pytest capturada em arquivo.
        Extrai apenas totais globais (sem separação por categoria).
        """
        path = Path(text_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo de saída textual não encontrado: {path}"
            )
        content = path.read_text(encoding="utf-8", errors="replace")
        return self._parse_text_output(content)

    # ------------------------------------------------------------------
    # Lógica interna – JSON
    # ------------------------------------------------------------------

    def _parse_json_data(self, data: dict) -> ParsedResults:
        results = ParsedResults()
        results.total_duration = float(data.get("duration", 0.0))

        tests: list = data.get("tests", [])
        for test in tests:
            node_id: str = test.get("nodeid", "")
            outcome: str = test.get("outcome", "unknown").lower()
            duration: float = float(
                test.get("call", {}).get("duration", 0.0)
                if isinstance(test.get("call"), dict)
                else 0.0
            )

            category = _resolve_category(node_id)
            if category is None:
                # Testes fora das pastas conhecidas são ignorados silenciosamente
                continue

            bucket: TestCategoryResult = getattr(results, category)
            bucket.total += 1
            bucket.duration += duration

            if outcome == "passed":
                bucket.passed += 1
            elif outcome == "failed":
                bucket.failed += 1
                bucket.failed_tests.append(node_id)
            elif outcome in ("error", "xfail", "xpass"):
                bucket.errors += 1
                if outcome == "error":
                    bucket.failed_tests.append(node_id)

        return results

    # ------------------------------------------------------------------
    # Lógica interna – texto
    # ------------------------------------------------------------------

    _SUMMARY_RE = re.compile(
        r"(?:(\d+) failed)?[,\s]*"
        r"(?:(\d+) passed)?[,\s]*"
        r"(?:(\d+) error(?:s)?)?[,\s]*"
        r"in\s+([\d.]+)s",
        re.IGNORECASE,
    )

    def _parse_text_output(self, content: str) -> ParsedResults:
        """
        Extrai totais da linha de resumo do pytest, ex.:
          '5 failed, 42 passed in 3.21s'
        Como não há separação por categoria no texto puro, todos os
        resultados são atribuídos à categoria 'unit' como fallback.
        """
        results = ParsedResults()

        match = self._SUMMARY_RE.search(content)
        if not match:
            return results

        failed = int(match.group(1) or 0)
        passed = int(match.group(2) or 0)
        errors = int(match.group(3) or 0)
        duration = float(match.group(4) or 0.0)

        # Sem informação de categoria no texto plano: atribui tudo a 'unit'
        bucket = results.unit
        bucket.failed = failed
        bucket.passed = passed
        bucket.errors = errors
        bucket.total = failed + passed + errors
        bucket.duration = duration
        results.total_duration = duration

        return results
