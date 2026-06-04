"""
Testes unitários para a classe Logger.

Cobre:
- Padrão Singleton
- Criação de arquivos de log
- Escrita de logs em múltiplos níveis
- Formatação de mensagens
- Mascaramento de dados sensíveis
- Logging de requisições HTTP
"""

import logging
import logging.handlers
import re
import pytest

from src.infrastructure.logger.logger import Logger


def _reset_logger_singleton():
    """Reseta a instância do Logger para testes isolados."""
    Logger._Logger__instance = None
    Logger._Logger__initialized = False
    test_logger = logging.getLogger("SentinelaLogger")
    for handler in test_logger.handlers[:]:
        handler.close()
        test_logger.removeHandler(handler)


@pytest.mark.unit
class TestLoggerSingleton:
    """Testes do padrão Singleton do Logger."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_return_same_instance_when_instantiated_multiple_times(self, tmp_path):
        """Múltiplas instâncias devem retornar o mesmo objeto."""
        # Act
        logger_a = Logger(log_level="INFO", log_dir=str(tmp_path))
        logger_b = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Assert
        assert logger_a is logger_b
    
    def test_should_ignore_different_parameters_on_second_instantiation(self, tmp_path):
        """Segunda instância deve ignorar parâmetros diferentes."""
        # Arrange
        Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        logger_b = Logger(log_level="DEBUG", log_dir=str(tmp_path))
        
        # Assert
        internal = logger_b.get_logger()
        assert internal.level == logging.INFO


@pytest.mark.unit
class TestLogFileCreation:
    """Testes de criação de arquivos de log."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_create_log_directory_automatically(self, tmp_path):
        """Logger deve criar diretório de logs automaticamente."""
        # Arrange
        new_dir = tmp_path / "subdir" / "logs"
        assert not new_dir.exists()
        
        # Act
        Logger(log_level="INFO", log_dir=str(new_dir))
        
        # Assert
        assert new_dir.exists()
    
    def test_should_create_general_log_file(self, tmp_path):
        """Logger deve criar arquivo sentinela.log."""
        # Act
        Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Assert
        assert (tmp_path / "sentinela.log").exists()
    
    def test_should_create_error_log_file(self, tmp_path):
        """Logger deve criar arquivo errors.log."""
        # Act
        Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Assert
        assert (tmp_path / "errors.log").exists()


@pytest.mark.unit
class TestLogWriting:
    """Testes de escrita de mensagens no log."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_write_info_message_to_general_log(self, tmp_path):
        """Mensagens INFO devem aparecer no sentinela.log."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Teste de mensagem INFO")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Teste de mensagem INFO" in content
    
    def test_should_write_debug_when_log_level_is_debug(self, tmp_path):
        """DEBUG deve ser gravado quando nível é DEBUG."""
        # Arrange
        log = Logger(log_level="DEBUG", log_dir=str(tmp_path))
        
        # Act
        log.debug("Mensagem de debug detalhada")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Mensagem de debug detalhada" in content
    
    def test_should_not_write_debug_when_log_level_is_info(self, tmp_path):
        """DEBUG não deve ser gravado quando nível é INFO."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.debug("Esta mensagem NÃO deve aparecer")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Esta mensagem NÃO deve aparecer" not in content
    
    def test_should_write_warning_to_both_logs(self, tmp_path):
        """WARNING deve aparecer em sentinela.log e errors.log."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.warning("Aviso de atenção")
        
        # Assert
        general = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        errors = (tmp_path / "errors.log").read_text(encoding="utf-8")
        
        assert "Aviso de atenção" in general
        assert "Aviso de atenção" in errors
    
    def test_should_write_error_to_both_logs(self, tmp_path):
        """ERROR deve aparecer em sentinela.log e errors.log."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.error("Erro crítico de teste")
        
        # Assert
        general = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        errors = (tmp_path / "errors.log").read_text(encoding="utf-8")
        
        assert "Erro crítico de teste" in general
        assert "Erro crítico de teste" in errors
    
    def test_should_not_write_info_to_error_log(self, tmp_path):
        """INFO não deve aparecer em errors.log."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Apenas informação")
        
        # Assert
        errors = (tmp_path / "errors.log").read_text(encoding="utf-8")
        assert "Apenas informação" not in errors


