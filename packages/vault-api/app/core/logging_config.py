"""Structured logging configuration"""
import logging
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
import uuid


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id


def setup_logging(log_level: str = "INFO"):
    """Setup structured logging"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for security logs
    security_handler = logging.FileHandler('logs/security.log')
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(formatter)
    logger.addHandler(security_handler)
    
    return logger


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_oauth_attempt(self, provider: str, user_id: str, success: bool, ip_address: str):
        """Log OAuth authentication attempt"""
        self.logger.info(
            "OAuth attempt",
            extra={
                'event_type': 'oauth_attempt',
                'provider': provider,
                'user_id': user_id,
                'success': success,
                'ip_address': ip_address
            }
        )
    
    def log_token_operation(self, operation: str, token_id: str, user_id: str, provider: str):
        """Log token operation (create, refresh, delete)"""
        self.logger.info(
            f"Token {operation}",
            extra={
                'event_type': f'token_{operation}',
                'token_id': token_id,
                'user_id': user_id,
                'provider': provider
            }
        )
    
    def log_rate_limit(self, endpoint: str, ip_address: str):
        """Log rate limit exceeded"""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                'event_type': 'rate_limit_exceeded',
                'endpoint': endpoint,
                'ip_address': ip_address
            }
        )
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log generic security event"""
        self.logger.warning(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                **details
            }
        )


# Create global security logger instance
security_logger = SecurityLogger()


def get_correlation_id() -> str:
    """Generate correlation ID for request tracking"""
    return str(uuid.uuid4())
