"""
Task Manager for Asynchronous Video Processing
Handles multiple concurrent video processing tasks for different users
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import time
import uuid

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages asynchronous video processing tasks"""
    
    def __init__(self):
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_status: Dict[str, Dict[str, Any]] = {}
        self.user_tasks: Dict[int, str] = {}  # user_id -> task_id mapping
        
    async def start_task(self, user_id: int, task_name: str, coroutine, task_data: Optional[Dict] = None) -> str:
        """Start a new async task for a user"""
        task_id = str(uuid.uuid4())
        
        # Cancel existing task for this user if any
        if user_id in self.user_tasks:
            await self.cancel_user_task(user_id)
        
        # Create and start the task
        task = asyncio.create_task(coroutine)
        self.active_tasks[task_id] = task
        self.user_tasks[user_id] = task_id
        
        # Initialize task status
        self.task_status[task_id] = {
            "user_id": user_id,
            "task_name": task_name,
            "status": "running",
            "start_time": time.time(),
            "data": task_data or {}
        }
        
        # Set up task completion callback
        task.add_done_callback(lambda t: self._on_task_complete(task_id, t))
        
        logger.info(f"Started task {task_id} for user {user_id}: {task_name}")
        return task_id
    
    def _on_task_complete(self, task_id: str, task: asyncio.Task):
        """Handle task completion"""
        try:
            if task_id in self.task_status:
                status = self.task_status[task_id]
                user_id = status["user_id"]
                
                if task.cancelled():
                    status["status"] = "cancelled"
                elif task.exception():
                    status["status"] = "failed"
                    status["error"] = str(task.exception())
                    logger.error(f"Task {task_id} failed: {task.exception()}")
                else:
                    status["status"] = "completed"
                    result = task.result()
                    if result:
                        status["result"] = result
                
                status["end_time"] = time.time()
                status["duration"] = status["end_time"] - status["start_time"]
                
                # Clean up
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                if user_id in self.user_tasks and self.user_tasks[user_id] == task_id:
                    del self.user_tasks[user_id]
                    
                logger.info(f"Task {task_id} completed with status: {status['status']}")
                
        except Exception as e:
            logger.error(f"Error in task completion callback: {e}")
    
    async def cancel_user_task(self, user_id: int) -> bool:
        """Cancel the active task for a user"""
        if user_id not in self.user_tasks:
            return False
            
        task_id = self.user_tasks[user_id]
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            logger.info(f"Cancelled task {task_id} for user {user_id}")
            return True
        
        return False
    
    def get_user_task_status(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the status of a user's current task"""
        if user_id not in self.user_tasks:
            return None
            
        task_id = self.user_tasks[user_id]
        return self.task_status.get(task_id)
    
    def get_active_tasks_count(self) -> int:
        """Get the number of currently active tasks"""
        return len(self.active_tasks)
    
    def get_all_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active tasks"""
        active_status = {}
        for task_id in self.active_tasks:
            if task_id in self.task_status:
                active_status[task_id] = self.task_status[task_id].copy()
        return active_status
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed task records"""
        current_time = time.time()
        to_remove = []
        
        for task_id, status in self.task_status.items():
            if status["status"] in ["completed", "failed", "cancelled"]:
                age_hours = (current_time - status.get("end_time", current_time)) / 3600
                if age_hours > max_age_hours:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.task_status[task_id]
            
        logger.info(f"Cleaned up {len(to_remove)} old task records")

# Global task manager instance
task_manager = TaskManager()