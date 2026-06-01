"""
File Reader Module - Lê dados de arquivos JSON e CSV
"""
import json
import csv
import os
from typing import List, Dict, Any, Union


class FileReader:
    """
    Classe responsável por ler dados de diferentes tipos de arquivo
    Implementa o conceito de abstração para múltiplas fontes de dados
    """
    
    @staticmethod
    def read_json(file_path: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Lê um arquivo JSON e retorna os dados
        
        Args:
            file_path (str): Caminho completo do arquivo JSON
            
        Returns:
            Union[List[Dict], Dict]: Dados lidos do arquivo JSON
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            json.JSONDecodeError: Se o arquivo JSON for inválido
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo JSON não encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Erro ao decodificar JSON de {file_path}: {e.msg}", e.doc, e.pos)
    
    @staticmethod
    def read_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Lê um arquivo CSV e retorna os dados como lista de dicionários
        
        Args:
            file_path (str): Caminho completo do arquivo CSV
            
        Returns:
            List[Dict]: Lista de dicionários onde cada linha se torna um dicionário
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {file_path}")
        
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Converte valores booleanos em string para tipo bool
                    converted_row = {}
                    for key, value in row.items():
                        converted_row[key] = FileReader._convert_value(value)
                    data.append(converted_row)
            return data
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo CSV {file_path}: {str(e)}")
    
    @staticmethod
    def _convert_value(value: str) -> Any:
        """
        Tenta converter uma string em seu tipo apropriado
        
        Args:
            value (str): Valor em string
            
        Returns:
            Any: Valor convertido para tipo apropriado (int, float, bool, str)
        """
        if value is None or value == '':
            return None
        
        # Tenta converter para booleano
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        
        # Tenta converter para inteiro
        try:
            return int(value)
        except ValueError:
            pass
        
        # Tenta converter para float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Retorna como string
        return value
    
    @staticmethod
    def list_files_in_directory(directory: str, extension: str = None) -> List[str]:
        """
        Lista todos os arquivos em um diretório
        
        Args:
            directory (str): Caminho do diretório
            extension (str): Filtro por extensão (ex: '.json', '.csv')
            
        Returns:
            List[str]: Lista de nomes de arquivos
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extension is None or file.endswith(extension):
                    files.append(file)
        
        return files
