"""
Testes Unitários para o Data Provider.

Valida:
- Leitura de arquivos (JSON, CSV)
- Validação de dados
- Fallback entre fontes
- Padrão Singleton do DataProvider
"""

import pytest

from src.utils.file_reader import FileReader
from src.utils.data_validator import DataValidator
from src.utils.data_provider import (
    DataProvider, DataStrategy, JSONDataStrategy, 
    CSVDataStrategy, HardcodedDataStrategy
)
from src.config.data_provider_config import DataProviderConfig, DataSourceType


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestFileReader:
    """Testes para a classe FileReader."""
    
    def test_read_json_success(self):
        """Testa leitura bem-sucedida de arquivo JSON"""
        reader = FileReader()
        data = reader.read_json('data/test_data/users.json')
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert 'email' in data[0]
    
    def test_read_json_not_found(self):
        """Testa leitura de arquivo JSON inexistente"""
        reader = FileReader()
        
        with pytest.raises(FileNotFoundError):
            reader.read_json('data/test_data/inexistente.json')
    
    def test_read_csv_success(self):
        """Testa leitura bem-sucedida de arquivo CSV"""
        reader = FileReader()
        data = reader.read_csv('data/test_data/users.csv')
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'id' in data[0]
        assert 'name' in data[0]
    
    def test_read_csv_not_found(self):
        """Testa leitura de arquivo CSV inexistente"""
        reader = FileReader()
        
        with pytest.raises(FileNotFoundError):
            reader.read_csv('data/test_data/inexistente.csv')
    
    def test_convert_value_boolean(self):
        """Testa conversão de string para booleano"""
        assert FileReader._convert_value('true') is True
        assert FileReader._convert_value('false') is False
        assert FileReader._convert_value('True') is True
        assert FileReader._convert_value('False') is False
    
    def test_convert_value_integer(self):
        """Testa conversão de string para inteiro"""
        assert FileReader._convert_value('123') == 123
        assert isinstance(FileReader._convert_value('123'), int)
    
    def test_convert_value_float(self):
        """Testa conversão de string para float"""
        assert FileReader._convert_value('123.45') == 123.45
        assert isinstance(FileReader._convert_value('123.45'), float)
    
    def test_convert_value_string(self):
        """Testa que strings normais permanecem como strings"""
        assert FileReader._convert_value('hello') == 'hello'
        assert isinstance(FileReader._convert_value('hello'), str)
    
    def test_convert_value_none(self):
        """Testa conversão de string vazia"""
        assert FileReader._convert_value('') is None
        assert FileReader._convert_value(None) is None
    
    def test_list_files_in_directory(self):
        """Testa listagem de arquivos em diretório"""
        reader = FileReader()
        files = reader.list_files_in_directory('data/test_data')
        
        assert len(files) > 0
        assert 'users.json' in files or 'users.csv' in files


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestDataValidator:
    """Testes para a classe DataValidator."""
    
    def test_email_validator_valid(self):
        """Testa validação de e-mail válido"""
        validator_func = DataValidator.create_email_validator()
        
        is_valid, message = validator_func('test@example.com')
        assert is_valid is True
        assert message is None
    
    def test_email_validator_invalid(self):
        """Testa validação de e-mail inválido"""
        validator_func = DataValidator.create_email_validator()
        
        is_valid, message = validator_func('invalid-email')
        assert is_valid is False
        assert message is not None
    
    def test_range_validator_valid(self):
        """Testa validação de intervalo"""
        validator_func = DataValidator.create_range_validator(min_val=0, max_val=100)
        
        is_valid, message = validator_func(50)
        assert is_valid is True
        
        is_valid, message = validator_func(50.5)
        assert is_valid is True
    
    def test_range_validator_below_minimum(self):
        """Testa validação abaixo do mínimo"""
        validator_func = DataValidator.create_range_validator(min_val=10)
        
        is_valid, message = validator_func(5)
        assert is_valid is False
    
    def test_range_validator_above_maximum(self):
        """Testa validação acima do máximo"""
        validator_func = DataValidator.create_range_validator(max_val=100)
        
        is_valid, message = validator_func(150)
        assert is_valid is False
    
    def test_string_length_validator(self):
        """Testa validação de comprimento de string"""
        validator_func = DataValidator.create_string_length_validator(min_length=3, max_length=10)
        
        is_valid, _ = validator_func('hello')
        assert is_valid is True
        
        is_valid, _ = validator_func('ab')
        assert is_valid is False
        
        is_valid, _ = validator_func('this is too long')
        assert is_valid is False
    
    def test_type_validator(self):
        """Testa validação de tipo"""
        validator_func = DataValidator.create_type_validator(str)
        
        is_valid, _ = validator_func('hello')
        assert is_valid is True
        
        is_valid, _ = validator_func(123)
        assert is_valid is False
    
    def test_enum_validator(self):
        """Testa validação de valores permitidos"""
        allowed = ['admin', 'user', 'moderator']
        validator_func = DataValidator.create_enum_validator(allowed)
        
        is_valid, _ = validator_func('admin')
        assert is_valid is True
        
        is_valid, _ = validator_func('superuser')
        assert is_valid is False


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestDataProvider:
    """Testes para a classe DataProvider."""
    
    def test_singleton_instance(self):
        """Testa que DataProvider é Singleton"""
        provider1 = DataProvider()
        provider2 = DataProvider()
        
        assert provider1 is provider2
    
    def test_get_user_data_json(self):
        """Testa obtenção de dados de usuários de JSON"""
        provider = DataProvider()
        provider.set_default_source(DataSourceType.JSON)
        
        data = provider.get_user_data()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert all('id' in item for item in data)
        assert all('email' in item for item in data)
    
    def test_get_user_data_csv(self):
        """Testa obtenção de dados de usuários de CSV"""
        provider = DataProvider()
        
        data = provider.get_user_data(source=DataSourceType.CSV)
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert all('id' in item for item in data)
    
    def test_get_product_data_json(self):
        """Testa obtenção de dados de produtos de JSON"""
        provider = DataProvider()
        
        data = provider.get_product_data()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert all('price' in item for item in data)
    
    def test_get_data_generic(self):
        """Testa obtenção genérica de dados"""
        provider = DataProvider()
        
        data = provider.get_data(identifier='users')
        
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_data_without_identifier(self):
        """Testa que erro é lançado sem identificador"""
        provider = DataProvider()
        
        with pytest.raises(ValueError):
            provider.get_data()
    
    def test_hardcoded_strategy(self):
        """Testa estratégia de dados hardcoded"""
        provider = DataProvider()
        
        data = provider.get_data(
            source=DataSourceType.HARDCODED,
            identifier='default_user'
        )
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['name'] == 'Test User'
    
    def test_fallback_csv_to_json(self):
        """Testa fallback de CSV para JSON quando arquivo CSV não existe"""
        provider = DataProvider()
        provider.config.enable_fallback = True
        
        # Tenta obter um arquivo que só existe em JSON
        data = provider.get_data(
            source=DataSourceType.CSV,
            identifier='products'
        )
        
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_available_data_files_json(self):
        """Testa listagem de arquivos JSON disponíveis"""
        provider = DataProvider()
        
        files = provider.list_available_data_files(DataSourceType.JSON)
        
        assert isinstance(files, list)
        assert len(files) > 0
    
    def test_list_available_data_files_csv(self):
        """Testa listagem de arquivos CSV disponíveis"""
        provider = DataProvider()
        
        files = provider.list_available_data_files(DataSourceType.CSV)
        
        assert isinstance(files, list)
        assert len(files) > 0
    
    def test_list_available_data_files_hardcoded(self):
        """Testa listagem de dados hardcoded disponíveis"""
        provider = DataProvider()
        
        files = provider.list_available_data_files(DataSourceType.HARDCODED)
        
        assert isinstance(files, list)
        assert 'default_user' in files
        assert 'admin_user' in files
    
    def test_set_default_source(self):
        """Testa alteração da fonte de dados padrão"""
        provider = DataProvider()
        
        provider.set_default_source(DataSourceType.CSV)
        assert provider.config.default_source == DataSourceType.CSV
        
        provider.set_default_source(DataSourceType.JSON)
        assert provider.config.default_source == DataSourceType.JSON
    
    def test_validate_file_schema_json(self):
        """Testa validação de schema de arquivo JSON"""
        provider = DataProvider()
        
        schema = {
            'id': int,
            'name': str,
            'email': str,
            'active': bool
        }
        
        is_valid, errors = provider.validate_file_schema(
            'data/test_data/users.json',
            schema
        )
        
        assert is_valid is True or len(errors) == 0
    
    def test_validate_file_schema_csv(self):
        """Testa validação de schema de arquivo CSV"""
        provider = DataProvider()
        
        schema = {
            'id': int,
            'name': str,
            'email': str
        }
        
        is_valid, errors = provider.validate_file_schema(
            'data/test_data/users.csv',
            schema
        )
        
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestJSONDataStrategy:
    """Testes para a estratégia JSON."""
    
    def test_strategy_is_available(self):
        """Testa verificação de disponibilidade"""
        strategy = JSONDataStrategy('data/test_data')
        
        assert strategy.is_available() is True
    
    def test_strategy_get_data(self):
        """Testa obtenção de dados"""
        strategy = JSONDataStrategy('data/test_data')
        
        data = strategy.get_data('users')
        
        assert isinstance(data, list)
        assert len(data) > 0


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestCSVDataStrategy:
    """Testes para a estratégia CSV."""
    
    def test_strategy_is_available(self):
        """Testa verificação de disponibilidade"""
        strategy = CSVDataStrategy('data/test_data')
        
        assert strategy.is_available() is True
    
    def test_strategy_get_data(self):
        """Testa obtenção de dados"""
        strategy = CSVDataStrategy('data/test_data')
        
        data = strategy.get_data('users')
        
        assert isinstance(data, list)
        assert len(data) > 0


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestHardcodedDataStrategy:
    """Testes para a estratégia Hardcoded."""
    
    def test_strategy_is_available(self):
        """Sempre disponível"""
        strategy = HardcodedDataStrategy()
        
        assert strategy.is_available() is True
    
    def test_strategy_get_default_data(self):
        """Testa obtenção de dados padrão"""
        strategy = HardcodedDataStrategy()
        
        data = strategy.get_data()
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['name'] == 'Test User'
    
    def test_strategy_get_specific_data(self):
        """Testa obtenção de dados específicos"""
        strategy = HardcodedDataStrategy()
        
        data = strategy.get_data('admin_user')
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['role'] == 'admin'


@pytest.mark.unit
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestDataProviderConfig:
    """Testes para a configuração do Data Provider."""
    
    def test_config_singleton(self):
        """Testa que Config é Singleton"""
        config1 = DataProviderConfig()
        config2 = DataProviderConfig()
        
        assert config1 is config2
    
    def test_default_config_values(self):
        """Testa valores padrão de configuração"""
        config = DataProviderConfig()
        
        assert config.default_source == DataSourceType.JSON
        assert config.validate_data is True
        assert config.enable_fallback is True
        assert config.max_records == 100
    
    def test_set_default_source(self):
        """Testa alteração de fonte padrão"""
        config = DataProviderConfig()
        
        config.set_default_source(DataSourceType.CSV)
        assert config.default_source == DataSourceType.CSV
    
    def test_get_config(self):
        """Testa obtenção de configuração como dicionário"""
        config = DataProviderConfig()
        
        config_dict = config.get_config()
        
        assert isinstance(config_dict, dict)
        assert 'default_source' in config_dict
        assert 'data_path' in config_dict
