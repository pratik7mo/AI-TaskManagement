from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

# Support both package and script import styles deterministically
if __package__:
    from .database import get_db, create_tables, Task
    from .models import TaskCreate, TaskUpdate, TaskResponse, ChatMessage, ChatRequest
    from .agent import process_user_message
else:  # When started as a script from inside `backend/`
    from .database import get_db, create_tables, Task
    from .models import TaskCreate, TaskUpdate, TaskResponse, ChatMessage, ChatRequest
    from .agent import process_user_message

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at startup
    create_tables()
    yield
    # Run at shutdown (if needed)

# Create FastAPI app (explicit docs and OpenAPI URLs)
app = FastAPI(
    title="AI Task Management API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Database tables are created in the lifespan startup handler

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "AI Task Management API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Task Management API is running"}

# WebSocket endpoint for chat
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message with the AI agent
            result = process_user_message(
                message_data.get("message", ""),
                message_data.get("conversation_history", [])
            )
            
            # Send response back to client
            await manager.send_personal_message(
                json.dumps({
                    "type": "agent_response",
                    "response": result["response"],
                    "conversation_history": result["conversation_history"]
                }),
                websocket
            )
            
            # Broadcast task list update to all connected clients
            await manager.broadcast(
                json.dumps({
                    "type": "task_list_update",
                    "message": "Task list updated"
                })
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# REST API endpoints for task management
@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """Get all tasks"""
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task_endpoint(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Broadcast update to all connected clients
    await manager.broadcast(
        json.dumps({
            "type": "task_created",
            "task": db_task.to_dict()
        })
    )
    
    return db_task

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    
    # Broadcast update to all connected clients
    await manager.broadcast(
        json.dumps({
            "type": "task_updated",
            "task": db_task.to_dict()
        })
    )
    
    return db_task

@app.delete("/api/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    
    # Broadcast update to all connected clients
    await manager.broadcast(
        json.dumps({
            "type": "task_deleted",
            "task_id": task_id
        })
    )
    
    return {"message": "Task deleted successfully"}

@app.get("/api/tasks/filter/{status}")
async def filter_tasks_by_status(status: str, db: Session = Depends(get_db)):
    """Filter tasks by status"""
    tasks = db.query(Task).filter(Task.status == status).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/api/tasks/priority/{priority}")
async def filter_tasks_by_priority(priority: str, db: Session = Depends(get_db)):
    """Filter tasks by priority"""
    tasks = db.query(Task).filter(Task.priority == priority).order_by(Task.created_at.desc()).all()
    return tasks

# Chat endpoint for non-WebSocket clients
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Process a chat message and return AI response"""
    result = process_user_message(request.message)
    
    return {
        "response": result["response"],
        "conversation_history": result["conversation_history"]
    }

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
