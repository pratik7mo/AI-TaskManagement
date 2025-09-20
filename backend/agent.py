"""
AI Task Management Agent

A modular AI agent for task management with both LLM-powered and fallback capabilities.
Supports natural language processing for task creation, updates, deletion, and filtering.
"""

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import MessagesState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from typing import TypedDict, List, Dict, Any, Optional
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Import task management functions (always prefer real implementations)
# Try relative import first (package context), then absolute as fallback
try:
    from .task_tools import create_task, update_task, delete_task, list_tasks, filter_tasks
except Exception:
    try:
        from task_tools import create_task, update_task, delete_task, list_tasks, filter_tasks
    except Exception as import_error:
        # If both imports fail, surface a clear error instead of using non-persistent stubs
        raise RuntimeError(
            "Failed to import task tools. Ensure 'task_tools.py' is available and importable."
        ) from import_error

# Load env next to this file so it works regardless of CWD
load_dotenv(dotenv_path=Path(__file__).with_name('.env'))

# System prompt for the AI agent
SYSTEM_PROMPT = """You are an AI-powered task management assistant. Your role is to help users manage their tasks through natural language commands.

You have access to tools for creating, updating, deleting, listing, and filtering tasks.

IMPORTANT: When users mention creating a task, use the create_task tool immediately. Don't ask for clarification unless absolutely necessary.

For task creation:
- Extract title from the user's message
- Set due date if mentioned
- Set priority if mentioned (default to medium)
- Create the task immediately using create_task tool

Always respond with friendly, natural language and appropriate emojis."""

class AgentState(TypedDict):
    """State structure for the agent workflow"""
    messages: List[Dict[str, str]]
    current_task: Dict[str, Any]
    user_preferences: Dict[str, Any]

