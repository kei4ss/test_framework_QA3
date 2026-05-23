import logging
import re

DEFAULT_LOG_LEVEL = "INFO"

GENERAL_LOG_FILENAME = "sentinela.log"

ERROR_LOG_FILENAME = "errors.log"

MAX_BYTES = 10 * 1024 * 1024

BACKUP_COUNT = 5

LOG_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(module)s:%(lineno)d] %(message)s"

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

SENSITIVE_PATTERNS = [
    (r'(?i)(password|senha|passwd)\s*[=:]\s*\S+', r'\1=***MASKED***'),
    (r'(?i)(token|api_key|apikey|secret|authorization)\s*[=:]\s*\S+',
     r'\1=***MASKED***'),
    (r'(?i)(credit_card|cc_number|card_number)\s*[=:]\s*\S+', r'\1=***MASKED***')
]

class SensitiveDataFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message)
        return message