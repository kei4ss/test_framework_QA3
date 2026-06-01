"""
Utils Package - Utilitários gerais do framework
Inclui: Data Provider, File Reader, Data Validator
"""

from src.utils.file_reader import FileReader
from src.utils.data_validator import DataValidator
from src.utils.data_provider import (
    DataProvider,
    DataStrategy,
    JSONDataStrategy,
    CSVDataStrategy,
    HardcodedDataStrategy
)

__all__ = [
    'FileReader',
    'DataValidator',
    'DataProvider',
    'DataStrategy',
    'JSONDataStrategy',
    'CSVDataStrategy',
    'HardcodedDataStrategy'
]
