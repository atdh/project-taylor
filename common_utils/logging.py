import logging
import os
from pythonjsonlogger import jsonlogger
from datetime import datetime

def get_logger(service_name: str) -> logging.Logger:
    """
    Set up a JSON logger with consistent formatting across services
    Args:
        service_name: Name of the service for identification
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    
    # Set log level from environment variable or default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(log_level)

    # Create JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.utcnow().isoformat()
            log_record['service'] = service_name
            log_record['level'] = record.levelname
            log_record['correlation_id'] = getattr(record, 'correlation_id', None)

    # Create and configure handler
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(service)s %(level)s %(message)s %(correlation_id)s'
    )
    handler.setFormatter(formatter)
    
    # Remove existing handlers and add new one
    logger.handlers = []
    logger.addHandler(handler)
    
    return logger
