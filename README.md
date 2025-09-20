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

| Tool Name    | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| **create_task** | Add a new task with title, description, optional `due_date` or `priority`. |
| **update_task** | Modify fields (title, status, etc.) by ID or name. Supports toggling status (e.g., “mark task X as done”). |
| **delete_task** | Remove a task by ID or name match.                                        |
| **list_tasks**  | Return all active tasks.                                                 |
| **filter_tasks**| Filter tasks by priority, status, or due date.                            |

Each tool is registered as a LangGraph tool and callable directly by the agent.

---

## 🏗️ Project Structure
ai-task-agent/
├─ backend/
│ ├─ app/
│ │ ├─ main.py # FastAPI entry point + WebSocket
│ │ ├─ agent/ # LangGraph agent & tools
│ │ ├─ models/ # SQLAlchemy/Tortoise ORM models
│ │ ├─ routes/ # API routes
│ │ └─ schemas/ # Pydantic schemas
│ ├─ requirements.txt
│ └─ Dockerfile
│
├─ frontend/
│ ├─ pages/
│ ├─ components/ # Chat UI + Task list UI
│ ├─ package.json
│ └─ tailwind.config.js
│
└─ docs/ # Architecture diagrams, API docs

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Google Gemini API Key

### Local Development Setup

#### Backend Setup
```bash
# Clone the repo
git clone https://github.com/pratik7mo/AI-TaskManagement.git
cd AI-TaskManagement/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/tasks
GEMINI_API_KEY=your_gemini_key

# Run the server
uvicorn main:app --reload
```

#### Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

### 🚀 Railway Deployment

This project is optimized for Railway deployment without Docker. See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed deployment instructions.

**Quick Railway Deploy:**
1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Railway will automatically deploy your FastAPI backend
4. Your app will be available at `https://your-app.railway.app`

## 💡 Usage
Open the app in your browser.

Start chatting with the AI:

“Create a high priority task to finish the report by tomorrow.”

“List all tasks due this week.”

“Mark the report task as done.”

Watch the task list update in real time.

## 🔮 Future Enhancements
Multi-user authentication & team workspaces.

Advanced natural-language filtering (e.g., “tasks due next Friday with high priority”).

Push notifications and email reminders.

Integrate calendar sync (Google Calendar, Outlook).

## 🤝 Contributing
Pull requests and feature suggestions are welcome!
Please open an issue first to discuss changes.

## 📜 License
This project is licensed under the MIT License.

## 📧 Contact
Your Name – pratikkumarsahoo5@gmail.com
GitHub: https://github.com/pratik7mo/AI-TaskManagement
