import logging
import logging.handlers
import re
import pytest

from src.infraestructure.logger import Logger

@pytest.fixture(autouse=True)
def reset_logger_singleton():
    original_instance = Logger._Logger__instance
    original_initialized = Logger._Logger__initialized

    Logger._Logger__instance = None
    Logger._Logger__initialized = False

    yield

    Logger._Logger__instance = original_instance
    Logger._Logger__initialized = original_initialized

    test_logger = logging.getLogger("SentinelaLogger")
    for handler in test_logger.handlers[:]:
        handler.close()
        test_logger.removeHandler(handler)

class TestLoggerSingleton:

    def test_mesma_instancia_em_multiplas_chamadas(self, tmp_path):
        log_a = Logger(log_level="INFO", log_dir=str(tmp_path))
        log_b = Logger(log_level="INFO", log_dir=str(tmp_path))

        assert log_a is log_b

    def test_segunda_instancia_ignora_parametros_diferentes(self, tmp_path):
        Logger(log_level="INFO", log_dir=str(tmp_path))

        log_b = Logger(log_level="DEBUG", log_dir=str(tmp_path))

        internal = log_b.get_logger()
        assert internal.level == logging.INFO

class TestCriacaoDeArquivos:

    def test_cria_diretorio_de_logs_automaticamente(self, tmp_path):
        novo_dir = tmp_path / "subdir" / "logs"
        assert not novo_dir.exists()

        Logger(log_level="INFO", log_dir=str(novo_dir))

        assert novo_dir.exists()

    def test_cria_arquivo_de_log_geral(self, tmp_path):
        Logger(log_level="INFO", log_dir=str(tmp_path))
        assert (tmp_path / "sentinela.log").exists()

    def test_cria_arquivo_de_erros(self, tmp_path):
        Logger(log_level="INFO", log_dir=str(tmp_path))
        assert (tmp_path / "errors.log").exists()

class TestEscritaDeLogs:

    def test_mensagem_info_gravada_no_arquivo_geral(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Teste de mensagem INFO")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Teste de mensagem INFO" in conteudo

    def test_mensagem_debug_gravada_quando_nivel_e_debug(self, tmp_path):
        log = Logger(log_level="DEBUG", log_dir=str(tmp_path))
        log.debug("Mensagem de debug detalhada")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Mensagem de debug detalhada" in conteudo

    def test_mensagem_debug_nao_gravada_quando_nivel_e_info(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.debug("Esta mensagem NÃO deve aparecer")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "Esta mensagem NÃO deve aparecer" not in conteudo

    def test_mensagem_warning_aparece_em_ambos_arquivos(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.warning("Aviso de atenção")

        geral = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        erros = (tmp_path / "errors.log").read_text(encoding="utf-8")

        assert "Aviso de atenção" in geral
        assert "Aviso de atenção" in erros

    def test_mensagem_error_aparece_em_ambos_arquivos(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.error("Erro crítico de teste")

        geral = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        erros = (tmp_path / "errors.log").read_text(encoding="utf-8")

        assert "Erro crítico de teste" in geral
        assert "Erro crítico de teste" in erros

    def test_mensagem_info_nao_aparece_em_errors_log(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Apenas informação")

        erros = (tmp_path / "errors.log").read_text(encoding="utf-8")
        assert "Apenas informação" not in erros

class TestNiveisDeSeveridade:

    @pytest.mark.parametrize("nivel,metodo,mensagem", [
        ("DEBUG", "debug",    "msg debug"),
        ("DEBUG", "info",     "msg info"),
        ("DEBUG", "warning",  "msg warning"),
        ("DEBUG", "error",    "msg error"),
        ("DEBUG", "critical", "msg critical"),
    ])
    def test_todos_niveis_com_log_level_debug(self, tmp_path, nivel, metodo, mensagem):
        log = Logger(log_level=nivel, log_dir=str(tmp_path))
        getattr(log, metodo)(mensagem)

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert mensagem in conteudo

    def test_nivel_aparece_na_mensagem_formatada(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.error("Falha simulada")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "ERROR" in conteudo

class TestFormatacao:

    def test_timestamp_presente_na_mensagem(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Testando timestamp")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert re.search(r'\d{4}-\d{2}-\d{2}', conteudo), \
            "Data não encontrada no log — verifique o formato do timestamp"

    def test_formato_padrao_contem_colchetes(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Mensagem para checar formato")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "[" in conteudo and "]" in conteudo

    def test_numero_da_linha_presente_no_log(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.warning("Verificando número de linha")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert re.search(r':\d+\]', conteudo), \
            "Número de linha não encontrado no formato do log"

class TestMascaramentoDeSensitivos:

    def test_senha_e_mascarada(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Tentando autenticar com password=minha_senha_secreta")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "minha_senha_secreta" not in conteudo
        assert "***MASKED***" in conteudo

    def test_token_e_mascarado(self, tmp_path):
        log = Logger(log_level="DEBUG", log_dir=str(tmp_path))
        log.debug("Autorizando com token=eyJhbGciOiJIUzI1NiJ9.abc123")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "eyJhbGciOiJIUzI1NiJ9.abc123" not in conteudo
        assert "***MASKED***" in conteudo

    def test_numero_cartao_e_mascarado(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Processando cartão 4111111111111111")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "4111111111111111" not in conteudo
        assert "***CARD***" in conteudo

    def test_texto_normal_nao_e_mascarado(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.info("Usuário joao.silva@email.com fez login")

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "joao.silva@email.com fez login" in conteudo

class TestLogRequest:

    def test_requisicao_bem_sucedida_gera_info(self, tmp_path):
        log = Logger(log_level="INFO", log_dir=str(tmp_path))
        log.log_request("GET", "https://api.exemplo.com/users", 200, 0.342)

        conteudo = (tmp_path / "sentinela.log").read_text(encoding="utf-8")
        assert "HTTP GET" in conteudo
        assert "200" in conteudo

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