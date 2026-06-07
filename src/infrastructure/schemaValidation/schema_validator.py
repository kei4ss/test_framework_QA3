from typing import Any, Dict, Iterable, List

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match


class SchemaValidationError(AssertionError):
    """Erro de validação de schema com mensagem legível para testes."""


class SchemaValidator:
    """Valida payloads JSON usando JSON Schema."""

    @staticmethod
    def validate(payload: Any, schema: Dict[str, Any]) -> bool:
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(payload))
        if not errors:
            return True

        main_error = best_match(errors) or errors[0]
        readable_errors = SchemaValidator.collect_errors(payload, schema)
        raise SchemaValidationError(
            "Schema validation failed: "
            f"{SchemaValidator._format_error(main_error)}"
            f" | details={readable_errors}"
        )

    @staticmethod
    def validate_many(payloads: Iterable[Any], schema: Dict[str, Any]) -> bool:
        return SchemaValidator.validate(list(payloads), schema)

    @staticmethod
    def collect_errors(payload: Any, schema: Dict[str, Any]) -> List[str]:
        validator = Draft202012Validator(schema)
        return [
            SchemaValidator._format_error(error)
            for error in validator.iter_errors(payload)
        ]

    @staticmethod
    def _format_error(error: Any) -> str:
        path = ".".join(str(item) for item in error.absolute_path) or "<root>"
        return f"path={path}: {error.message}"
