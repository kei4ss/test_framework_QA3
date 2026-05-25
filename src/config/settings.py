from dotenv import load_dotenv
import os

root_dir = os.path.join(os.path.dirname(__file__), '../../')


def resolve_env_file(base_dir, file_name='.env'):
    candidates = [
        os.path.join(base_dir, file_name),
        os.path.join(base_dir, '.env.test'),
        os.path.join(base_dir, '.env.example'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


# Carregando as variáveis de ambiente do arquivo principal
root_env_path = resolve_env_file(root_dir, '.env')
if root_env_path is None:
    raise FileNotFoundError(
        f"Arquivo .env principal não encontrado em: {os.path.join(root_dir, '.env')}\n"
        "Certifique-se de criar um arquivo .env/.env.test/.env.example na raiz do projeto."
    )
load_dotenv(dotenv_path=root_env_path)


# Carrega variaveis de ambiente específicas para cada ambiente (DEV, PROD, STAGING)
def load_environment_variables(env_dir, env_name):
    env_path = resolve_env_file(env_dir, '.env')
    if env_path is None:
        raise FileNotFoundError(
            f"Arquivo .env de {env_name} não encontrado em: {os.path.join(env_dir, '.env')}\n"
            f"Certifique-se de criar um arquivo .env/.env.test/.env.example para {env_name}."
        )
    load_dotenv(dotenv_path=env_path)


raw_mode = (os.getenv('MODE') or '').strip().upper()
mode = 'DEV' if not raw_mode or raw_mode.startswith('#') else raw_mode

match mode:
    case 'DEV':
        dev_env_path = os.path.join(root_dir, 'environments', 'dev')
        load_environment_variables(dev_env_path, 'desenvolvimento')
    case 'PROD':
        prod_env_path = os.path.join(root_dir, 'environments', 'prod')
        load_environment_variables(prod_env_path, 'produção')
    case 'STAGING':
        staging_env_path = os.path.join(root_dir, 'environments', 'staging')
        load_environment_variables(staging_env_path, 'staging')
    case _:
        raise ValueError("MODE inválido. Use 'DEV', 'PROD' ou 'STAGING'.")


# Classe de configuração para acessar as variáveis de ambiente de forma estruturada
class settings:
    __instace = None
    __initialized = False

    def __new__(cls):
        if cls.__instace is None:
            cls.__instace = super().__new__(cls)
        return cls.__instace

    def __init__(self):
        if self.__initialized:
            return

        self.__mode = os.getenv('MODE')
        self.__log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.__app_name = os.getenv('APP_NAME', "Minha Aplicação")
        self.__app_version = os.getenv('APP_VERSION', "1.0.0")
        self.__timezone = os.getenv('TIMEZONE', "UTC")
        self.__default_language = os.getenv('DEFAULT_LANGUAGE', "pt-BR")

        self.__db_host = os.getenv('DB_HOST', 'localhost')
        self.__db_port = os.getenv('DB_PORT', '5432')
        self.__db_user = os.getenv('DB_USER', 'user')
        self.__db_password = os.getenv('DB_PASSWORD')
        self.__db_name = os.getenv('DB_NAME', 'database')

        self.__api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        self.__api_endpoints = os.getenv('API_ENDPOINTS', '').split(',')

        self.__timeout = int(os.getenv('TIMEOUT', '30'))

        self.__initialized = True

        print(f"Configurações carregadas para o ambiente: {self.__mode}")
        print(f"Nível de log: {self.__log_level}")
        print(f"Nome da aplicação: {self.__app_name}")
        print(f"Versão da aplicação: {self.__app_version}")
        print(f"Fuso horário: {self.__timezone}")
        print(f"Idioma padrão: {self.__default_language}")
        print(f"Configurações de banco de dados: {self.__db_host}:{self.__db_port} (Usuário: {self.__db_user})")
        print(f"Configurações de API: Base URL: {self.__api_base_url}, Endpoints: {self.__api_endpoints}")

    def database_config(self):
        if self.__db_password is None:
            raise ValueError("A variável de ambiente DB_PASSWORD é obrigatória e não pode estar vazia.")

        return {
            "host": self.__db_host,
            "port": self.__db_port,
            "user": self.__db_user,
            "password": self.__db_password,
            "name": self.__db_name
        }

    def api_config(self):
        return {
            "base_url": self.__api_base_url,
            "endpoints": self.__api_endpoints
        }

    def global_config(self):
        return {
            "mode": self.__mode,
            "log_level": self.__log_level,
            "app_name": self.__app_name,
            "app_version": self.__app_version,
            "timezone": self.__timezone,
            "default_language": self.__default_language
        }

    def performance_config(self):
        return {
            "timeout": self.__timeout
        }

    def api_config(self):
        if not self.__api_base_url:
            raise ValueError("A variável de ambiente API_BASE_URL é obrigatória e não pode estar vazia.")

        return {
            "base_url": self.__api_base_url,
            "endpoints": self.__api_endpoints
        }
