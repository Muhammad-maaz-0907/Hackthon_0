# Agent Skill Base - Gold Tier
# Base class for all agent skills

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Logs')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data')
AUDIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'Audits')

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)


class AgentSkillResponse:
    """Standardized skill response format."""
    
    @staticmethod
    def success(data: Dict[str, Any], skill: str = None) -> Dict:
        return {
            "status": "success",
            "skill": skill,
            "data": data,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, skill: str = None, details: Dict = None) -> Dict:
        return {
            "status": "error",
            "skill": skill,
            "data": None,
            "error": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }


class AuditLogger:
    """Audit logger for skill operations."""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(LOGS_DIR, 'skills_audit.json')
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log(self, skill_name: str, action: str, status: str,
            context: Dict = None, result: Dict = None, error: str = None):
        """Log a skill operation."""
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
                'skill': skill_name,
                'action': action,
                'status': status,
                'context': context,
                'result': result,
                'error': error
            }
            logs.append(entry)
            
            # Keep only last 500 entries
            logs = logs[-500:]
            
            # Save logs
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


class AgentSkill(ABC):
    """
    Base class for all agent skills.
    
    All skills must:
    - Inherit from this class
    - Implement execute(context) method
    - Return structured response
    - Log via audit_logger
    """
    
    def __init__(self, skill_name: str, tier: str = "gold"):
        """
        Initialize agent skill.
        
        Args:
            skill_name: Name identifier for this skill
            tier: Skill tier (silver, gold, etc.)
        """
        self.skill_name = skill_name
        self.tier = tier
        self.audit_logger = AuditLogger()
        logger.info(f"AgentSkill '{skill_name}' ({tier}) initialized")
    
    @abstractmethod
    def execute(self, context: Dict) -> Dict:
        """
        Execute the skill with given context.
        
        Must be implemented by subclasses.
        
        Args:
            context: Context dictionary with parameters
            
        Returns:
            Dict: AgentSkillResponse formatted result
        """
        pass
    
    def validate(self, context: Dict) -> tuple:
        """
        Validate context parameters.
        
        Override in subclasses for custom validation.
        
        Args:
            context: Context dictionary
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        return True, None
    
    def _execute_with_logging(self, context: Dict) -> Dict:
        """Execute skill with audit logging."""
        # Validate
        is_valid, error_msg = self.validate(context)
        if not is_valid:
            error_response = AgentSkillResponse.error(
                error_msg, self.skill_name
            )
            self.audit_logger.log(
                skill_name=self.skill_name,
                action="execute",
                status="validation_failed",
                context=context,
                error=error_msg
            )
            return error_response
        
        # Execute
        try:
            logger.info(f"[{self.skill_name}] Executing with context: {list(context.keys())}")
            
            result = self.execute(context)
            
            # Log success
            self.audit_logger.log(
                skill_name=self.skill_name,
                action="execute",
                status="success",
                context=context,
                result=result
            )
            
            logger.info(f"[{self.skill_name}] Completed successfully")
            return result
            
        except Exception as e:
            # Log error
            error_response = AgentSkillResponse.error(
                str(e), self.skill_name, {"exception_type": type(e).__name__}
            )
            self.audit_logger.log(
                skill_name=self.skill_name,
                action="execute",
                status="error",
                context=context,
                error=str(e)
            )
            logger.error(f"[{self.skill_name}] Execution failed: {e}")
            return error_response
