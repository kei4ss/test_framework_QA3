"""
Data Validator Module - Valida dados antes de serem usados nos testes
"""
from typing import Dict, List, Any, Optional, Callable
import re


class ValidationRule:
    """Representa uma regra de validação para um campo específico"""
    
    def __init__(self, field_name: str, validators: List[Callable]):
        """
        Args:
            field_name (str): Nome do campo a validar
            validators (List[Callable]): Lista de funções validadoras
        """
        self.field_name = field_name
        self.validators = validators
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Valida um valor contra todos os validadores
        
        Returns:
            tuple: (é_válido, mensagem_erro)
        """
        for validator in self.validators:
            is_valid, message = validator(value)
            if not is_valid:
                return False, message
        return True, None


class DataValidator:
    """
    Classe responsável por validar dados antes de uso nos testes
    Suporta validação customizável e transformação de dados
    """
    
    def __init__(self):
        """Inicializa o validador com regras padrão"""
        self.rules: Dict[str, ValidationRule] = {}
    
    def add_rule(self, field_name: str, validators: List[Callable]):
        """
        Adiciona uma regra de validação para um campo
        
        Args:
            field_name (str): Nome do campo
            validators (List[Callable]): Lista de funções validadoras
        """
        self.rules[field_name] = ValidationRule(field_name, validators)
    
    def validate(self, data: Dict[str, Any], strict: bool = False) -> tuple[bool, List[str]]:
        """
        Valida um dicionário de dados contra as regras definidas
        
        Args:
            data (Dict): Dados a validar
            strict (bool): Se True, falha em dados inválidos; se False, tenta recuperar
            
        Returns:
            tuple: (é_válido, lista_de_erros)
        """
        errors = []
        
        for field_name, rule in self.rules.items():
            if field_name not in data:
                if strict:
                    errors.append(f"Campo obrigatório ausente: {field_name}")
                continue
            
            value = data[field_name]
            is_valid, message = rule.validate(value)
            
            if not is_valid:
                errors.append(f"Campo '{field_name}': {message}")
        
        return len(errors) == 0, errors
    
    def validate_list(self, data_list: List[Dict[str, Any]], strict: bool = False) -> tuple[List[Dict], List[Dict]]:
        """
        Valida uma lista de dicionários
        
        Args:
            data_list (List[Dict]): Lista de dados a validar
            strict (bool): Se True, falha em dados inválidos
            
        Returns:
            tuple: (dados_válidos, dados_inválidos)
        """
        valid_data = []
        invalid_data = []
        
        for item in data_list:
            is_valid, errors = self.validate(item, strict)
            if is_valid:
                valid_data.append(item)
            else:
                invalid_data.append({'data': item, 'errors': errors})
        
        return valid_data, invalid_data
    
    @staticmethod
    def create_email_validator() -> Callable:
        """Cria um validador para e-mail"""
        def validate_email(email: Any) -> tuple[bool, Optional[str]]:
            if not isinstance(email, str):
                return False, "E-mail deve ser uma string"
            
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                return False, f"E-mail inválido: {email}"
            
            return True, None
        
        return validate_email
    
    @staticmethod
    def create_range_validator(min_val: float = None, max_val: float = None) -> Callable:
        """Cria um validador para valores dentro de um intervalo"""
        def validate_range(value: Any) -> tuple[bool, Optional[str]]:
            try:
                num_value = float(value)
            except (TypeError, ValueError):
                return False, f"Valor deve ser numérico, recebido: {value}"
            
            if min_val is not None and num_value < min_val:
                return False, f"Valor {num_value} é menor que o mínimo {min_val}"
            
            if max_val is not None and num_value > max_val:
                return False, f"Valor {num_value} é maior que o máximo {max_val}"
            
            return True, None
        
        return validate_range
    
    @staticmethod
    def create_string_length_validator(min_length: int = None, max_length: int = None) -> Callable:
        """Cria um validador para comprimento de string"""
        def validate_length(value: Any) -> tuple[bool, Optional[str]]:
            if not isinstance(value, str):
                return False, f"Valor deve ser string, recebido: {type(value)}"
            
            if min_length is not None and len(value) < min_length:
                return False, f"String tem {len(value)} caracteres, mínimo é {min_length}"
            
            if max_length is not None and len(value) > max_length:
                return False, f"String tem {len(value)} caracteres, máximo é {max_length}"
            
            return True, None
        
        return validate_length
    
    @staticmethod
    def create_type_validator(expected_type: type) -> Callable:
        """Cria um validador para tipo de dados"""
        def validate_type(value: Any) -> tuple[bool, Optional[str]]:
            if not isinstance(value, expected_type):
                return False, f"Tipo esperado {expected_type.__name__}, recebido {type(value).__name__}"
            
            return True, None
        
        return validate_type
    
    @staticmethod
    def create_enum_validator(allowed_values: List[Any]) -> Callable:
        """Cria um validador para valores permitidos"""
        def validate_enum(value: Any) -> tuple[bool, Optional[str]]:
            if value not in allowed_values:
                return False, f"Valor '{value}' não está em valores permitidos: {allowed_values}"
            
            return True, None
        
        return validate_enum