class TextProcessor:
    """Utility class for processing natural language text"""
    
    @staticmethod
    def extract_title(user_input: str) -> str:
        """Extract task title from user input"""
        patterns = [
            r'add a task:\s*(.+?)(?:\s+(?:by|due|tomorrow|today|next week|priority|description)|$)',
            r'finish (.+?)\s+by\s+(.+?)(?:\s|$)',
            r'remind me to (.+?)(?:\s+(?:tomorrow|today|next week|due|priority|description)|$)',
            r'(?:i\s+)?(?:have|need|must|should|want)\s+to\s+(.+?)(?:\s+(?:by|due|tomorrow|today|next week|priority|description)|$)',
            r'task:\s*(.+?)(?:\s+(?:description|due|priority)|$)',
            r'create a task (?:called|named|to)?\s*(.+?)(?:\s+(?:description|due|priority)|$)',
            r'buy (.+?)(?:\s+(?:tomorrow|today|next week|due|priority|description)|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: return the first few words as title
        words = user_input.split()
        if len(words) > 3:
            return " ".join(words[:4])
        return user_input
    
    @staticmethod
    def extract_description(user_input: str) -> Optional[str]:
        """Extract task description from user input"""
        match = re.search(r'description:\s*(.+?)(?:\s+(?:due|priority)|$)', user_input, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def extract_due_date(user_input: str) -> Optional[str]:
        """Extract due date from user input"""
        # Day names mapping
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Look for specific patterns
        patterns = [
            (r'by\s+(friday|monday|tuesday|wednesday|thursday|saturday|sunday)', 
             lambda m: TextProcessor._get_date_for_day(m.group(1).lower(), day_map)),
            (r'by\s+tomorrow', lambda m: (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')),
            (r'tomorrow', lambda m: (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')),
            (r'today', lambda m: datetime.now().strftime('%Y-%m-%d')),
            (r'next week', lambda m: (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')),
            (r'(\d{4}-\d{2}-\d{2})', lambda m: m.group(1)),
            (r'(\d{1,2}/\d{1,2}/\d{4})', lambda m: m.group(1))
        ]
        
        for pattern, extractor in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return extractor(match)
        
        return None

    @staticmethod
    def extract_time(user_input: str) -> Optional[str]:
        """Extract time (HH:MM 24h) from user input. Supports patterns like 'at 7pm', 'by 19:30', 'tomorrow morning'."""
        # Explicit HH:MM
        m = re.search(r'(?:at|by)?\s*(\d{1,2}):(\d{2})\s*(am|pm)?', user_input, re.IGNORECASE)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2))
            mer = m.group(3).lower() if m.group(3) else None
            if mer == 'pm' and hour < 12:
                hour += 12
            if mer == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}"
        # Hour with am/pm
        m = re.search(r'(?:at|by)?\s*(\d{1,2})\s*(am|pm)', user_input, re.IGNORECASE)
        if m:
            hour = int(m.group(1))
            mer = m.group(2).lower()
            if mer == 'pm' and hour < 12:
                hour += 12
            if mer == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}:00"
        # Parts of day
        part_map = {
            'morning': '09:00',
            'afternoon': '15:00',
            'evening': '18:00',
            'night': '20:00'
        }
        for k, v in part_map.items():
            if re.search(rf'\b{k}\b', user_input, re.IGNORECASE):
                return v
        return None
    
    @staticmethod
    def _get_date_for_day(day_name: str, day_map: Dict[str, int]) -> str:
        """Calculate date for a given day name"""
        target_day = day_map[day_name]
        today = datetime.now()
        current_day = today.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def extract_priority(user_input: str) -> str:
        """Extract priority from user input"""
        priority_map = {
            'urgent': 'urgent', 'high': 'high', 'medium': 'medium', 'low': 'low',
            'important': 'high', 'critical': 'urgent'
        }
        
        for keyword, priority in priority_map.items():
            if re.search(rf'\b{keyword}\b', user_input, re.IGNORECASE):
                return priority
        
        return "medium"
    
    @staticmethod
    def extract_status(user_input: str) -> Optional[str]:
        """Extract status from user input"""
        status_map = {
            'done': 'completed', 'completed': 'completed', 'finished': 'completed',
            'in progress': 'in_progress', 'started': 'in_progress', 'pending': 'pending',
            'cancelled': 'cancelled', 'canceled': 'cancelled'
        }
        
        for keyword, status in status_map.items():
            if re.search(rf'\b{keyword}\b', user_input, re.IGNORECASE):
                return status
        
        return None
    
    @staticmethod
    def extract_task_id(user_input: str) -> Optional[int]:
        """Extract task ID from user input"""
        match = re.search(r'task\s*#?(\d+)', user_input, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def extract_task_title(user_input: str) -> Optional[str]:
        """Extract task title for matching from user input"""
        match = re.search(r'(?:the\s+)?task\s+(.+?)(?:\s+(?:as|to|is)|$)', user_input, re.IGNORECASE)
        return match.group(1).strip() if match else None

class IntentHandler:
    """Handles intent classification and task actions"""
    
    @staticmethod
    def parse_user_intent(state: AgentState) -> AgentState:
        """Parse user intent and determine what action to take"""
        messages = state["messages"]
        if not messages:
            return state
        
        last_message = messages[-1]
        user_input = last_message.get("content", "").lower()
        
        # Enhanced intent classification with more patterns
        intent_patterns = {
            "create": [
                "create", "add", "new", "make", "finish", "complete", "do", "plan", "schedule",
                "remind me to", "i have to", "have to", "need to", "must", "should", "want to",
                "i want", "i need", "i should", "i must", "i have", "i will", "i'm going to"
            ],
            "update": ["update", "change", "modify", "edit", "mark", "done", "complete", "finish"],
            "delete": ["delete", "remove", "cancel", "drop", "erase"],
            "list": ["list", "show", "display", "get all", "what are", "what's my", "my tasks"],
            "filter": ["filter", "find", "search", "look for", "high priority", "urgent", "pending", "completed"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                state["intent"] = intent
                return state
        
        state["intent"] = "general"
        return state

    @staticmethod
    def execute_task_action(state: AgentState) -> AgentState:
        """Execute the appropriate task action based on intent"""
        intent = state.get("intent", "general")
        messages = state["messages"]
        last_message = messages[-1] if messages else {"content": ""}
        user_input = last_message.get("content", "")
        
        try:
            if intent == "create":
                result = IntentHandler._create_task_from_input(user_input)
            elif intent == "update":
                result = IntentHandler._update_task_from_input(user_input)
            elif intent == "delete":
                result = IntentHandler._delete_task_from_input(user_input)
            elif intent == "list":
                result = list_tasks()
            elif intent == "filter":
                result = IntentHandler._filter_tasks_from_input(user_input)
            else:
                # Enhanced detection for create intent
                create_indicators = [
                    "add", "create", "new", "finish", "complete", "do", "task", "plan", "schedule",
                    "remind me to", "i have to", "have to", "need to", "must", "should", "want to",
                    "i want", "i need", "i should", "i must", "i have", "i will", "i'm going to",
                    "tomorrow", "today", "next week", "this week", "play", "eat", "buy", "call", "visit"
                ]
                
                if any(word in user_input.lower() for word in create_indicators):
                    result = IntentHandler._create_task_from_input(user_input)
                else:
                    result = {
                        "message": "I can help you manage tasks! 😊\n\nTry saying:\n• 'Create a task to buy groceries tomorrow'\n• 'Show me all my tasks'\n• 'Mark task 1 as completed'\n• 'Delete the grocery task'\n\nWhat would you like to do?"
                    }
        except Exception as e:
            result = {"error": f"An error occurred: {str(e)}"}
        
        state["action_result"] = result
        return state

    @staticmethod
    def _create_task_from_input(user_input: str) -> Dict[str, Any]:
        """Extract task details from user input and create task with better parsing"""
        title = TextProcessor.extract_title(user_input)
        if not title:
            return {"error": "I'd be happy to help you create a task! 😊\n\nCould you please tell me what you'd like to do? For example:\n• 'Buy groceries tomorrow'\n• 'Call the dentist next week'\n• 'Finish the report by Friday'"}
        
        description = TextProcessor.extract_description(user_input)
        due_date = TextProcessor.extract_due_date(user_input)
        time_hint = TextProcessor.extract_time(user_input)
        priority = TextProcessor.extract_priority(user_input)
        
        return create_task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            time_hint=time_hint
        )

    @staticmethod
    def _update_task_from_input(user_input: str) -> Dict[str, Any]:
        """Extract update details from user input and update task"""
        task_id = TextProcessor.extract_task_id(user_input)
        title_match = TextProcessor.extract_task_title(user_input)
        
        if not task_id and not title_match:
            return {"error": "I can help you update a task! 😊\n\nPlease tell me which task to update:\n• 'Mark task 1 as completed'\n• 'Update the grocery task to high priority'\n• 'Change task 2 to due tomorrow'"}
        
        # Extract update fields
        new_title = TextProcessor.extract_title(user_input)
        new_description = TextProcessor.extract_description(user_input)
        new_status = TextProcessor.extract_status(user_input)
        new_due_date = TextProcessor.extract_due_date(user_input)
        new_priority = TextProcessor.extract_priority(user_input)
        
        return update_task(
            task_id=task_id,
            title_match=title_match,
            title=new_title,
            description=new_description,
            status=new_status,
            due_date=new_due_date,
            priority=new_priority
        )

    @staticmethod
    def _delete_task_from_input(user_input: str) -> Dict[str, Any]:
        """Extract task identifier from user input and delete task"""
        task_id = TextProcessor.extract_task_id(user_input)
        title_match = TextProcessor.extract_task_title(user_input)
        
        if not task_id and not title_match:
            return {"error": "I can help you delete a task! 😊\n\nPlease tell me which task to delete:\n• 'Delete task 1'\n• 'Remove the grocery task'\n• 'Cancel the dentist appointment'"}
        
        return delete_task(task_id=task_id, title_match=title_match)

    @staticmethod
    def _filter_tasks_from_input(user_input: str) -> Dict[str, Any]:
        """Extract filter criteria from user input and filter tasks"""
        status = TextProcessor.extract_status(user_input)
        priority = TextProcessor.extract_priority(user_input)
        due_date = TextProcessor.extract_due_date(user_input)
        
        return filter_tasks(
            status=status,
            priority=priority,
            due_date_from=due_date
        )

class ResponseGenerator:
    """Generates natural language responses based on action results"""
    
    @staticmethod
    def generate_response(state: AgentState) -> AgentState:
        """Generate a natural language response based on the action result"""
        action_result = state.get("action_result", {})
        messages = state["messages"]
        
        if action_result.get("error"):
            response = action_result["error"]
        elif action_result.get("success"):
            response = action_result.get("message", "Action completed successfully! ✅")
            
            # Add task details if available
            if "task" in action_result:
                task = action_result["task"]
                response += f"\n\n📋 Task Details:\n"
                response += f"• ID: {task['id']}\n"
                response += f"• Title: {task['title']}\n"
                response += f"• Status: {task['status']}\n"
                response += f"• Priority: {task['priority']}\n"
                if task.get('due_date'):
                    response += f"• Due Date: {task['due_date']}\n"
        elif "tasks" in action_result:
            tasks = action_result["tasks"]
            if tasks:
                response = f"📝 Found {len(tasks)} task(s):\n\n"
                for task in tasks:
                    response += f"• {task['title']} (ID: {task['id']}, Status: {task['status']}, Priority: {task['priority']})\n"
                    if task.get('due_date'):
                        response += f"  📅 Due: {task['due_date']}\n"
            else:
                response = "No tasks found matching your criteria. 🤷‍♂️"
        else:
            response = action_result.get("message", "I'm here to help you manage your tasks! 😊")
        
        # Add the assistant's response to messages
        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": str(datetime.utcnow())
        })
        
        state["messages"] = messages
        return state

# Tools for LLM tool-calling
@tool("create_task")
def create_task_tool(title: str, description: Optional[str] = None, 
                    due_date: Optional[str] = None, priority: str = "medium") -> Dict[str, Any]:
    """Add a new task. Provide title (required), optional description, due_date (YYYY-MM-DD), and priority (low|medium|high|urgent)."""
    return create_task(title=title, description=description, due_date=due_date, priority=priority)

@tool("update_task")
def update_task_tool(task_id: Optional[int] = None, title_match: Optional[str] = None, 
                    title: Optional[str] = None, description: Optional[str] = None, 
                    status: Optional[str] = None, due_date: Optional[str] = None, 
                    priority: Optional[str] = None) -> Dict[str, Any]:
    """Modify a task by id or matching title. You can change title, description, status, due_date, or priority. Provide either task_id or title_match."""
    return update_task(task_id=task_id, title_match=title_match, title=title, 
                      description=description, status=status, due_date=due_date, priority=priority)

@tool("delete_task")
def delete_task_tool(task_id: Optional[int] = None, title_match: Optional[str] = None) -> Dict[str, Any]:
    """Delete a task by id or approximate title."""
    return delete_task(task_id=task_id, title_match=title_match)

@tool("list_tasks")
def list_tasks_tool() -> Dict[str, Any]:
    """Return all tasks."""
    return list_tasks()

@tool("filter_tasks")
def filter_tasks_tool(status: Optional[str] = None, priority: Optional[str] = None, 
                     due_date_from: Optional[str] = None, due_date_to: Optional[str] = None) -> Dict[str, Any]:
    """Filter tasks by status, priority, or due date range."""
    return filter_tasks(status=status, priority=priority, due_date_from=due_date_from, due_date_to=due_date_to)

TOOLS = [create_task_tool, update_task_tool, delete_task_tool, list_tasks_tool, filter_tasks_tool]

# Agent creation functions
def create_deterministic_agent():
    """Create and return the non-LLM deterministic agent graph used as fallback."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_intent", IntentHandler.parse_user_intent)
    workflow.add_node("execute_action", IntentHandler.execute_task_action)
    workflow.add_node("generate_response", ResponseGenerator.generate_response)
    
    # Define edges
    workflow.set_entry_point("parse_intent")
    workflow.add_edge("parse_intent", "execute_action")
    workflow.add_edge("execute_action", "generate_response")
    workflow.add_edge("generate_response", END)
    
    return workflow.compile()

def create_llm_tool_agent() -> Any:
    """Create a simple LangGraph of LLM + ToolNode for tool-calling using Gemini.
    Falls back to None if LLM is unavailable."""
    if llm is None:
        return None

    llm_with_tools = llm.bind_tools(TOOLS)

    def call_model(state: MessagesState):
        ai_msg = llm_with_tools.invoke(state["messages"])
        return {"messages": [ai_msg]}

    graph = StateGraph(MessagesState)
    graph.add_node("llm", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "llm")
    graph.add_conditional_edges("llm", tools_condition)
    graph.add_edge("tools", "llm")
    
    return graph.compile()

# Initialize LLM
def initialize_llm():
    """Initialize the Gemini LLM with explicit opt-in and safe fallback.

    To enable the LLM pathway, set environment variable ENABLE_LLM_TOOL_AGENT=true
    and provide a valid GEMINI_API_KEY. Otherwise, the deterministic agent is used.
    """
    try:
        enable_llm = os.getenv("ENABLE_LLM_TOOL_AGENT", "false").lower() == "true"
        if not enable_llm:
            print("Info: LLM tool agent disabled. Using deterministic agent.")
            return None

        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=gemini_key,
                temperature=0.1
            )
        else:
            print("Warning: GEMINI_API_KEY not set. Using fallback mode.")
            return None
    except Exception as e:
        print(f"Warning: Could not initialize Gemini API: {e}. Using fallback mode.")
        return None

# Create agents
llm = initialize_llm()
deterministic_agent = create_deterministic_agent()
llm_tool_agent = create_llm_tool_agent()

def process_user_message(user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Process a user message and return the agent's response.
    Uses Gemini+LangGraph tools when available; otherwise falls back to the regex agent."""
    if conversation_history is None:
        conversation_history = []
    
    # If LLM tool agent available, route through it
    if llm_tool_agent is not None:
        # Build LangChain chat messages: system + history + user
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        for msg in conversation_history:
            if msg.get("role") == "user":
                lc_messages.append(HumanMessage(content=msg.get("content", "")))
            else:
                lc_messages.append(AIMessage(content=msg.get("content", "")))
        lc_messages.append(HumanMessage(content=user_message))

        result = llm_tool_agent.invoke({"messages": lc_messages})
        
        # Convert back to simple dict messages for the frontend
        final_text = result["messages"][-1].content if result.get("messages") else ""
        
        conv_hist = []
        for m in result.get("messages", []):
            if isinstance(m, SystemMessage):
                continue
                
            role = "assistant" if isinstance(m, AIMessage) else "user"
            
            # Filter out raw JSON responses and system prompts
            if role == "assistant" and m.content.startswith('{"success":'):
                continue
            if role == "assistant" and "You are an AI-powered task management assistant" in m.content:
                continue
                
            conv_hist.append({
                "role": role, 
                "content": m.content, 
                "timestamp": str(datetime.utcnow())
            })
            
        return {"response": final_text, "conversation_history": conv_hist}
    
    # Fallback: use deterministic pipeline
    conversation_history.append({
        "role": "user",
        "content": user_message,
        "timestamp": str(datetime.utcnow())
    })
    
    initial_state = {
        "messages": conversation_history,
        "current_task": {},
        "user_preferences": {}
    }
    
    result = deterministic_agent.invoke(initial_state)
    
    return {
        "response": result["messages"][-1]["content"],
        "conversation_history": result["messages"]
    }