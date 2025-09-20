# AI-Powered Task Management (Local Setup) 🚀

A clean local-first setup: FastAPI backend + Next.js frontend + MySQL. Chat with the assistant to create and manage tasks that persist in your local MySQL (visible in MySQL Workbench).

## Features

- Natural language task management (create/update/delete/list/filter)
- Realtime UI via WebSocket
- Dark mode, responsive UI
- Local MySQL persistence (no Docker required)

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PyMySQL, WebSockets
- Frontend: Next.js 14, TypeScript, Tailwind
- AI: LangGraph; optional Gemini key (fallback works without it)
- Database: MySQL (localhost:3306)

## Quick Start (Windows / PowerShell)

### 1) Prerequisites
- Python 3.11+
- Node 18+
- MySQL running locally on 127.0.0.1:3306 (Workbench is fine)

### 2) Backend
```powershell
cd backend
python -m venv .venv
 .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure environment
copy env.example .env
# Adjust .env if your root password differs from 7894

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3) Frontend
```powershell
cd frontend
npm install

# Create .env.local
copy .env.local.example .env.local

npm run dev
```

### 4) URLs
- Frontend: http://localhost:3000 (Next may switch to 3001 if 3000 is in use)
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Environment

- Backend env file: `backend/.env` (see `backend/env.example`)
- Frontend env file: `frontend/.env.local` (see `frontend/.env.local.example`)

## Verify Data in MySQL
Run in MySQL Workbench (connection to 127.0.0.1:3306):
```sql
CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;
SELECT id, title, priority, created_at FROM tasks ORDER BY id DESC LIMIT 10;
```

## Project Structure
```
AI_PowerTMS/
├── backend/
│   ├── database.py
│   ├── models.py
│   ├── task_tools.py
│   ├── agent.py
│   ├── main.py
│   ├── requirements.txt
│   └── env.example
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── package.json
│   └── .env.local.example
└── README.md
```

## Notes

- Gemini key is optional. Without it, the agent uses a deterministic fallback.
- If your local MySQL root password is not `7894`, update `backend/.env` accordingly.

---
Built with ❤️ using FastAPI and Next.js

### Creating Tasks
```
User: "Create a task to buy groceries tomorrow"
AI: "Task 'buy groceries' created successfully with due date tomorrow"

User: "Remind me to call the dentist next week with high priority"
AI: "Task 'call the dentist' created successfully with high priority and due date next week"
```

### Managing Tasks
```
User: "Show me all my tasks"
AI: "Here are your 3 tasks: [lists all tasks with details]"

User: "Mark the grocery task as completed"
AI: "Task 'buy groceries' marked as completed"

User: "Update the dentist task to be due tomorrow"
AI: "Task 'call the dentist' updated with new due date"
```

### Filtering Tasks
```
User: "Show me all high priority tasks"
AI: "Found 2 high priority tasks: [lists matching tasks]"

User: "What tasks are due today?"
AI: "Found 1 task due today: [lists matching tasks]"
```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    WebSocket/HTTP    ┌─────────────────┐
│   Next.js       │◄────────────────────►│   FastAPI       │
│   Frontend      │                      │   Backend       │
└─────────────────┘                      └─────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────┐                      ┌─────────────────┐
│   Chat UI       │                      │   LangGraph     │
│   Task List     │                      │   Agent         │
└─────────────────┘                      └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   MysqlSQL    │
                                        │   Database      │
                                        └─────────────────┘
```

### Agent Workflow
1. **Intent Parsing**: Analyze user input to determine action type
2. **Information Extraction**: Extract task details from natural language
3. **Tool Execution**: Call appropriate task management functions
4. **Response Generation**: Create natural language response
5. **State Update**: Update conversation history and task list

## 🔧 Development

### Local Development Setup

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn main:app --reload
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### API Testing
```bash
# Test the API endpoints
curl http://localhost:8000/api/tasks

# Test WebSocket connection
wscat -c ws://localhost:8000/ws/chat
```

## 📁 Project Structure

```
AI_PowerTMS/
├── backend/
│   ├── alembic/                 # Database migrations
│   ├── database.py              # Database models and connection
│   ├── models.py                # Pydantic models
│   ├── task_tools.py            # Task management functions
│   ├── agent.py                 # LangGraph agent implementation
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Backend container config
├── frontend/
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility functions and types
│   ├── package.json            # Node.js dependencies
│   └── Dockerfile             # Frontend container config
├── docker-compose.yml          # Multi-container setup
├── env.example                 # Environment variables template
└── README.md                   # This file
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Test the complete flow
docker-compose up --build
# Navigate to http://localhost:3000 and test the chat interface
```

## 🚀 Deployment

### Production Deployment

#### Using Docker Compose
```bash
# Set production environment variables
export GEMINI_API_KEY=your_production_key
export SECRET_KEY=your_production_secret
export ENVIRONMENT=production

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

#### Manual Deployment
1. Set up PostgreSQL database
2. Deploy backend to your server
3. Build and deploy frontend
4. Configure reverse proxy (nginx)
5. Set up SSL certificates

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your_production_gemini_key
SECRET_KEY=your_secure_secret_key
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🔒 Security Considerations

- **API Keys**: Store sensitive keys in environment variables
- **Database**: Use strong passwords and restrict access
- **CORS**: Configure appropriate CORS policies
- **Input Validation**: All user inputs are validated
- **SQL Injection**: Protected by SQLAlchemy ORM
- **XSS**: Protected by React's built-in XSS protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agent framework
- [Google Gemini](https://ai.google.dev/) for the language model
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for styling

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**Built with ❤️ using modern AI and web technologies**
