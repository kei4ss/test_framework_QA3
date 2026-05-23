"""
Configurações do Data Provider
Define as fontes de dados e validações para o framework de testes
"""
from enum import Enum
import os

class DataSourceType(Enum):
    """Tipos de fonte de dados suportadas"""
    JSON = "json"
    CSV = "csv"
    HARDCODED = "hardcoded"


class DataProviderConfig:
    """Configuração centralizada do Data Provider com padrão Singleton"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Caminho raiz do projeto
        self.root_path = os.path.join(os.path.dirname(__file__), '../../')
        self.data_path = os.path.join(self.root_path, 'data', 'test_data')
        
        # Configurações de fonte preferencial
        self.default_source = DataSourceType.JSON
        
        # Configurações de caminhos para arquivos
        self.json_path = self.data_path
        self.csv_path = self.data_path
        
        # Configurações de validação
        self.validate_data = True
        self.strict_mode = False  # Se True, falha em dados inválidos; se False, tenta recuperar
        
        # Configurações de geração de dados
        self.max_records = 100
        self.enable_fallback = True  # Tenta fonte alternativa se a preferencial falhar
        
        self._initialized = True
    
    def get_config(self):
        """Retorna a configuração como dicionário"""
        return {
            'data_path': self.data_path,
            'json_path': self.json_path,
            'csv_path': self.csv_path,
            'default_source': self.default_source,
            'validate_data': self.validate_data,
            'strict_mode': self.strict_mode,
            'max_records': self.max_records,
            'enable_fallback': self.enable_fallback
        }
    
    def set_default_source(self, source_type: DataSourceType):
        """Define a fonte preferencial de dados"""
        if isinstance(source_type, DataSourceType):
            self.default_source = source_type
        else:
            raise ValueError(f"Tipo de fonte inválido: {source_type}")
    
    def set_json_path(self, path: str):
        """Define o caminho para arquivos JSON"""
        self.json_path = path
    
    def set_csv_path(self, path: str):
        """Define o caminho para arquivos CSV"""
        self.csv_path = path
