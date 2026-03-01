# RALPH Loop - Autonomous Decision Engine
# Ralph: Recursive Autonomous Learning & Processing Handler
# 
# Continuously monitors tasks, routes them to appropriate skills,
# executes with retry logic, and logs all actions.

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/ralph_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
CORE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(CORE_DIR, '..')
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'Logs')
NEEDS_ACTION_DIR = os.path.join(PROJECT_ROOT, 'Needs_Action')
AUDIT_DIR = os.path.join(PROJECT_ROOT, 'Audits')
SKILLS_DIR = os.path.join(PROJECT_ROOT, 'Skills')

STATE_STORE_FILE = os.path.join(DATA_DIR, 'state_store.json')
DECISION_LOG_FILE = os.path.join(LOGS_DIR, 'ralph_decisions.json')
TASK_HISTORY_FILE = os.path.join(LOGS_DIR, 'ralph_task_history.json')

# Ensure directories exist
for dir_path in [DATA_DIR, LOGS_DIR, NEEDS_ACTION_DIR, AUDIT_DIR]:
    os.makedirs(dir_path, exist_ok=True)


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKLOG = 5


class TaskStatus(Enum):
    """Task status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DecisionLogger:
    """Log all RALPH decisions for audit and learning."""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or DECISION_LOG_FILE
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log_decision(self, task_id: str, decision: Dict):
        """Log a decision made by RALPH."""
        try:
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'task_id': task_id,
                **decision
            }
            logs.append(entry)
            
            # Keep last 500 decisions
            logs = logs[-500:]
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, default=str)
            
            logger.debug(f"Logged decision for task {task_id}")
            
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent decisions."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return logs[-limit:]
        except Exception as e:
            logger.error(f"Failed to read decisions: {e}")
            return []


class TaskHistory:
    """Track task execution history."""
    
    def __init__(self, history_file: str = None):
        self.history_file = history_file or TASK_HISTORY_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        """Create history file if it doesn't exist."""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def record(self, task: Dict, result: Dict, duration: float):
        """Record task execution."""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        history = []
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'task': task,
                'result': result,
                'duration_seconds': duration
            }
            history.append(entry)
            
            # Keep last 1000 tasks
            history = history[-1000:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to record task history: {e}")
    
    def get_success_rate(self, skill_name: str = None) -> float:
        """Calculate success rate for a skill."""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                return 0.0
            
            if skill_name:
                relevant = [h for h in history if h.get('task', {}).get('skill') == skill_name]
            else:
                relevant = history
            
            if not relevant:
                return 0.0
            
            successes = sum(1 for h in relevant if h.get('result', {}).get('status') == 'success')
            return successes / len(relevant)
            
        except Exception as e:
            logger.error(f"Failed to calculate success rate: {e}")
            return 0.0


class StateStore:
    """Manage task state in state_store.json."""
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or STATE_STORE_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        """Create state file if it doesn't exist."""
        if not os.path.exists(self.state_file):
            initial_state = {
                'tasks': [],
                'last_updated': datetime.now().isoformat(),
                'system_status': 'running'
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(initial_state, f, indent=2)
    
    def read(self) -> Dict:
        """Read current state."""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Ensure tasks list exists
            if 'tasks' not in state:
                state['tasks'] = []
            
            return state
        except Exception as e:
            logger.error(f"Failed to read state: {e}")
            return {'tasks': [], 'last_updated': datetime.now().isoformat()}
    
    def write(self, state: Dict):
        """Write updated state."""
        try:
            state['last_updated'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
            logger.debug("State updated")
        except Exception as e:
            logger.error(f"Failed to write state: {e}")
    
    def add_task(self, task: Dict) -> str:
        """Add a new task to the state store."""
        try:
            state = self.read()
            
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(state['tasks'])}"
            task['id'] = task_id
            task['status'] = TaskStatus.PENDING.value
            task['created_at'] = datetime.now().isoformat()
            task['retry_count'] = 0
            task['max_retries'] = 3
            
            state['tasks'].append(task)
            self.write(state)
            
            logger.info(f"Added task: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return None
    
    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update a task's status or data."""
        try:
            state = self.read()
            
            for task in state['tasks']:
                if task.get('id') == task_id:
                    task.update(updates)
                    self.write(state)
                    logger.debug(f"Updated task: {task_id}")
                    return True
            
            logger.warning(f"Task not found: {task_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks sorted by priority."""
        try:
            state = self.read()
            pending = [
                t for t in state['tasks']
                if t.get('status') == TaskStatus.PENDING.value
            ]
            
            # Sort by priority (lower number = higher priority)
            pending.sort(key=lambda x: x.get('priority', 3))
            
            return pending
            
        except Exception as e:
            logger.error(f"Failed to get pending tasks: {e}")
            return []
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID."""
        try:
            state = self.read()
            for task in state['tasks']:
                if task.get('id') == task_id:
                    return task
            return None
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None


class TaskRouter:
    """Route tasks to appropriate skills based on content and context."""
    
    def __init__(self):
        self.decision_logger = DecisionLogger()
        
        # Routing rules
        self.routing_rules = {
            'marketing': {
                'keywords': ['post', 'social', 'marketing', 'tweet', 'linkedin', 'facebook', 'instagram'],
                'skill': 'marketing_skill',
                'default_action': 'post_all'
            },
            'email_response': {
                'keywords': ['email', 'reply', 'respond', 'send email'],
                'skill': 'operations_skill',
                'default_action': 'process_gmail'
            },
            'whatsapp_response': {
                'keywords': ['whatsapp', 'message', 'chat'],
                'skill': 'operations_skill',
                'default_action': 'process_whatsapp'
            },
            'briefing': {
                'keywords': ['briefing', 'report', 'summary', 'ceo'],
                'skill': 'ceo_briefing_skill',
                'default_action': 'generate'
            },
            'content_generation': {
                'keywords': ['generate', 'create content', 'write', 'draft'],
                'skill': 'marketing_skill',
                'default_action': 'generate_content'
            }
        }
    
    def route(self, task: Dict) -> Tuple[str, str, Dict]:
        """
        Route a task to the appropriate skill.
        
        Returns:
            Tuple of (skill_name, action, skill_context)
        """
        task_id = task.get('id', 'unknown')
        description = task.get('description', '').lower()
        metadata = task.get('metadata', {})
        
        # Score each routing rule
        best_match = None
        best_score = 0
        
        for rule_name, rule in self.routing_rules.items():
            score = sum(1 for kw in rule['keywords'] if kw in description)
            if score > best_score:
                best_score = score
                best_match = rule
        
        # Default routing if no match
        if not best_match or best_score == 0:
            # Check for explicit skill in metadata
            if 'skill' in metadata:
                best_match = {
                    'skill': metadata['skill'],
                    'default_action': metadata.get('action', 'execute')
                }
            else:
                # Default to operations for unknown tasks
                best_match = {
                    'skill': 'operations_skill',
                    'default_action': 'process_inbound'
                }
        
        # Build skill context
        skill_context = {
            'action': best_match['default_action'],
            'task_id': task_id,
            'source': task.get('source', 'ralph_loop')
        }
        
        # Add action-specific parameters
        skill_context.update(self._build_action_params(task, best_match['default_action']))
        
        # Log routing decision
        self.decision_logger.log_decision(task_id, {
            'decision_type': 'routing',
            'routed_to': best_match['skill'],
            'action': best_match['default_action'],
            'confidence': best_score,
            'description': description[:100]
        })
        
        logger.info(f"Routed task {task_id} to {best_match['skill']}::{best_match['default_action']}")
        
        return best_match['skill'], best_match['default_action'], skill_context
    
    def _build_action_params(self, task: Dict, action: str) -> Dict:
        """Build parameters for specific actions."""
        params = {}
        metadata = task.get('metadata', {})
        description = task.get('description', '')
        
        if action == 'post_all' or action == 'post':
            params['content'] = metadata.get('content', description)
            params['image_url'] = metadata.get('image_url')
        
        elif action == 'generate_content':
            params['topic'] = metadata.get('topic', self._extract_topic(description))
            params['count'] = metadata.get('count', 5)
        
        elif action == 'process_gmail':
            params['max_results'] = metadata.get('max_results', 10)
            params['auto_respond'] = metadata.get('auto_respond', False)
        
        elif action == 'generate':
            params['period'] = metadata.get('period', 7)
            params['include_recommendations'] = True
        
        return params
    
    def _extract_topic(self, text: str) -> str:
        """Extract topic from text."""
        # Simple keyword extraction
        keywords = ['AI', 'automation', 'marketing', 'product', 'update', 'news']
        for kw in keywords:
            if kw.lower() in text.lower():
                return kw
        return 'general'


class SkillExecutor:
    """Execute skills with error handling and retry logic."""
    
    def __init__(self):
        self.skill_cache = {}
        self.decision_logger = DecisionLogger()
        self.task_history = TaskHistory()
    
    def execute(self, skill_name: str, context: Dict, max_retries: int = 3) -> Dict:
        """
        Execute a skill with retry logic.
        
        Args:
            skill_name: Name of the skill to execute
            context: Skill context/parameters
            max_retries: Maximum retry attempts
            
        Returns:
            Dict: Execution result
        """
        start_time = time.time()
        task_id = context.get('task_id', 'unknown')
        
        logger.info(f"Executing {skill_name} with action: {context.get('action')}")
        
        last_error = None
        result = None
        
        for attempt in range(1, max_retries + 1):
            try:
                # Get skill instance
                skill = self._get_skill(skill_name)
                
                if not skill:
                    return {
                        'status': 'error',
                        'error': f"Skill not found: {skill_name}",
                        'skill': skill_name
                    }
                
                # Execute skill
                result = skill._execute_with_logging(context)
                
                # Check if successful
                if result.get('status') == 'success':
                    duration = time.time() - start_time
                    
                    # Log success
                    self.decision_logger.log_decision(task_id, {
                        'decision_type': 'execution',
                        'status': 'success',
                        'skill': skill_name,
                        'attempt': attempt,
                        'duration': duration
                    })
                    
                    self.task_history.record(
                        {'skill': skill_name, 'context': context},
                        result,
                        duration
                    )
                    
                    logger.info(f"Skill {skill_name} completed successfully in {duration:.2f}s")
                    return result
                
                # If failed, prepare for retry
                last_error = result.get('error', 'Unknown error')
                logger.warning(f"Skill {skill_name} failed (attempt {attempt}/{max_retries}): {last_error}")
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Skill {skill_name} exception (attempt {attempt}/{max_retries}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                wait_time = 2 ** (attempt - 1)  # 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        # All retries exhausted
        duration = time.time() - start_time
        
        self.decision_logger.log_decision(task_id, {
            'decision_type': 'execution',
            'status': 'failed',
            'skill': skill_name,
            'attempts': max_retries,
            'error': last_error,
            'duration': duration
        })
        
        return {
            'status': 'error',
            'error': f"All {max_retries} retries failed: {last_error}",
            'skill': skill_name,
            'attempts': max_retries
        }
    
    def _get_skill(self, skill_name: str):
        """Get or create skill instance."""
        try:
            # Check cache
            if skill_name in self.skill_cache:
                return self.skill_cache[skill_name]
            
            # Add Skills directory to path
            skills_dir = os.path.join(os.path.dirname(__file__), '..', 'Skills')
            if skills_dir not in sys.path:
                sys.path.insert(0, skills_dir)
            
            # Import skill dynamically
            if skill_name == 'marketing_skill':
                from marketing_skill import MarketingSkill
                skill = MarketingSkill()
            elif skill_name == 'operations_skill':
                from operations_skill import OperationsSkill
                skill = OperationsSkill()
            elif skill_name == 'ceo_briefing_skill':
                from ceo_briefing_skill import CEOBriefingSkill
                skill = CEOBriefingSkill()
            else:
                logger.error(f"Unknown skill: {skill_name}")
                return None
            
            # Cache it
            self.skill_cache[skill_name] = skill
            return skill
            
        except ImportError as e:
            logger.error(f"Failed to import skill {skill_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load skill {skill_name}: {e}")
            return None


class MultiStepOrchestrator:
    """Orchestrate multi-step tasks."""
    
    def __init__(self, skill_executor: SkillExecutor):
        self.executor = skill_executor
        self.decision_logger = DecisionLogger()
    
    def execute_sequence(self, task_id: str, steps: List[Dict]) -> Dict:
        """
        Execute a sequence of steps.
        
        Args:
            task_id: Task identifier
            steps: List of {skill, action, context} dicts
            
        Returns:
            Dict: Combined result
        """
        results = []
        overall_status = 'success'
        
        for i, step in enumerate(steps):
            logger.info(f"Executing step {i+1}/{len(steps)}: {step.get('skill')}::{step.get('action')}")
            
            result = self.executor.execute(
                step.get('skill'),
                step.get('context', {})
            )
            
            results.append({
                'step': i + 1,
                'skill': step.get('skill'),
                'action': step.get('action'),
                'result': result
            })
            
            if result.get('status') != 'success':
                overall_status = 'partial_success' if overall_status == 'success' else 'failed'
                logger.warning(f"Step {i+1} had status: {result.get('status')}")
        
        return {
            'status': overall_status,
            'task_id': task_id,
            'steps_completed': len(results),
            'results': results
        }
    
    def detect_multistep(self, task: Dict) -> Optional[List[Dict]]:
        """
        Detect if a task requires multiple steps.
        
        Returns list of steps if multi-step, None otherwise.
        """
        description = task.get('description', '').lower()
        metadata = task.get('metadata', {})
        
        # Pattern: "post marketing update" or similar
        if any(kw in description for kw in ['post', 'publish', 'share']) and \
           any(kw in description for kw in ['update', 'announcement', 'news', 'marketing']):
            
            return [
                {
                    'skill': 'marketing_skill',
                    'action': 'generate_content',
                    'context': {
                        'action': 'generate_content',
                        'topic': metadata.get('topic', 'company update'),
                        'count': 3
                    }
                },
                {
                    'skill': 'marketing_skill',
                    'action': 'post_all',
                    'context': {
                        'action': 'post_all',
                        'content': metadata.get('content', task.get('description'))
                    }
                }
            ]
        
        # Pattern: "send email and follow up on whatsapp"
        if 'email' in description and 'whatsapp' in description:
            return [
                {
                    'skill': 'operations_skill',
                    'action': 'process_gmail',
                    'context': {
                        'action': 'process_gmail',
                        'max_results': 10
                    }
                },
                {
                    'skill': 'operations_skill',
                    'action': 'process_whatsapp',
                    'context': {
                        'action': 'process_whatsapp',
                        'limit': 10
                    }
                }
            ]
        
        return None


class RALPHLoop:
    """
    Main RALPH Loop - Recursive Autonomous Learning & Processing Handler.
    
    Continuously monitors for tasks, routes them, executes skills,
    and logs all actions.
    """
    
    def __init__(self, poll_interval: float = 5.0):
        self.poll_interval = poll_interval
        self.running = False
        
        # Initialize components
        self.state_store = StateStore()
        self.router = TaskRouter()
        self.executor = SkillExecutor()
        self.orchestrator = MultiStepOrchestrator(self.executor)
        self.decision_logger = DecisionLogger()
        self.task_history = TaskHistory()
        
        # Statistics
        self.stats = {
            'tasks_processed': 0,
            'tasks_failed': 0,
            'multistep_detected': 0,
            'retries_total': 0,
            'start_time': None
        }
        
        logger.info("RALPH Loop initialized")
    
    def start(self):
        """Start the RALPH loop."""
        self.running = True
        self.stats['start_time'] = datetime.now().isoformat()
        
        logger.info("=" * 50)
        logger.info("RALPH Loop started - Autonomous Decision Engine")
        logger.info("=" * 50)
        
        try:
            while self.running:
                self._loop_iteration()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("RALPH Loop interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"RALPH Loop error: {e}")
            # Don't crash - continue running
            self._loop_iteration()
    
    def stop(self):
        """Stop the RALPH loop."""
        self.running = False
        logger.info("RALPH Loop stopped")
    
    def _loop_iteration(self):
        """Execute one iteration of the RALPH loop."""
        try:
            # Get pending tasks
            pending_tasks = self.state_store.get_pending_tasks()
            
            if not pending_tasks:
                logger.debug("No pending tasks - waiting...")
                return
            
            logger.info(f"Found {len(pending_tasks)} pending task(s)")
            
            # Process each task
            for task in pending_tasks:
                self._process_task(task)
            
        except Exception as e:
            logger.error(f"Loop iteration error: {e}")
            # Continue running - don't crash
    
    def _process_task(self, task: Dict):
        """Process a single task."""
        task_id = task.get('id')
        description = task.get('description', '')[:50]
        
        logger.info(f"Processing task {task_id}: {description}...")
        
        # Update status to in_progress
        self.state_store.update_task(task_id, {
            'status': TaskStatus.IN_PROGRESS.value,
            'started_at': datetime.now().isoformat()
        })
        
        try:
            # Check for multi-step pattern
            steps = self.orchestrator.detect_multistep(task)
            
            if steps:
                # Execute multi-step sequence
                logger.info(f"Multi-step pattern detected for task {task_id}")
                self.stats['multistep_detected'] += 1
                
                result = self.orchestrator.execute_sequence(task_id, steps)
                
            else:
                # Single-step execution
                # Route task
                skill_name, action, context = self.router.route(task)
                
                # Execute skill
                result = self.executor.execute(skill_name, context, task.get('max_retries', 3))
            
            # Update task status
            if result.get('status') == 'success':
                self.state_store.update_task(task_id, {
                    'status': TaskStatus.COMPLETED.value,
                    'completed_at': datetime.now().isoformat(),
                    'result': result
                })
                self.stats['tasks_processed'] += 1
                logger.info(f"Task {task_id} completed successfully")
                
            else:
                # Check if we should retry
                retry_count = task.get('retry_count', 0)
                max_retries = task.get('max_retries', 3)
                
                if retry_count < max_retries:
                    # Schedule retry
                    self.state_store.update_task(task_id, {
                        'status': TaskStatus.RETRYING.value,
                        'retry_count': retry_count + 1,
                        'last_error': result.get('error'),
                        'next_retry': datetime.now().isoformat()
                    })
                    self.stats['retries_total'] += 1
                    logger.warning(f"Task {task_id} scheduled for retry ({retry_count + 1}/{max_retries})")
                else:
                    # Mark as failed
                    self.state_store.update_task(task_id, {
                        'status': TaskStatus.FAILED.value,
                        'failed_at': datetime.now().isoformat(),
                        'error': result.get('error')
                    })
                    self.stats['tasks_failed'] += 1
                    logger.error(f"Task {task_id} failed after {max_retries} retries")
            
            # Record in history
            self.task_history.record(task, result, 0)
            
        except Exception as e:
            logger.error(f"Task {task_id} processing error: {e}")
            self.state_store.update_task(task_id, {
                'status': TaskStatus.FAILED.value,
                'error': str(e)
            })
            self.stats['tasks_failed'] += 1
    
    def add_task(self, description: str, metadata: Dict = None, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Add a new task to the queue."""
        task = {
            'description': description,
            'metadata': metadata or {},
            'priority': priority.value,
            'source': 'api'
        }
        return self.state_store.add_task(task)
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        uptime = None
        if self.stats['start_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            uptime = (datetime.now() - start).total_seconds()
        
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'success_rate': self.task_history.get_success_rate(),
            'pending_tasks': len(self.state_store.get_pending_tasks())
        }
    
    def print_stats(self):
        """Print current statistics."""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("RALPH Loop Statistics")
        print("=" * 50)
        print(f"Tasks Processed: {stats['tasks_processed']}")
        print(f"Tasks Failed: {stats['tasks_failed']}")
        print(f"Multi-step Detected: {stats['multistep_detected']}")
        print(f"Total Retries: {stats['retries_total']}")
        print(f"Success Rate: {stats['success_rate']:.1%}")
        print(f"Pending Tasks: {stats['pending_tasks']}")
        print(f"Uptime: {stats['uptime_seconds']:.0f}s")
        print("=" * 50 + "\n")


# Convenience functions
def create_task(description: str, **kwargs) -> str:
    """Create a new task."""
    loop = RALPHLoop()
    return loop.add_task(description, kwargs.get('metadata'), kwargs.get('priority', TaskPriority.NORMAL))


# Main entry point
if __name__ == '__main__':
    print("=" * 60)
    print("RALPH Loop - Autonomous Decision Engine")
    print("Recursive Autonomous Learning & Processing Handler")
    print("=" * 60)
    print()
    
    # Create the loop
    loop = RALPHLoop(poll_interval=5.0)
    
    # Add demo tasks for testing
    print("Adding demo tasks...")
    
    loop.add_task(
        "Post marketing update about our new AI features",
        metadata={'content': 'Excited to announce our new AI-powered automation features! 🚀 #AI #Innovation'},
        priority=TaskPriority.HIGH
    )
    
    loop.add_task(
        "Generate weekly CEO briefing",
        metadata={'period': 7},
        priority=TaskPriority.NORMAL
    )
    
    loop.add_task(
        "Process unread emails and respond to inquiries",
        metadata={'auto_respond': True},
        priority=TaskPriority.HIGH
    )
    
    print("Demo tasks added. Starting RALPH loop...")
    print("Press Ctrl+C to stop.\n")
    
    # Start the loop
    loop.start()
