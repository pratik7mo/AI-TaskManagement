from typing import List, Optional, Dict, Any
if __package__:
    from .database import Task, TaskStatus, TaskPriority, SessionLocal
else:
    from database import Task, TaskStatus, TaskPriority, SessionLocal
from datetime import datetime

def get_db_session():
    """Get a database session"""
    return SessionLocal()

def create_task(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "medium",
    time_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new task with the given details.
    
    Args:
        title: The task title
        description: Optional task description
        due_date: Optional due date in ISO format (YYYY-MM-DD)
        priority: Task priority (low, medium, high, urgent)
    
    Returns:
        Dictionary containing the created task details
    """
    db = get_db_session()
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD format."}
        
        # Validate priority
        try:
            task_priority = TaskPriority(priority.lower())
        except ValueError:
            return {"error": f"Invalid priority. Must be one of: {[p.value for p in TaskPriority]}"}
        
        # Include time hint in description if present (simple UX improvement without schema change)
        final_description = description
        if time_hint:
            final_description = (description + f" | time: {time_hint}") if description else f"time: {time_hint}"
        
        task = Task(
            title=title,
            description=final_description,
            due_date=parsed_due_date,
            priority=task_priority
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {
            "success": True,
            "message": f"Task '{title}' created successfully",
            "task": task.to_dict()
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create task: {str(e)}"}
    finally:
        db.close()

def update_task(
    task_id: Optional[int] = None,
    title_match: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task by ID or title match.
    
    Args:
        task_id: The task ID to update
        title_match: Title to match for updating (if no ID provided)
        title: New title
        description: New description
        status: New status (pending, in_progress, completed, cancelled)
        due_date: New due date in ISO format
        priority: New priority (low, medium, high, urgent)
    
    Returns:
        Dictionary containing the update result
    """
    db = get_db_session()
    try:
        # Find the task
        task = None
        if task_id:
            task = db.query(Task).filter(Task.id == task_id).first()
        elif title_match:
            task = db.query(Task).filter(Task.title.ilike(f"%{title_match}%")).first()
        
        if not task:
            return {"error": "Task not found"}
        
        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            try:
                task.status = TaskStatus(status.lower())
            except ValueError:
                return {"error": f"Invalid status. Must be one of: {[s.value for s in TaskStatus]}"}
        if due_date is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD format."}
        if priority is not None:
            try:
                task.priority = TaskPriority(priority.lower())
            except ValueError:
                return {"error": f"Invalid priority. Must be one of: {[p.value for p in TaskPriority]}"}
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        
        return {
            "success": True,
            "message": f"Task '{task.title}' updated successfully",
            "task": task.to_dict()
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update task: {str(e)}"}
    finally:
        db.close()

def delete_task(task_id: Optional[int] = None, title_match: Optional[str] = None) -> Dict[str, Any]:
    """
    Delete a task by ID or title match.
    
    Args:
        task_id: The task ID to delete
        title_match: Title to match for deletion (if no ID provided)
    
    Returns:
        Dictionary containing the deletion result
    """
    db = get_db_session()
    try:
        # Find the task
        task = None
        if task_id:
            task = db.query(Task).filter(Task.id == task_id).first()
        elif title_match:
            task = db.query(Task).filter(Task.title.ilike(f"%{title_match}%")).first()
        
        if not task:
            return {"error": "Task not found"}
        
        task_title = task.title
        db.delete(task)
        db.commit()
        
        return {
            "success": True,
            "message": f"Task '{task_title}' deleted successfully"
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete task: {str(e)}"}
    finally:
        db.close()

def list_tasks() -> Dict[str, Any]:
    """
    List all tasks.
    
    Returns:
        Dictionary containing all tasks
    """
    db = get_db_session()
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        
        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks)
        }
    except Exception as e:
        return {"error": f"Failed to list tasks: {str(e)}"}
    finally:
        db.close()

def filter_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filter tasks by various criteria.
    
    Args:
        status: Filter by status (pending, in_progress, completed, cancelled)
        priority: Filter by priority (low, medium, high, urgent)
        due_date_from: Filter tasks due from this date (ISO format)
        due_date_to: Filter tasks due until this date (ISO format)
    
    Returns:
        Dictionary containing filtered tasks
    """
    db = get_db_session()
    try:
        query = db.query(Task)
        
        if status:
            try:
                task_status = TaskStatus(status.lower())
                query = query.filter(Task.status == task_status)
            except ValueError:
                return {"error": f"Invalid status. Must be one of: {[s.value for s in TaskStatus]}"}
        
        if priority:
            try:
                task_priority = TaskPriority(priority.lower())
                query = query.filter(Task.priority == task_priority)
            except ValueError:
                return {"error": f"Invalid priority. Must be one of: {[p.value for p in TaskPriority]}"}
        
        if due_date_from:
            try:
                from_date = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
                query = query.filter(Task.due_date >= from_date)
            except ValueError:
                return {"error": "Invalid due_date_from format. Use YYYY-MM-DD format."}
        
        if due_date_to:
            try:
                to_date = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
                query = query.filter(Task.due_date <= to_date)
            except ValueError:
                return {"error": "Invalid due_date_to format. Use YYYY-MM-DD format."}
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return {
            "success": True,
            "tasks": [task.to_dict() for task in tasks],
            "count": len(tasks),
            "filters": {
                "status": status,
                "priority": priority,
                "due_date_from": due_date_from,
                "due_date_to": due_date_to
            }
        }
    except Exception as e:
        return {"error": f"Failed to filter tasks: {str(e)}"}
    finally:
        db.close()
