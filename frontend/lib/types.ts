export interface Task {
  id: number
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  due_date?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface WebSocketMessage {
  type: 'agent_response' | 'task_list_update' | 'task_created' | 'task_updated' | 'task_deleted'
  response?: string
  conversation_history?: ChatMessage[]
  task?: Task
  task_id?: number
  message?: string
}
