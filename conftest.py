from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

import pytest

from src.infrastructure.reportManager.result_parser import (
    ParsedResults,
    TestCategoryResult,
    _resolve_category,
)
from src.infrastructure.reportManager.report_manager import ReportManager


# ---------------------------------------------------------------------------
# Coleta de resultados durante a sessão
# ---------------------------------------------------------------------------

class _SessionCollector:
    """Acumula os resultados de cada teste durante a sessão pytest."""

    def __init__(self) -> None:
        self.start_time: float = time.time()
        self._buckets: Dict[str, TestCategoryResult] = {
            "unit":        TestCategoryResult(category="unit"),
            "integration": TestCategoryResult(category="integration"),
            "e2e":         TestCategoryResult(category="e2e"),
        }

    def record(self, report: pytest.TestReport) -> None:
        """Registra um relatório de fase 'call' (resultado do teste em si)."""
        category = _resolve_category(report.nodeid)
        if category is None:
            return

        bucket = self._buckets[category]

        if report.when == "call":
            bucket.total += 1
            duration = getattr(report, "duration", 0.0)
            bucket.duration += duration

            if report.passed:
                bucket.passed += 1
            elif report.failed:
                bucket.failed += 1
                bucket.failed_tests.append(report.nodeid)
        elif report.when == "setup" and report.failed:
            # Falha no setup é contabilizada como erro
            bucket.total += 1
            bucket.errors += 1
            bucket.failed_tests.append(report.nodeid)

    def build_results(self) -> ParsedResults:
        elapsed = time.time() - self.start_time
        results = ParsedResults(
            unit=self._buckets["unit"],
            integration=self._buckets["integration"],
            e2e=self._buckets["e2e"],
            total_duration=elapsed,
        )
        return results


# ---------------------------------------------------------------------------
# Hooks pytest
# ---------------------------------------------------------------------------

_collector: _SessionCollector | None = None


def pytest_sessionstart(session: pytest.Session) -> None:  
    global _collector
    _collector = _SessionCollector()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if _collector is not None:
        _collector.record(report)


def pytest_sessionfinish(
    session: pytest.Session,  
    exitstatus: int,          
) -> None:
    if _collector is None:
        return

    results = _collector.build_results()
    total = sum(c.total for c in results.categories)

    if total == 0:
        return

    try:
        rm = ReportManager()
        output_path = rm.generate(parsed_results=results)
        print(f"\n[ReportManager] Relatório PDF gerado: {output_path}")
    except Exception as exc:  # pragma: no cover
        print(f"\n[ReportManager] AVISO: falha ao gerar relatório PDF: {exc}")
