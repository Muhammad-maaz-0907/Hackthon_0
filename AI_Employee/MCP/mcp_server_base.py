# MCP Server Base - Gold Tier Core Framework
# Provides base class for all MCP servers with standardized error handling,
# retry logic, audit logging, and graceful degradation.

import os
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
ENV_FILE = os.path.join(os.path.dirname(__file__), '..', '.env')

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)


class MCPResponse:
    """
    Standardized MCP response format.
    
    All MCP servers must return responses in this format.
    """
    
    @staticmethod
    def success(data: Dict[str, Any], action: str = None) -> Dict:
        """Create a success response."""
        return {
            "status": "success",
            "data": data,
            "error": None,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, action: str = None, details: Dict = None) -> Dict:
        """Create an error response."""
        return {
            "status": "error",
            "data": None,
            "error": message,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }


class MCPAuditLogger:
    """
    Audit logger for MCP operations.
    Logs all actions to a centralized JSON log file.
    """
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(LOGS_DIR, 'mcp_audit.json')
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log(self, server_name: str, action: str, status: str, 
            payload: Dict = None, result: Dict = None, error: str = None):
        """Log an MCP operation."""
        try:
            # Load existing logs
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            # Create new entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                'server': server_name,
                'action': action,
                'status': status,
                'payload': payload,
                'result': result,
                'error': error
            }
            logs.append(entry)
            
            # Keep only last 1000 entries
            logs = logs[-1000:]
            
            # Save logs
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, default=str)
            
            logger.debug(f"Audit log entry created: {server_name}/{action}")
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """Get recent audit log entries."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return logs[-limit:]
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            return []


class MCPServerBase(ABC):
    """
    Base class for all MCP (Model Context Protocol) servers.
    
    Provides:
    - Connection management
    - Standardized action execution
    - Error handling with graceful degradation
    - Retry logic with exponential backoff
    - Audit logging
    
    Usage:
        class MyMCPServer(MCPServerBase):
            def __init__(self):
                super().__init__("my_server")
            
            def _execute_action(self, action: str, payload: Dict) -> Dict:
                # Implement action routing
                if action == "my_action":
                    return self._handle_my_action(payload)
                return MCPResponse.error(f"Unknown action: {action}", action)
    """
    
    def __init__(self, server_name: str, max_retries: int = 3, 
                 retry_delay: float = 1.0, enable_audit: bool = True):
        """
        Initialize MCP server base.
        
        Args:
            server_name: Name identifier for this MCP server
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Base delay between retries (seconds)
            enable_audit: Enable audit logging
        """
        self.server_name = server_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_audit = enable_audit
        self.connected = False
        self.audit_logger = MCPAuditLogger() if enable_audit else None
        
        # Load environment variables
        self._load_env()
        
        logger.info(f"MCP Server '{server_name}' initialized")
    
    def _load_env(self):
        """Load environment variables from .env file."""
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Override config if specified in env
                        if key == 'MCP_MAX_RETRIES':
                            self.max_retries = int(value)
                        elif key == 'MCP_RETRY_DELAY':
                            self.retry_delay = float(value)
    
    @abstractmethod
    def _execute_action(self, action: str, payload: Dict) -> Dict:
        """
        Execute an action specific to this server.
        
        Must be implemented by subclasses.
        
        Args:
            action: Action name to execute
            payload: Action parameters
            
        Returns:
            Dict: MCPResponse formatted result
        """
        pass
    
    def connect(self, **kwargs) -> Dict:
        """
        Establish connection to the service.
        
        Override in subclasses if connection logic is needed.
        
        Returns:
            Dict: Connection status
        """
        try:
            logger.info(f"[{self.server_name}] Connecting...")
            
            # Perform connection logic (override in subclass)
            self.connected = True
            
            result = {
                "server": self.server_name,
                "status": "connected",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[{self.server_name}] Connected successfully")
            return MCPResponse.success(result, "connect")
            
        except Exception as e:
            self.connected = False
            error_response = self.handle_error(e, "connect")
            logger.error(f"[{self.server_name}] Connection failed: {e}")
            return error_response
    
    def disconnect(self) -> Dict:
        """
        Close connection to the service.
        
        Override in subclasses if cleanup is needed.
        
        Returns:
            Dict: Disconnection status
        """
        try:
            logger.info(f"[{self.server_name}] Disconnecting...")
            
            # Perform cleanup logic (override in subclass)
            self.connected = False
            
            result = {
                "server": self.server_name,
                "status": "disconnected",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[{self.server_name}] Disconnected successfully")
            return MCPResponse.success(result, "disconnect")
            
        except Exception as e:
            error_response = self.handle_error(e, "disconnect")
            logger.error(f"[{self.server_name}] Disconnection failed: {e}")
            return error_response
    
    def execute(self, action: str, payload: Dict = None) -> Dict:
        """
        Execute an action with full error handling and audit logging.
        
        This is the main entry point for all MCP operations.
        
        Args:
            action: Action name to execute
            payload: Action parameters
            
        Returns:
            Dict: MCPResponse formatted result
        """
        payload = payload or {}
        start_time = time.time()
        
        # Log action start
        logger.info(f"[{self.server_name}] Executing action: {action}")
        
        if self.audit_logger:
            self.audit_logger.log(
                server_name=self.server_name,
                action=action,
                status="started",
                payload=payload
            )
        
        try:
            # Execute with retry logic
            result = self.retry_logic(
                lambda: self._execute_action(action, payload),
                action=action,
                payload=payload
            )
            
            # Log success
            elapsed = time.time() - start_time
            logger.info(f"[{self.server_name}] Action '{action}' completed in {elapsed:.2f}s")
            
            if self.audit_logger:
                self.audit_logger.log(
                    server_name=self.server_name,
                    action=action,
                    status="success",
                    payload=payload,
                    result=result
                )
            
            return result
            
        except Exception as e:
            # Handle error with graceful degradation
            error_response = self.handle_error(e, action)
            
            elapsed = time.time() - start_time
            logger.error(f"[{self.server_name}] Action '{action}' failed after {elapsed:.2f}s: {e}")
            
            if self.audit_logger:
                self.audit_logger.log(
                    server_name=self.server_name,
                    action=action,
                    status="error",
                    payload=payload,
                    error=str(e)
                )
            
            return error_response
    
    def retry_logic(self, func: Callable, action: str, 
                    payload: Dict = None, max_retries: int = None,
                    retry_delay: float = None) -> Dict:
        """
        Execute function with retry logic and exponential backoff.
        
        Args:
            func: Function to execute
            action: Action name for logging
            payload: Payload to pass to function
            max_retries: Override default max retries
            retry_delay: Override default retry delay
            
        Returns:
            Dict: MCPResponse formatted result
        """
        max_retries = max_retries or self.max_retries
        retry_delay = retry_delay or self.retry_delay
        payload = payload or {}
        
        last_error = None
        last_traceback = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.debug(f"[{self.server_name}] Attempt {attempt}/{max_retries} for action: {action}")
                
                result = func()
                
                # Check if result indicates failure
                if isinstance(result, dict) and result.get('status') == 'error':
                    raise MCPExecutionError(result.get('error', 'Unknown error'))
                
                return result
                
            except Exception as e:
                last_error = e
                last_traceback = traceback.format_exc()
                
                logger.warning(
                    f"[{self.server_name}] Attempt {attempt}/{max_retries} failed: {e}"
                )
                
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = retry_delay * (2 ** (attempt - 1))
                    logger.info(f"[{self.server_name}] Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
        
        # All retries exhausted
        error_msg = f"All {max_retries} retries failed"
        if last_error:
            error_msg += f": {str(last_error)}"
        
        logger.error(f"[{self.server_name}] {error_msg}")
        logger.debug(f"Traceback: {last_traceback}")
        
        return self.handle_error(last_error, action, {
            "attempts": max_retries,
            "traceback": last_traceback
        })
    
    def handle_error(self, error: Exception, action: str, 
                     details: Dict = None) -> Dict:
        """
        Handle errors with graceful degradation.
        
        Args:
            error: The exception that occurred
            action: The action that failed
            details: Additional error details
            
        Returns:
            Dict: MCPResponse formatted error response
        """
        error_details = details or {}
        
        # Categorize error
        error_type = type(error).__name__
        error_message = str(error)
        
        # Add context
        error_details.update({
            "error_type": error_type,
            "server": self.server_name,
            "action": action
        })
        
        # Graceful degradation - return structured error instead of crashing
        logger.error(f"[{self.server_name}] Error handling: {error_type}: {error_message}")
        
        return MCPResponse.error(
            message=error_message,
            action=action,
            details=error_details
        )
    
    def health_check(self) -> Dict:
        """
        Perform a health check on the server.
        
        Returns:
            Dict: Health status
        """
        try:
            health_status = {
                "server": self.server_name,
                "status": "healthy" if self.connected else "disconnected",
                "connected": self.connected,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "audit_enabled": self.enable_audit,
                "timestamp": datetime.now().isoformat()
            }
            
            return MCPResponse.success(health_status, "health_check")
            
        except Exception as e:
            return self.handle_error(e, "health_check", {
                "status": "unhealthy"
            })
    
    def get_stats(self) -> Dict:
        """
        Get server statistics.
        
        Override in subclasses to provide custom stats.
        
        Returns:
            Dict: Server statistics
        """
        stats = {
            "server": self.server_name,
            "connected": self.connected,
            "config": {
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "audit_enabled": self.enable_audit
            }
        }
        
        return MCPResponse.success(stats, "get_stats")


class MCPExecutionError(Exception):
    """Custom exception for MCP execution failures."""
    pass


class MCPRegistry:
    """
    Registry for managing multiple MCP servers.
    Provides graceful degradation when servers fail.
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerBase] = {}
        self.logger = logging.getLogger(__name__)
    
    def register(self, server: MCPServerBase):
        """Register an MCP server."""
        self.servers[server.server_name] = server
        self.logger.info(f"MCP Registry: Registered '{server.server_name}'")
    
    def unregister(self, server_name: str):
        """Unregister an MCP server."""
        if server_name in self.servers:
            del self.servers[server_name]
            self.logger.info(f"MCP Registry: Unregistered '{server_name}'")
    
    def execute(self, server_name: str, action: str, 
                payload: Dict = None) -> Dict:
        """
        Execute an action on a specific server with graceful degradation.
        
        Args:
            server_name: Name of the server to execute on
            action: Action to execute
            payload: Action parameters
            
        Returns:
            Dict: MCPResponse formatted result
        """
        if server_name not in self.servers:
            return MCPResponse.error(
                f"Server '{server_name}' not found",
                action=action,
                details={"available_servers": list(self.servers.keys())}
            )
        
        server = self.servers[server_name]
        
        try:
            return server.execute(action, payload)
        except Exception as e:
            self.logger.error(
                f"MCP Registry: Server '{server_name}' failed: {e}"
            )
            return MCPResponse.error(
                f"Server '{server_name}' unavailable: {str(e)}",
                action=action,
                details={
                    "graceful_degradation": True,
                    "fallback_available": len(self.servers) > 1
                }
            )
    
    def execute_fallback(self, actions: list, 
                         fallback_order: list = None) -> Dict:
        """
        Execute actions with automatic fallback to alternative servers.
        
        Args:
            actions: List of (server_name, action, payload) tuples
            fallback_order: Preferred server order for fallback
            
        Returns:
            Dict: Results from all actions
        """
        results = {}
        fallback_order = fallback_order or list(self.servers.keys())
        
        for server_name, action, payload in actions:
            # Try primary server
            if server_name in self.servers:
                result = self.servers[server_name].execute(action, payload)
                
                # If failed, try fallback servers
                if result.get('status') == 'error':
                    for fallback_server in fallback_order:
                        if fallback_server != server_name:
                            self.logger.info(
                                f"Attempting fallback to '{fallback_server}'"
                            )
                            result = self.servers[fallback_server].execute(
                                action, payload
                            )
                            if result.get('status') == 'success':
                                break
                
                results[f"{server_name}/{action}"] = result
            else:
                results[f"{server_name}/{action}"] = MCPResponse.error(
                    f"Server '{server_name}' not available",
                    action=action
                )
        
        return MCPResponse.success(results, "execute_fallback")
    
    def health_check_all(self) -> Dict:
        """
        Check health of all registered servers.
        
        Returns:
            Dict: Health status of all servers
        """
        health_status = {}
        
        for name, server in self.servers.items():
            try:
                health_status[name] = server.health_check()
            except Exception as e:
                health_status[name] = MCPResponse.error(
                    f"Health check failed: {str(e)}",
                    action="health_check"
                )
        
        return MCPResponse.success({
            "servers": health_status,
            "total": len(self.servers),
            "healthy": sum(1 for s in health_status.values() 
                          if s.get('status') == 'success')
        }, "health_check_all")


