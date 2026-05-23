"""
Data Provider Module - Sistema unificado de fornecimento de dados para testes
Implementa o padrão Strategy para flexibilidade na escolha da fonte de dados
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
import os

from src.utils.file_reader import FileReader
from src.utils.data_validator import DataValidator
from src.config.data_provider_config import DataProviderConfig, DataSourceType


class DataStrategy(ABC):
    """
    Classe abstrata que define a interface para estratégias de obtenção de dados
    Implementa o padrão Strategy Pattern
    """
    
    @abstractmethod
    def get_data(self, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Obtém dados de acordo com a estratégia implementada
        
        Args:
            identifier (str): Identificador do arquivo/dados a obter
            
        Returns:
            List[Dict]: Lista de dicionários com os dados
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se a estratégia está disponível"""
        pass


class JSONDataStrategy(DataStrategy):
    """Estratégia para obter dados de arquivos JSON"""
    
    def __init__(self, json_path: str):
        """
        Args:
            json_path (str): Caminho para os arquivos JSON
        """
        self.json_path = json_path
        self.file_reader = FileReader()
    
    def get_data(self, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Lê dados de um arquivo JSON
        
        Args:
            identifier (str): Nome do arquivo (ex: 'users.json' ou 'users')
            
        Returns:
            List[Dict]: Dados lidos do arquivo JSON
        """
        if identifier is None:
            raise ValueError("Identificador (nome do arquivo) é obrigatório para JSON")
        
        # Remove extensão se fornecida
        if identifier.endswith('.json'):
            identifier = identifier[:-5]
        
        file_path = os.path.join(self.json_path, f"{identifier}.json")
        data = self.file_reader.read_json(file_path)
        
        # Se for um dicionário, converte para lista
        if isinstance(data, dict):
            data = [data]
        
        return data
    
    def is_available(self) -> bool:
        """Verifica se o caminho de JSON está disponível"""
        return os.path.exists(self.json_path)


class CSVDataStrategy(DataStrategy):
    """Estratégia para obter dados de arquivos CSV"""
    
    def __init__(self, csv_path: str):
        """
        Args:
            csv_path (str): Caminho para os arquivos CSV
        """
        self.csv_path = csv_path
        self.file_reader = FileReader()
    
    def get_data(self, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Lê dados de um arquivo CSV
        
        Args:
            identifier (str): Nome do arquivo (ex: 'users.csv' ou 'users')
            
        Returns:
            List[Dict]: Dados lidos do arquivo CSV
        """
        if identifier is None:
            raise ValueError("Identificador (nome do arquivo) é obrigatório para CSV")
        
        # Remove extensão se fornecida
        if identifier.endswith('.csv'):
            identifier = identifier[:-4]
        
        file_path = os.path.join(self.csv_path, f"{identifier}.csv")
        return self.file_reader.read_csv(file_path)
    
    def is_available(self) -> bool:
        """Verifica se o caminho de CSV está disponível"""
        return os.path.exists(self.csv_path)


class HardcodedDataStrategy(DataStrategy):
    """Estratégia para dados definidos em código"""
    
    def __init__(self):
        """Inicializa com dados pré-definidos"""
        self.hardcoded_data = {
            'default_user': [
                {
                    'id': 999,
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'password': 'testPassword123',
                    'age': 30,
                    'role': 'user',
                    'active': True
                }
            ],
            'admin_user': [
                {
                    'id': 998,
                    'name': 'Admin User',
                    'email': 'admin@example.com',
                    'password': 'adminPassword123',
                    'age': 35,
                    'role': 'admin',
                    'active': True
                }
            ],
            'inactive_user': [
                {
                    'id': 997,
                    'name': 'Inactive User',
                    'email': 'inactive@example.com',
                    'password': 'inactivePassword123',
                    'age': 25,
                    'role': 'user',
                    'active': False
                }
            ]
        }
    
    def get_data(self, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Retorna dados pré-definidos
        
        Args:
            identifier (str): Chave dos dados (ex: 'default_user')
            
        Returns:
            List[Dict]: Dados pré-definidos
        """
        if identifier is None:
            identifier = 'default_user'
        
        if identifier not in self.hardcoded_data:
            raise ValueError(f"Dados hardcoded não encontrados: {identifier}")
        
        return self.hardcoded_data[identifier]
    
    def is_available(self) -> bool:
        """Sempre disponível"""
        return True


class DataProvider:
    """
    Fornecedor de dados centralizado com suporte a múltiplas estratégias
    Implementa padrões Singleton e Strategy
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o Data Provider com as estratégias padrão"""
        if self._initialized:
            return
        
        self.config = DataProviderConfig()
        self.validator = DataValidator()
        self.strategies: Dict[DataSourceType, DataStrategy] = {}
        
        # Registra estratégias disponíveis
        self.strategies[DataSourceType.JSON] = JSONDataStrategy(self.config.json_path)
        self.strategies[DataSourceType.CSV] = CSVDataStrategy(self.config.csv_path)
        self.strategies[DataSourceType.HARDCODED] = HardcodedDataStrategy()
        
        self._initialized = True
    
    def get_user_data(self, source: DataSourceType = None, identifier: str = 'users') -> List[Dict[str, Any]]:
        """
        Obtém dados de usuários
        
        Args:
            source (DataSourceType): Fonte de dados preferencial (usa padrão se None)
            identifier (str): Identificador do dados (nome do arquivo ou chave)
            
        Returns:
            List[Dict]: Lista de dados de usuários
        """
        return self._get_data(source, identifier)
    
    def get_product_data(self, source: DataSourceType = None, identifier: str = 'products') -> List[Dict[str, Any]]:
        """
        Obtém dados de produtos
        
        Args:
            source (DataSourceType): Fonte de dados preferencial
            identifier (str): Identificador do dados
            
        Returns:
            List[Dict]: Lista de dados de produtos
        """
        return self._get_data(source, identifier)
    
    def get_data(self, source: DataSourceType = None, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Método genérico para obter dados de qualquer fonte
        
        Args:
            source (DataSourceType): Fonte de dados preferencial
            identifier (str): Identificador único dos dados
            
        Returns:
            List[Dict]: Lista de dicionários com os dados
        """
        return self._get_data(source, identifier)
    
    def _get_data(self, source: DataSourceType = None, identifier: str = None) -> List[Dict[str, Any]]:
        """
        Implementação interna de obtenção de dados com fallback
        
        Args:
            source (DataSourceType): Fonte preferencial
            identifier (str): Identificador do dados
            
        Returns:
            List[Dict]: Lista de dados
            
        Raises:
            ValueError: Se nenhuma estratégia conseguir fornecer os dados
        """
        if identifier is None:
            raise ValueError("Identificador dos dados é obrigatório")
        
        # Define qual estratégia tentar primeiro
        source_to_use = source or self.config.default_source
        
        # Tenta obter dados da estratégia preferencial
        try:
            strategy = self.strategies[source_to_use]
            if strategy.is_available():
                data = strategy.get_data(identifier)
                
                # Valida os dados se configurado
                if self.config.validate_data:
                    self._validate_data(data)
                
                return data
        except Exception as e:
            if self.config.strict_mode:
                raise
            # Se em modo não-strict e fallback está habilitado, tenta outras estratégias
            if not self.config.enable_fallback:
                raise
        
        # Fallback para outras estratégias se habilitado
        if self.config.enable_fallback:
            for strategy_type, strategy in self.strategies.items():
                if strategy_type == source_to_use:
                    continue  # Já tentou
                
                try:
                    if strategy.is_available():
                        data = strategy.get_data(identifier)
                        
                        if self.config.validate_data:
                            self._validate_data(data)
                        
                        return data
                except:
                    continue
        
        # Se chegou aqui, não conseguiu obter dados de nenhuma estratégia
        raise ValueError(
            f"Não foi possível obter dados com identificador '{identifier}' "
            f"da fonte '{source_to_use.value}' ou alternativas"
        )
    
    def _validate_data(self, data: List[Dict[str, Any]]):
        """
        Valida dados antes de retornar
        
        Args:
            data (List[Dict]): Dados a validar
        """
        if not data:
            return
        
        if self.config.strict_mode:
            # Em modo strict, falha em qualquer erro
            for item in data:
                is_valid, errors = self.validator.validate(item, strict=True)
                if not is_valid:
                    raise ValueError(f"Dados inválidos: {errors}")
    
    def set_default_source(self, source: DataSourceType):
        """
        Define a fonte de dados preferencial
        
        Args:
            source (DataSourceType): Tipo de fonte
        """
        self.config.set_default_source(source)
    
    def register_custom_strategy(self, source_type: str, strategy: DataStrategy):
        """
        Registra uma estratégia customizada
        
        Args:
            source_type (str): Nome único para a estratégia
            strategy (DataStrategy): Instância da estratégia
        """
        self.strategies[source_type] = strategy
    
    def list_available_data_files(self, source: DataSourceType = None) -> List[str]:
        """
        Lista arquivos de dados disponíveis
        
        Args:
            source (DataSourceType): Tipo de fonte (padrão se None)
            
        Returns:
            List[str]: Lista de nomes de arquivos
        """
        source_to_check = source or self.config.default_source
        
        if source_to_check == DataSourceType.JSON:
            return FileReader.list_files_in_directory(self.config.json_path, '.json')
        elif source_to_check == DataSourceType.CSV:
            return FileReader.list_files_in_directory(self.config.csv_path, '.csv')
        elif source_to_check == DataSourceType.HARDCODED:
            strategy = self.strategies[DataSourceType.HARDCODED]
            if isinstance(strategy, HardcodedDataStrategy):
                return list(strategy.hardcoded_data.keys())
        
        return []
    
    def validate_file_schema(self, file_path: str, schema: Dict[str, Type]) -> tuple[bool, List[str]]:
        """
        Valida se um arquivo de dados segue um schema específico
        
        Args:
            file_path (str): Caminho do arquivo
            schema (Dict[str, Type]): Schema esperado (nome_campo: tipo)
            
        Returns:
            tuple: (é_válido, lista_de_erros)
        """
        try:
            if file_path.endswith('.json'):
                data = FileReader.read_json(file_path)
            elif file_path.endswith('.csv'):
                data = FileReader.read_csv(file_path)
            else:
                return False, ["Tipo de arquivo não suportado"]
            
            if isinstance(data, dict):
                data = [data]
            
            errors = []
            for item in data:
                for field, expected_type in schema.items():
                    if field not in item:
                        errors.append(f"Campo ausente: {field}")
                    elif not isinstance(item[field], expected_type):
                        errors.append(
                            f"Campo '{field}' tem tipo {type(item[field]).__name__}, "
                            f"esperado {expected_type.__name__}"
                        )
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [str(e)]
