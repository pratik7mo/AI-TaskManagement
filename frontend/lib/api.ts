import { Task } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`)
    if (!response.ok) {
      throw new Error('Failed to fetch tasks')
    }
    return response.json()
  }

  async getTask(id: number): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}`)
    if (!response.ok) {
      throw new Error('Failed to fetch task')
    }
    return response.json()
  }

  async createTask(task: Partial<Task>): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(task),
    })
    if (!response.ok) {
      throw new Error('Failed to create task')
    }
    return response.json()
  }

  async updateTask(id: number, task: Partial<Task>): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(task),
    })
    if (!response.ok) {
      throw new Error('Failed to update task')
    }
    return response.json()
  }

  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error('Failed to delete task')
    }
  }

  async filterTasksByStatus(status: string): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks/filter/${status}`)
    if (!response.ok) {
      throw new Error('Failed to filter tasks')
    }
    return response.json()
  }

  async filterTasksByPriority(priority: string): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks/priority/${priority}`)
    if (!response.ok) {
      throw new Error('Failed to filter tasks')
    }
    return response.json()
  }

  async sendChatMessage(message: string): Promise<{ response: string; conversation_history: any[] }> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    })
    if (!response.ok) {
      throw new Error('Failed to send chat message')
    }
    return response.json()
  }
}

export const apiClient = new ApiClient()
