# 🤖 AI-Powered Task Management Agent with Chat & List Interfaces

A modern **full-stack Task Management App** where all task operations are controlled by an **AI Agent** through a natural-language **chat interface**.  
The app provides a **live-updating list UI** so users can view and manage tasks in real time.

---

## 📋 Objective
Design and implement a minimal yet powerful AI agent that can:
- Understand natural-language commands from the user.
- Perform full CRUD operations on tasks (create, update, delete, list, filter).
- Keep the task list interface in sync with real-time updates.

---

## 🖼️ Scenario
- The **user interacts only via a chat interface**—no manual forms or buttons needed.
- The **AI agent** parses intent and calls backend tools to manage tasks.
- A **live task list** updates instantly as the agent makes changes.

---

## ⚡ Tech Stack
### Backend
- **Python 3.11+**
- [FastAPI](https://fastapi.tiangolo.com/) – REST API + WebSocket support  
- [LangGraph](https://github.com/langchain-ai/langgraph) – Custom AI agent & tools  
- [Google Gemini API](https://ai.google.dev/) – LLM via `ChatGoogleGenerativeAI`  
- **PostgreSQL** – Persistent task storage  
- **SQLAlchemy or Tortoise ORM** – Database modeling  

### Frontend
- [Next.js](https://nextjs.org/) – React-based framework
- [Tailwind CSS](https://tailwindcss.com/) (or MUI) – Modern UI styling
- WebSocket client or polling for real-time chat/task updates

---

## 🗂️ Task Schema
| Field        | Type        | Description                              |
|--------------|-------------|------------------------------------------|
| `id`         | UUID / int  | Unique identifier                        |
| `title`      | string      | Task title                               |
| `description`| string      | Task details                              |
| `status`     | enum        | e.g. `pending`, `in_progress`, `done`    |
| `due_date`   | datetime    | Optional deadline                        |
| `priority`   | enum        | `low`, `medium`, `high`                  |
| `created_at` | datetime    | Auto-generated                           |
| `updated_at` | datetime    | Auto-generated on updates                 |

---

## 🛠️ AI Agent & Tools
The LangGraph agent uses Gemini to interpret natural-language requests and call Python tool functions:

| Tool Name     | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| **create_task** | Add a new task with title, description, optional `due_date` or `priority`. |
| **update_task** | Modify fields (title, status, etc.) by ID or name. Supports toggling status (e.g., “mark task X as done”). |
| **delete_task** | Remove a task by ID or name match.                                        |
| **list_tasks**  | Return all active tasks.                                                 |
| **filter_tasks**| Filter tasks by priority, status, or due date.                            |

Each tool is registered as a LangGraph tool and callable directly by the agent.

---

## 🏗️ Project Structure
