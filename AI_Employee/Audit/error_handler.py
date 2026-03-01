# Centralized Error Handler - Gold Tier
# Provides unified error processing, retry logic, and graceful degradation
# Ensures system never fully crashes

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from functools import wraps
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/error_handler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'Audits')

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)

# Error log files
ERROR_LOG_FILE = os.path.join(LOGS_DIR, 'errors.json')
CRITICAL_ERROR_LOG = os.path.join(LOGS_DIR, 'critical_errors.json')
ERROR_STATS_FILE = os.path.join(LOGS_DIR, 'error_statistics.json')


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories for classification."""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class ErrorRecord:
    """Represents a recorded error."""
    
    def __init__(self, error: Exception, context: Dict = None):
        self.timestamp = datetime.now()
        self.error_type = type(error).__name__
        self.error_message = str(error)
        self.traceback = traceback.format_exc()
        self.context = context or {}
        self.severity = self._determine_severity(error)
        self.category = self._categorize_error(error)
        self.handled = False
        self.resolved = False
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on type."""
        error_name = type(error).__name__.lower()
        error_msg = str(error).lower()
        
        # Critical errors
        if any(x in error_name for x in ['systemexit', 'keyboardinterrupt']):
            return ErrorSeverity.FATAL
        
        # High severity
        if any(x in error_msg for x in ['authentication', 'permission', 'access denied']):
            return ErrorSeverity.HIGH
        
        if any(x in error_name for x in ['connection', 'timeout', 'network']):
            return ErrorSeverity.HIGH
        
        # Medium severity
        if any(x in error_name for x in ['value', 'type', 'key', 'index']):
            return ErrorSeverity.MEDIUM
        
        if 'rate limit' in error_msg:
            return ErrorSeverity.MEDIUM
        
        # Low severity
        return ErrorSeverity.LOW
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message."""
        error_name = type(error).__name__.lower()
        error_msg = str(error).lower()
        
        if any(x in error_msg for x in ['network', 'connection', 'socket', 'http']):
            return ErrorCategory.NETWORK
        
        if any(x in error_msg for x in ['auth', 'token', 'permission', 'access']):
            return ErrorCategory.AUTHENTICATION
        
        if any(x in error_name for x in ['value', 'type', 'key']):
            return ErrorCategory.VALIDATION
        
        if any(x in error_msg for x in ['config', 'not found', 'missing']):
            return ErrorCategory.CONFIGURATION
        
        if any(x in error_msg for x in ['memory', 'disk', 'resource']):
            return ErrorCategory.RESOURCE
        
        if 'timeout' in error_msg or 'timed out' in error_msg:
            return ErrorCategory.TIMEOUT
        
        if 'rate limit' in error_msg or 'too many requests' in error_msg:
            return ErrorCategory.RATE_LIMIT
        
        return ErrorCategory.UNKNOWN
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'error_type': self.error_type,
            'error_message': self.error_message,
            'traceback': self.traceback,
            'context': self.context,
            'severity': self.severity.value,
            'category': self.category.value,
            'handled': self.handled,
            'resolved': self.resolved
        }


class ErrorStatistics:
    """Track error statistics for analysis."""
    
    def __init__(self, stats_file: str = None):
        self.stats_file = stats_file or ERROR_STATS_FILE
        self._load_stats()
    
    def _load_stats(self):
        """Load existing statistics."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            else:
                self.stats = self._empty_stats()
        except Exception as e:
            logger.error(f"Failed to load error stats: {e}")
            self.stats = self._empty_stats()
    
    def _empty_stats(self) -> Dict:
        """Create empty statistics structure."""
        return {
            'total_errors': 0,
            'by_severity': {
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0,
                'fatal': 0
            },
            'by_category': {},
            'by_hour': {},
            'by_source': {},
            'retry_successes': 0,
            'retry_failures': 0,
            'last_updated': None,
            'system_uptime': datetime.now().isoformat()
        }
    
    def record(self, error_record: ErrorRecord, source: str = None):
        """Record an error in statistics."""
        self.stats['total_errors'] += 1
        
        # By severity
        severity = error_record.severity.value
        if severity in self.stats['by_severity']:
            self.stats['by_severity'][severity] += 1
        
        # By category
        category = error_record.category.value
        if category not in self.stats['by_category']:
            self.stats['by_category'][category] = 0
        self.stats['by_category'][category] += 1
        
        # By hour
        hour = datetime.now().strftime('%Y-%m-%d %H:00')
        if hour not in self.stats['by_hour']:
            self.stats['by_hour'][hour] = 0
        self.stats['by_hour'][hour] += 1
        
        # By source
        if source:
            if source not in self.stats['by_source']:
                self.stats['by_source'][source] = 0
            self.stats['by_source'][source] += 1
        
        self.stats['last_updated'] = datetime.now().isoformat()
        self._save_stats()
    
    def record_retry_success(self):
        """Record successful retry."""
        self.stats['retry_successes'] += 1
        self._save_stats()
    
    def record_retry_failure(self):
        """Record failed retry."""
        self.stats['retry_failures'] += 1
        self._save_stats()
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save error stats: {e}")
    
    def get_summary(self) -> Dict:
        """Get error statistics summary."""
        return {
            'total_errors': self.stats['total_errors'],
            'retry_success_rate': (
                self.stats['retry_successes'] / 
                (self.stats['retry_successes'] + self.stats['retry_failures']) * 100
                if (self.stats['retry_successes'] + self.stats['retry_failures']) > 0
                else 0
            ),
            'top_categories': sorted(
                self.stats['by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'recent_hours': dict(list(self.stats['by_hour'].items())[-24:])
        }


class CentralErrorHandler:
    """
    Centralized error handler for the AI Employee system.
    
    Features:
    - Central error processing
    - Retry wrapper with exponential backoff
    - Structured error logging
    - Graceful degradation
    - System never fully crashes
    - Integration with audit logger
    """
    
    def __init__(self, component_name: str = "system"):
        self.component_name = component_name
        self.error_log = []
        self.critical_errors = []
        self.statistics = ErrorStatistics()
        self.max_log_size = 1000
        self._load_logs()
        
        logger.info(f"CentralErrorHandler initialized for: {component_name}")
    
    def _load_logs(self):
        """Load existing error logs."""
        try:
            if os.path.exists(ERROR_LOG_FILE):
                with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
                    self.error_log = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load error logs: {e}")
            self.error_log = []
        
        try:
            if os.path.exists(CRITICAL_ERROR_LOG):
                with open(CRITICAL_ERROR_LOG, 'r', encoding='utf-8') as f:
                    self.critical_errors = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load critical errors: {e}")
            self.critical_errors = []
    
    def _save_logs(self):
        """Save error logs to files."""
        try:
            # Trim logs to max size
            self.error_log = self.error_log[-self.max_log_size:]
            self.critical_errors = self.critical_errors[-100:]
            
            with open(ERROR_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.error_log, f, indent=2, default=str)
            
            with open(CRITICAL_ERROR_LOG, 'w', encoding='utf-8') as f:
                json.dump(self.critical_errors, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save error logs: {e}")
    
    def handle(self, error: Exception, context: Dict = None, 
               raise_error: bool = False) -> Dict:
        """
        Handle an error centrally.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            raise_error: Whether to re-raise the error
            
        Returns:
            Dict: Error handling result
        """
        # Create error record
        error_record = ErrorRecord(error, context)
        error_record.handled = True
        
        # Log the error
        self._log_error(error_record)
        
        # Update statistics
        self.statistics.record(error_record, self.component_name)
        
        # Determine action based on severity
        result = self._determine_action(error_record)
        
        # Log to audit
        self._audit_log(error_record, result)
        
        # Save logs
        self._save_logs()
        
        # Re-raise if requested and not fatal
        if raise_error and error_record.severity != ErrorSeverity.FATAL:
            raise error
        
        return result
    
    def _log_error(self, error_record: ErrorRecord):
        """Log error to appropriate log."""
        error_dict = error_record.to_dict()
        
        # Add to main log
        self.error_log.append(error_dict)
        
        # Also log to critical if high severity
        if error_record.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            self.critical_errors.append(error_dict)
            logger.critical(
                f"[{error_record.severity.value.upper()}] "
                f"{error_record.error_type}: {error_record.error_message}"
            )
        elif error_record.severity == ErrorSeverity.MEDIUM:
            logger.warning(
                f"[{error_record.severity.value.upper()}] "
                f"{error_record.error_type}: {error_record.error_message}"
            )
        else:
            logger.info(
                f"[{error_record.severity.value.upper()}] "
                f"{error_record.error_type}: {error_record.error_message}"
            )
    
    def _determine_action(self, error_record: ErrorRecord) -> Dict:
        """Determine action to take based on error."""
        severity = error_record.severity
        
        if severity == ErrorSeverity.FATAL:
            return {
                'action': 'shutdown_gracefully',
                'message': 'Fatal error detected. Initiating graceful shutdown.',
                'recoverable': False
            }
        
        elif severity == ErrorSeverity.CRITICAL:
            return {
                'action': 'alert_and_retry',
                'message': 'Critical error. Alerting administrators and retrying.',
                'recoverable': True,
                'retry_recommended': True,
                'max_retries': 3
            }
        
        elif severity == ErrorSeverity.HIGH:
            return {
                'action': 'retry_with_backoff',
                'message': 'High severity error. Retrying with exponential backoff.',
                'recoverable': True,
                'retry_recommended': True,
                'max_retries': 3
            }
        
        elif severity == ErrorSeverity.MEDIUM:
            return {
                'action': 'log_and_continue',
                'message': 'Medium severity error. Logged and continuing.',
                'recoverable': True,
                'retry_recommended': False
            }
        
        else:  # LOW
            return {
                'action': 'log_only',
                'message': 'Low severity error. Logged for analysis.',
                'recoverable': True,
                'retry_recommended': False
            }
    
    def _audit_log(self, error_record: ErrorRecord, result: Dict):
        """Log error to audit trail."""
        try:
            audit_entry = {
                'timestamp': error_record.timestamp.isoformat(),
                'component': self.component_name,
                'error_type': error_record.error_type,
                'severity': error_record.severity.value,
                'category': error_record.category.value,
                'action_taken': result.get('action'),
                'recoverable': result.get('recoverable')
            }
            
            # Append to skills audit log for centralized viewing
            skills_audit_file = os.path.join(LOGS_DIR, 'error_audit.json')
            audit_logs = []
            
            if os.path.exists(skills_audit_file):
                with open(skills_audit_file, 'r', encoding='utf-8') as f:
                    try:
                        audit_logs = json.load(f)
                    except json.JSONDecodeError:
                        audit_logs = []
            
            audit_logs.append(audit_entry)
            audit_logs = audit_logs[-500:]  # Keep last 500
            
            with open(skills_audit_file, 'w', encoding='utf-8') as f:
                json.dump(audit_logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def retry_with_backoff(self, func: Callable, max_retries: int = 3,
                           base_delay: float = 1.0, max_delay: float = 60.0,
                           exceptions: tuple = None) -> Callable:
        """
        Decorator for retry with exponential backoff.
        
        Args:
            func: Function to wrap
            max_retries: Maximum retry attempts
            base_delay: Base delay between retries (seconds)
            max_delay: Maximum delay between retries
            exceptions: Tuple of exceptions to catch (None = all)
            
        Returns:
            Wrapped function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_error = e
                    
                    # Check if we should handle this exception
                    if exceptions and not isinstance(e, exceptions):
                        raise
                    
                    # Handle the error
                    context = {
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    }
                    
                    result = self.handle(e, context)
                    
                    # Check if we should retry
                    if attempt < max_retries and result.get('retry_recommended', False):
                        logger.info(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)  # Exponential backoff
                    else:
                        self.statistics.record_retry_failure()
                        break
            
            # All retries exhausted
            if last_error:
                self.statistics.record_retry_failure()
                # Return graceful degradation response
                return self._graceful_degradation(func.__name__, last_error)
            
            return None
        
        return wrapper
    
    def _graceful_degradation(self, function_name: str, error: Exception) -> Dict:
        """
        Provide graceful degradation when function fails.
        
        Returns safe default response instead of crashing.
        """
        logger.warning(f"Graceful degradation for {function_name}: {error}")
        
        # Return safe default based on function type
        if 'get' in function_name.lower() or 'fetch' in function_name.lower():
            return {'status': 'degraded', 'data': [], 'error': str(error)}
        
        if 'process' in function_name.lower() or 'execute' in function_name.lower():
            return {'status': 'degraded', 'processed': False, 'error': str(error)}
        
        if 'send' in function_name.lower() or 'post' in function_name.lower():
            return {'status': 'degraded', 'sent': False, 'error': str(error)}
        
        # Generic fallback
        return {
            'status': 'degraded',
            'function': function_name,
            'error': str(error),
            'graceful_degradation': True
        }
    
    def safe_execute(self, func: Callable, default: Any = None,
                     catch_exceptions: tuple = None) -> Callable:
        """
        Decorator for safe execution that never raises.
        
        Args:
            func: Function to wrap
            default: Default return value on error
            catch_exceptions: Exceptions to catch (None = all)
            
        Returns:
            Wrapped function that never raises
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Check if we should catch this exception
                if catch_exceptions and not isinstance(e, catch_exceptions):
                    raise
                
                # Handle error gracefully
                context = {
                    'function': func.__name__,
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                }
                
                self.handle(e, context)
                
                # Return default or graceful degradation
                return default if default is not None else self._graceful_degradation(
                    func.__name__, e
                )
        
        return wrapper
    
    def get_error_summary(self) -> Dict:
        """Get summary of recent errors."""
        return {
            'component': self.component_name,
            'statistics': self.statistics.get_summary(),
            'recent_errors': self.error_log[-10:],
            'critical_count': len(self.critical_errors),
            'system_status': self._determine_system_status()
        }
    
    def _determine_system_status(self) -> str:
        """Determine overall system health status."""
        stats = self.statistics.get_summary()
        
        # Check for critical errors in recent history
        recent_critical = sum(
            1 for e in self.error_log[-50:]
            if e.get('severity') in ['critical', 'fatal']
        )
        
        if recent_critical > 5:
            return 'degraded'
        
        if stats['total_errors'] > 100:
            return 'warning'
        
        # Check retry success rate
        if stats['retry_success_rate'] < 50:
            return 'warning'
        
        return 'healthy'
    
    def clear_resolved(self, older_than_hours: int = 24):
        """Mark old errors as resolved."""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        
        for error in self.error_log:
            error_time = datetime.fromisoformat(error.get('timestamp', '2000-01-01'))
            if error_time < cutoff and not error.get('resolved'):
                error['resolved'] = True
        
        self._save_logs()
        logger.info(f"Marked old errors as resolved (older than {older_than_hours}h)")


# Global error handler instance
_global_handler = None

def get_error_handler(component_name: str = "system") -> CentralErrorHandler:
    """Get or create global error handler."""
    global _global_handler
    if _global_handler is None:
        _global_handler = CentralErrorHandler(component_name)
    return _global_handler


# Convenience decorators
def retry(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator with default settings."""
    handler = get_error_handler()
    return handler.retry_with_backoff(max_retries=max_retries, base_delay=base_delay)


def safe(default=None):
    """Safe execute decorator with default return."""
    handler = get_error_handler()
    return handler.safe_execute(default=default)


# Context manager for error handling
class ErrorContext:
    """Context manager for structured error handling."""
    
    def __init__(self, operation: str, handler: CentralErrorHandler = None):
        self.operation = operation
        self.handler = handler or get_error_handler()
        self.error = None
        self.result = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            context = {
                'operation': self.operation,
                'exception_type': exc_type.__name__
            }
            result = self.handler.handle(exc_val, context)
            
            # Don't suppress fatal errors
            if result.get('action') == 'shutdown_gracefully':
                return False
            
            # Suppress other errors (handled gracefully)
            return True
        
        return False


# Main entry point for testing
if __name__ == '__main__':
    print("=" * 60)
    print("Central Error Handler - Gold Tier")
    print("=" * 60)
    
    # Create handler
    handler = CentralErrorHandler("test_component")
    
    # Test 1: Handle a simple error
    print("\n1. Testing error handling:")
    try:
        raise ValueError("Test error for demonstration")
    except Exception as e:
        result = handler.handle(e, {'test': 'value'})
        print(f"   Result: {result}")
    
    # Test 2: Retry decorator
    print("\n2. Testing retry with backoff:")
    attempt_count = 0
    
    def flaky_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Simulated failure {attempt_count}")
        return "Success!"
    
    # Wrap with retry
    wrapped_func = handler.retry_with_backoff(flaky_function, max_retries=3, base_delay=0.5)
    result = wrapped_func()
    print(f"   Result after retries: {result}")
    
    # Test 3: Safe execute decorator
    print("\n3. Testing safe execution:")
    
    def failing_function():
        raise RuntimeError("Always fails")
    
    # Wrap with safe execute
    safe_func = handler.safe_execute(failing_function, default={'status': 'default'})
    result = safe_func()
    print(f"   Safe result: {result}")
    
    # Test 4: Error context manager
    print("\n4. Testing error context:")
    with ErrorContext("test_operation", handler) as ctx:
        raise KeyError("Simulated key error")
    
    print(f"   Error handled: {ctx.error is not None}")
    
    # Test 5: Get summary
    print("\n5. Error summary:")
    summary = handler.get_error_summary()
    print(f"   System status: {summary['system_status']}")
    print(f"   Total errors: {summary['statistics']['total_errors']}")
    print(f"   Critical count: {summary['critical_count']}")
    
    print("\n" + "=" * 60)
    print("Error handler test complete!")
    print("=" * 60)
