# Contributing to AI-Powered Task Management Agent 🤝

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Basic knowledge of Python, TypeScript, and React
- Google Gemini API key (for testing)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/your-username/AI_PowerTMS.git
cd AI_PowerTMS
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/original-owner/AI_PowerTMS.git
```

## 🛠️ Development Setup

### 1. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit with your configuration
nano .env
```

### 2. Start Development Environment
```bash
# Start all services
docker-compose up -d --build

# Check service status
docker-compose ps
```

### 3. Verify Setup
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Fixes**: Fix existing issues
- **Feature Additions**: Add new functionality
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve tests
- **Performance**: Optimize existing code
- **UI/UX**: Improve user interface and experience

### Code Style

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Use meaningful variable and function names

```python
def create_task(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a new task with the given details.
    
    Args:
        title: The task title
        description: Optional task description
        due_date: Optional due date
        
    Returns:
        Dictionary containing the created task details
    """
    # Implementation here
```

#### TypeScript/React (Frontend)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling

```typescript
interface TaskProps {
  task: Task;
  onUpdate: (taskId: number, updates: Partial<Task>) => void;
  onDelete: (taskId: number) => void;
}

export function TaskComponent({ task, onUpdate, onDelete }: TaskProps) {
  // Component implementation
}
```

### Commit Message Format

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(agent): add support for task filtering by priority
fix(websocket): resolve connection timeout issues
docs(readme): update installation instructions
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

2. **Make Your Changes**
- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

3. **Test Your Changes**
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose up --build
# Test the application manually
```

4. **Commit Your Changes**
```bash
git add .
git commit -m "feat(component): add new feature"
```

5. **Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

### Submitting a Pull Request

1. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

2. **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

3. **Review Process**
   - Maintainers will review your PR
   - Address any feedback promptly
   - Make requested changes
   - Keep PR up to date with main branch

## 🐛 Issue Reporting

### Before Creating an Issue

1. Check existing issues
2. Search for similar problems
3. Verify the issue with latest version

### Creating an Issue

Use the appropriate issue template:

#### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

#### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## 🔄 Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `fix/*`: Bug fixes
- `hotfix/*`: Critical fixes for production

### Workflow Steps

1. **Start from main**
```bash
git checkout main
git pull upstream main
```

2. **Create feature branch**
```bash
git checkout -b feature/your-feature
```

3. **Develop and test**
```bash
# Make changes
# Write tests
# Test locally
```

4. **Keep branch updated**
```bash
git checkout main
git pull upstream main
git checkout feature/your-feature
git rebase main
```

5. **Submit PR**
```bash
git push origin feature/your-feature
# Create PR on GitHub
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_agent.py

# Run with verbose output
python -m pytest -v
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Integration Testing

```bash
# Start services
docker-compose up -d

# Run integration tests
npm run test:integration

# Test API endpoints
curl http://localhost:8000/api/tasks
```

### Test Guidelines

- Write unit tests for all new functions
- Write integration tests for API endpoints
- Test error conditions and edge cases
- Maintain test coverage above 80%
- Use descriptive test names

## 📚 Documentation

### Code Documentation

- Write docstrings for all functions and classes
- Use type hints in Python
- Add JSDoc comments for complex functions
- Include examples in docstrings

### API Documentation

- Update OpenAPI/Swagger documentation
- Document new endpoints
- Include request/response examples
- Document error codes

### User Documentation

- Update README.md for new features
- Add usage examples
- Update deployment guides
- Create tutorials for complex features

## 🏷️ Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `1.0.0` - Initial release
- `1.1.0` - New features
- `1.1.1` - Bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] Docker images built and pushed

## 🤔 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Comments**: Code-specific discussions

### Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the AI-Powered Task Management Agent! 🚀
