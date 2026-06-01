"""
Exemplos de Uso do Data Provider
Demonstra como utilizar o Data Provider em diferentes cenários de teste
"""

from src.utils.data_provider import DataProvider
from src.utils.data_validator import DataValidator
from src.config.data_provider_config import DataSourceType


# ============================================================================
# EXEMPLO 1: Uso Básico - Obter Dados Padrão
# ============================================================================

def exemplo_uso_basico():
    """
    Exemplo mais simples de como usar o Data Provider
    Obtém dados usando a configuração padrão (JSON)
    """
    print("\n=== EXEMPLO 1: Uso Básico ===")
    
    # Obter instância do Data Provider (Singleton)
    provider = DataProvider()
    
    # Obter dados de usuários (usa JSON por padrão)
    usuarios = provider.get_user_data()
    
    print(f"Total de usuários obtidos: {len(usuarios)}")
    print(f"Primeiro usuário: {usuarios[0]['name']} ({usuarios[0]['email']})")


# ============================================================================
# EXEMPLO 2: Usar Fonte Específica
# ============================================================================

def exemplo_fonte_especifica():
    """
    Exemplo usando uma fonte específica de dados
    Demonstra como forçar uma estratégia particular
    """
    print("\n=== EXEMPLO 2: Usar Fonte Específica ===")
    
    provider = DataProvider()
    
    # Obter dados de JSON explicitamente
    usuarios_json = provider.get_user_data(source=DataSourceType.JSON)
    print(f"Usuários de JSON: {len(usuarios_json)}")
    
    # Obter dados de CSV
    usuarios_csv = provider.get_user_data(source=DataSourceType.CSV)
    print(f"Usuários de CSV: {len(usuarios_csv)}")
    
    # Obter dados hardcoded
    usuarios_hardcoded = provider.get_user_data(
        source=DataSourceType.HARDCODED,
        identifier='default_user'
    )
    print(f"Usuários Hardcoded: {len(usuarios_hardcoded)}")
    print(f"Usuário Hardcoded: {usuarios_hardcoded[0]['name']}")


# ============================================================================
# EXEMPLO 3: Fallback Automático
# ============================================================================

def exemplo_fallback_automatico():
    """
    Exemplo demonstrando o fallback automático entre fontes
    Se uma fonte não tiver o arquivo, tenta automaticamente outra
    """
    print("\n=== EXEMPLO 3: Fallback Automático ===")
    
    provider = DataProvider()
    provider.config.enable_fallback = True
    
    # Tenta obter "products" (só existe em JSON)
    # Se não conseguir de CSV, automaticamente tenta JSON
    produtos = provider.get_data(
        source=DataSourceType.CSV,
        identifier='products'
    )
    
    print(f"Produtos obtidos (com fallback): {len(produtos)}")
    print(f"Primeiro produto: {produtos[0]['name']} - R${produtos[0]['price']}")


# ============================================================================
# EXEMPLO 4: Configurar Fonte Preferencial
# ============================================================================

def exemplo_configurar_fonte():
    """
    Exemplo de como alterar a fonte de dados preferencial
    """
    print("\n=== EXEMPLO 4: Configurar Fonte Preferencial ===")
    
    provider = DataProvider()
    
    # Definir CSV como fonte preferencial
    provider.set_default_source(DataSourceType.CSV)
    print(f"Fonte preferencial agora: {provider.config.default_source.value}")
    
    # Obter dados usa a nova fonte por padrão
    usuarios = provider.get_user_data()
    print(f"Usuários obtidos da fonte preferencial (CSV): {len(usuarios)}")


# ============================================================================
# EXEMPLO 5: Listar Dados Disponíveis
# ============================================================================

def exemplo_listar_dados():
    """
    Exemplo de como listar quais dados estão disponíveis
    Útil para descobrir que arquivos podem ser carregados
    """
    print("\n=== EXEMPLO 5: Listar Dados Disponíveis ===")
    
    provider = DataProvider()
    
    # Listar arquivos JSON disponíveis
    arquivos_json = provider.list_available_data_files(DataSourceType.JSON)
    print(f"Arquivos JSON disponíveis: {arquivos_json}")
    
    # Listar arquivos CSV disponíveis
    arquivos_csv = provider.list_available_data_files(DataSourceType.CSV)
    print(f"Arquivos CSV disponíveis: {arquivos_csv}")
    
    # Listar dados hardcoded disponíveis
    dados_hardcoded = provider.list_available_data_files(DataSourceType.HARDCODED)
    print(f"Dados Hardcoded disponíveis: {dados_hardcoded}")


# ============================================================================
# EXEMPLO 6: Validação de Dados
# ============================================================================

def exemplo_validacao_dados():
    """
    Exemplo de como validar dados com regras customizadas
    """
    print("\n=== EXEMPLO 6: Validação de Dados ===")
    
    # Criar validador
    validator = DataValidator()
    
    # Definir regras de validação
    validator.add_rule('email', [
        DataValidator.create_email_validator()
    ])
    
    validator.add_rule('age', [
        DataValidator.create_range_validator(min_val=18, max_val=120)
    ])
    
    validator.add_rule('role', [
        DataValidator.create_enum_validator(['admin', 'user', 'moderator'])
    ])
    
    # Dados para validar
    usuario_valido = {
        'email': 'joao@example.com',
        'age': 28,
        'role': 'user'
    }
    
    usuario_invalido = {
        'email': 'email-invalido',
        'age': 15,
        'role': 'superuser'
    }
    
    # Validar dados
    is_valid, errors = validator.validate(usuario_valido)
    print(f"Usuário válido: {is_valid}")
    
    is_valid, errors = validator.validate(usuario_invalido)
    print(f"Usuário inválido: {is_valid}")
    print(f"Erros encontrados: {errors}")