@pytest.mark.unit
class TestLogSeverityLevels:
    """Testes de níveis de severidade."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    @pytest.mark.parametrize("level,method,message", [
        ("DEBUG", "debug",    "msg debug"),
        ("DEBUG", "info",     "msg info"),
        ("DEBUG", "warning",  "msg warning"),
        ("DEBUG", "error",    "msg error"),
        ("DEBUG", "critical", "msg critical"),
    ])
    def test_should_write_all_levels_when_log_level_is_debug(
        self,
        tmp_path,
        level,
        method,
        message,
    ):
        """Todos os níveis devem ser gravados com DEBUG."""
        # Arrange
        log = Logger(log_level=level, log_dir=str(tmp_path))
        
        # Act
        getattr(log, method)(message)
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert message in content
    
    def test_should_include_severity_level_in_formatted_message(self, tmp_path):
        """Nível de severidade deve aparecer na mensagem formatada."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.error("Falha simulada")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "ERROR" in content


@pytest.mark.unit
class TestLogFormatting:
    """Testes de formatação de mensagens de log."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_include_timestamp_in_message(self, tmp_path):
        """Timestamp deve estar presente na mensagem."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Testando timestamp")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert re.search(r'\d{4}-\d{2}-\d{2}', content), \
            "Data não encontrada no log"
    
    def test_should_use_brackets_in_format(self, tmp_path):
        """Formato padrão deve conter colchetes."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Mensagem para checar formato")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "[" in content and "]" in content
    
    def test_should_include_line_number_in_log(self, tmp_path):
        """Número da linha deve estar presente no log."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.warning("Verificando número de linha")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert re.search(r':\d+\]', content), \
            "Número de linha não encontrado no formato do log"


@pytest.mark.unit
class TestSensitiveDataMasking:
    """Testes de mascaramento de dados sensíveis."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_mask_password_field(self, tmp_path):
        """Campo password deve ser mascarado."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Tentando autenticar com password=minha_senha_secreta")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "minha_senha_secreta" not in content
        assert "***MASKED***" in content
    
    def test_should_mask_token_field(self, tmp_path):
        """Campo token deve ser mascarado."""
        # Arrange
        log = Logger(log_level="DEBUG", log_dir=str(tmp_path))
        
        # Act
        log.debug("Autorizando com token=eyJhbGciOiJIUzI1NiJ9.abc123")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "eyJhbGciOiJIUzI1NiJ9.abc123" not in content
        assert "***MASKED***" in content
    
    def test_should_mask_card_number(self, tmp_path):
        """Números de cartão devem ser mascarados."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Processando cartão 4111111111111111")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "4111111111111111" not in content
        assert "***CARD***" in content
    
    def test_should_not_mask_normal_text(self, tmp_path):
        """Texto normal não deve ser mascarado."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.info("Usuário joao.silva@email.com fez login")
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "joao.silva@email.com fez login" in content


@pytest.mark.unit
class TestHttpRequestLogging:
    """Testes de logging de requisições HTTP."""
    
    def setup_method(self):
        """Limpa singleton antes de cada teste."""
        _reset_logger_singleton()
    
    def test_should_log_successful_request(self, tmp_path):
        """Requisição bem-sucedida deve gerar log INFO."""
        # Arrange
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        
        # Act
        log.log_request("GET", "https://api.exemplo.com/users", 200, 0.342)
        
        # Assert
        content = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP GET" in content
        assert "200" in content


        erros = (tmp_path / "errors.log").read_text(encoding="utf-8")
        assert "HTTP GET" not in erros

    def test_requisicao_com_erro_cliente_gera_error(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.log_request("POST", "https://api.exemplo.com/login", 401, 0.150)

        erros = (tmp_path / "errors.log").read_text(encoding="utf-8")
        assert "401" in erros

    def test_formato_padrao_do_log_de_requisicao(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.log_request("DELETE", "https://api.exemplo.com/item/42", 204, 0.089)

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP DELETE" in conteudo
        assert "https://api.exemplo.com/item/42" in conteudo
        assert "204" in conteudo
        assert "0.089s" in conteudo

class TestRotacaoDeArquivos:

    def test_rotacao_cria_arquivo_backup(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))

        internal_logger = log.get_logger()
        rotating_handler = None
        for handler in internal_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                if "errors" not in handler.baseFilename:
                    rotating_handler = handler
                    break

        assert rotating_handler is not None, "RotatingFileHandler não encontrado"

        rotating_handler.maxBytes = 1

        log.info("Primeira mensagem — forçando rotação")
        log.info("Segunda mensagem — após rotação")

        backup = tmp_path / "sentinela.log.1"
        assert backup.exists(), \
            "Arquivo de backup sentinela.log.1 não foi criado após rotação"