# Example usage and testing
if __name__ == '__main__':
    print("MCP Server Base - Gold Tier Framework")
    print("=" * 50)
    
    # Example: Create a test server
    class TestMCPServer(MCPServerBase):
        def __init__(self):
            super().__init__("test_server")
        
        def _execute_action(self, action: str, payload: Dict) -> Dict:
            if action == "echo":
                return MCPResponse.success({
                    "echo": payload,
                    "message": "Echo successful"
                }, action)
            elif action == "fail":
                raise MCPExecutionError("Intentional failure for testing")
            else:
                return MCPResponse.error(f"Unknown action: {action}", action)
    
    # Test the server
    server = TestMCPServer()
    
    print("\n1. Testing connection:")
    result = server.connect()
    print(json.dumps(result, indent=2))
    
    print("\n2. Testing echo action:")
    result = server.execute("echo", {"message": "Hello MCP"})
    print(json.dumps(result, indent=2))
    
    print("\n3. Testing error handling:")
    result = server.execute("fail", {})
    print(json.dumps(result, indent=2))
    
    print("\n4. Testing health check:")
    result = server.health_check()
    print(json.dumps(result, indent=2))
    
    print("\n5. Testing registry:")
    registry = MCPRegistry()
    registry.register(server)
    
    result = registry.health_check_all()
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 50)
    print("MCP Server Base framework test complete!")
