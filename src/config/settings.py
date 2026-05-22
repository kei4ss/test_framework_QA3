from dotenv import load_dotenv
import os

root_dir = os.path.join(os.path.dirname(__file__), '../../')

root_env_path = os.path.join(root_dir, '.env')
dev_env_path = os.path.join(root_dir, '/environments/.env.dev')
prod_env_path = os.path.join(root_dir, '/environments/.env.prod')
staging_env_path = os.path.join(root_dir, '/environments/.env.staging')

# Carregando as variáveis de ambiente do arquivo principal .env
load_dotenv(dotenv_path=root_env_path)

# Verifico qual ambiente está sendo executado e carrego as variáveis de ambiente correspondentes
if os.getenv('MODE') == 'DEV':
    load_dotenv(dotenv_path=dev_env_path)
elif os.getenv('MODE') == 'PROD':
    load_dotenv(dotenv_path=prod_env_path)
elif os.getenv('MODE') == 'STAGING':
    load_dotenv(dotenv_path=staging_env_path)
else:
    raise ValueError("MODE inválido. Use 'DEV', 'PROD' ou 'STAGING'.")

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
        self.__db_password = os.getenv('DB_PASSWORD', 'password')
        self.__db_name = os.getenv('DB_NAME', 'database')

        self.__api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        self.__api_key = os.getenv('API_KEY', '')
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


    def get_mode(self):
        return self.__mode
    def get_log_level(self):
        return self.__log_level
    def get_app_name(self):
        return self.__app_name
    def get_app_version(self):
        return self.__app_version
    def get_timezone(self):
        return self.__timezone
    def get_default_language(self):
        return self.__default_language
    
    def get_db_host(self):
        return self.__db_host
    def get_db_port(self):
        return self.__db_port
    def get_db_user(self):
        return self.__db_user
    def get_db_password(self):
        return self.__db_password
    def get_db_name(self):
        return self.__db_name

    def get_api_base_url(self):
        return self.__api_base_url
    def get_api_key(self):
        return self.__api_key
    def get_api_endpoints(self):
        return self.__api_endpoints
    
    def get_timeout(self):
        return self.__timeout
