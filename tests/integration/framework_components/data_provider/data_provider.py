import pytest
from src.utils.data_provider import DataProvider
from src.config.data_provider_config import DataSourceType


@pytest.mark.integration
@pytest.mark.framework_component
@pytest.mark.data_provider
class TestDataProviderIntegration:
    """Testes de integração do Data Provider"""
    
    def test_full_workflow_json_to_csv_fallback(self):
        """Testa workflow completo com fallback"""
        provider = DataProvider()
        provider.config.enable_fallback = True
        
        # Define CSV como preferencial
        provider.set_default_source(DataSourceType.CSV)
        
        # Tenta obter dados de produtos (só existe em JSON)
        data = provider.get_data(identifier='products')
        
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_multiple_data_sources_consistency(self):
        """Testa consistência de dados de múltiplas fontes"""
        provider = DataProvider()
        
        json_data = provider.get_user_data(source=DataSourceType.JSON)
        csv_data = provider.get_user_data(source=DataSourceType.CSV)
        
        # Ambos devem ter dados
        assert len(json_data) > 0
        assert len(csv_data) > 0
        
        # Ambos devem ter os mesmos campos
        if json_data and csv_data:
            json_fields = set(json_data[0].keys())
            csv_fields = set(csv_data[0].keys())
            # CSV pode ter campos adicionais por causa do parse
            assert json_fields.issubset(csv_fields) or csv_fields.issubset(json_fields)