# ============================================================================
# EXEMPLO 7: Usar em Testes
# ============================================================================

def exemplo_teste_com_data_provider():
    """
    Exemplo realista de como usar Data Provider em um teste
    Demonstra o caso de uso principal: testes data-driven
    """
    print("\n=== EXEMPLO 7: Usar em Teste ===")
    
    def test_criar_usuario_com_data_provider():
        """Teste que usa Data Provider para dados"""
        provider = DataProvider()
        
        # Obter dados de teste
        usuarios_teste = provider.get_user_data()
        
        # Iterar sobre os dados e fazer testes
        for usuario in usuarios_teste:
            print(f"\nTestando criação de usuário: {usuario['name']}")
            
            # Aqui seria feita a chamada real à API
            # response = api.criar_usuario(
            #     name=usuario['name'],
            #     email=usuario['email'],
            #     password=usuario['password']
            # )
            
            # Validações esperadas
            assert 'id' in usuario
            assert '@' in usuario['email']
            assert len(usuario['password']) > 0
            
            print(f"✓ Usuário {usuario['name']} validado com sucesso")
    
    # Executar o teste
    test_criar_usuario_com_data_provider()


# ============================================================================
# EXEMPLO 8: Validação de Schema de Arquivo
# ============================================================================

def exemplo_validacao_schema():
    """
    Exemplo de como validar se um arquivo de dados segue um schema esperado
    Útil para garantir integridade dos dados de teste
    """
    print("\n=== EXEMPLO 8: Validação de Schema ===")
    
    provider = DataProvider()
    
    # Definir schema esperado
    schema_usuario = {
        'id': int,
        'name': str,
        'email': str,
        'password': str,
        'age': int,
        'role': str,
        'active': bool
    }
    
    # Validar arquivo JSON contra schema
    is_valid, errors = provider.validate_file_schema(
        'data/test_data/users.json',
        schema_usuario
    )
    
    print(f"Arquivo users.json válido: {is_valid}")
    if not is_valid:
        print(f"Erros encontrados: {errors}")


# ============================================================================
# EXEMPLO 9: Múltiplas Validações em Lista de Dados
# ============================================================================

def exemplo_validacao_lista():
    """
    Exemplo de validação de uma lista completa de dados
    Retorna dados válidos e inválidos separadamente
    """
    print("\n=== EXEMPLO 9: Validação de Lista ===")
    
    provider = DataProvider()
    validator = DataValidator()
    
    # Adicionar regra de validação
    validator.add_rule('email', [
        DataValidator.create_email_validator()
    ])
    
    # Obter dados
    usuarios = provider.get_user_data()
    
    # Validar lista
    usuarios_validos, usuarios_invalidos = validator.validate_list(usuarios)
    
    print(f"Total de usuários: {len(usuarios)}")
    print(f"Usuários válidos: {len(usuarios_validos)}")
    print(f"Usuários inválidos: {len(usuarios_invalidos)}")


# ============================================================================
# EXEMPLO 10: Padrão Singleton - Mesma Instância
# ============================================================================

def exemplo_singleton():
    """
    Demonstra o padrão Singleton do DataProvider
    Sempre retorna a mesma instância
    """
    print("\n=== EXEMPLO 10: Padrão Singleton ===")
    
    # Obter duas instâncias
    provider1 = DataProvider()
    provider2 = DataProvider()
    
    # Verificar que são a mesma instância
    print(f"provider1 is provider2: {provider1 is provider2}")
    print(f"ID provider1: {id(provider1)}")
    print(f"ID provider2: {id(provider2)}")
    
    # Modificar em uma afeta a outra
    provider1.set_default_source(DataSourceType.CSV)
    print(f"Fonte em provider2 agora: {provider2.config.default_source.value}")


# ============================================================================
# EXEMPLO 11: Usar Dados Diferentes para Diferentes Cenários
# ============================================================================

def exemplo_multiplos_cenarios():
    """
    Exemplo de como usar diferentes dados para diferentes cenários de teste
    """
    print("\n=== EXEMPLO 11: Múltiplos Cenários ===")
    
    provider = DataProvider()
    
    # Cenário 1: Usuário padrão
    usuario_padrao = provider.get_user_data(
        source=DataSourceType.HARDCODED,
        identifier='default_user'
    )[0]
    print(f"Cenário 1 - Usuário padrão: {usuario_padrao['name']} ({usuario_padrao['role']})")
    
    # Cenário 2: Usuário admin
    usuario_admin = provider.get_user_data(
        source=DataSourceType.HARDCODED,
        identifier='admin_user'
    )[0]
    print(f"Cenário 2 - Usuário admin: {usuario_admin['name']} ({usuario_admin['role']})")
    
    # Cenário 3: Usuário inativo
    usuario_inativo = provider.get_user_data(
        source=DataSourceType.HARDCODED,
        identifier='inactive_user'
    )[0]
    print(f"Cenário 3 - Usuário inativo: {usuario_inativo['name']} (ativo={usuario_inativo['active']})")


# ============================================================================
# Executar Todos os Exemplos
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("EXEMPLOS DE USO DO DATA PROVIDER")
    print("=" * 70)
    
    exemplo_uso_basico()
    exemplo_fonte_especifica()
    exemplo_fallback_automatico()
    exemplo_configurar_fonte()
    exemplo_listar_dados()
    exemplo_validacao_dados()
    exemplo_teste_com_data_provider()
    exemplo_validacao_schema()
    exemplo_validacao_lista()
    exemplo_singleton()
    exemplo_multiplos_cenarios()
    
    print("\n" + "=" * 70)
    print("TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
    print("=" * 70)
