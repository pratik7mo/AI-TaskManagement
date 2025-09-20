"use client"

import React, { useState, useEffect } from 'react'
import { Task, ChatMessage, WebSocketMessage } from '@/lib/types'
import { ChatInterface } from '@/components/chat-interface'
import { TaskList } from '@/components/task-list'
import { ThemeToggle } from '@/components/theme-toggle'
import { useWebSocket } from '@/hooks/use-websocket'
import { apiClient } from '@/lib/api'
import { Wifi, WifiOff } from 'lucide-react'

export default function HomePage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/chat'

  const { isConnected, sendMessage } = useWebSocket({
    url: wsUrl,
    onMessage: (message: WebSocketMessage) => {
      switch (message.type) {
        case 'agent_response':
          if (message.response && message.conversation_history) {
            setMessages(message.conversation_history)
          }
          setIsLoading(false)
          break
        case 'task_list_update':
          fetchTasks()
          break
        case 'task_created':
        case 'task_updated':
        case 'task_deleted':
          fetchTasks()
          break
      }
    },
    onOpen: () => {
      console.log('WebSocket connected')
      setError(null)
    },
    onClose: () => {
      console.log('WebSocket disconnected')
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
      setError('Connection error. Please refresh the page.')
    },
  })

  const fetchTasks = async () => {
    try {
      const fetchedTasks = await apiClient.getTasks()
      setTasks(fetchedTasks)
      setError(null)
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
      setError('Failed to load tasks')
    }
  }

  useEffect(() => {
    fetchTasks()
  }, [])

  const handleSendMessage = async (message: string) => {
    if (!isConnected) {
      setError('Not connected to server. Please refresh the page.')
      return
    }

    setIsLoading(true)
    setError(null)

    // Add user message to local state immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMessage])

    // Send message via WebSocket
    sendMessage({
      message,
      conversation_history: messages,
    })
  }

  const handleTaskUpdate = async (taskId: number, updates: Partial<Task>) => {
    try {
      await apiClient.updateTask(taskId, updates)
      await fetchTasks()
    } catch (err) {
      console.error('Failed to update task:', err)
      setError('Failed to update task')
    }
  }

  const handleTaskDelete = async (taskId: number) => {
    try {
      await apiClient.deleteTask(taskId)
      await fetchTasks()
    } catch (err) {
      console.error('Failed to delete task:', err)
      setError('Failed to delete task')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                AI Task Management
              </h1>
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <div className="flex items-center space-x-1 text-green-600">
                    <Wifi className="h-4 w-4" />
                    <span className="text-sm">Connected</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-1 text-red-600">
                    <WifiOff className="h-4 w-4" />
                    <span className="text-sm">Disconnected</span>
                  </div>
                )}
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <div className="flex items-center justify-between">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-200px)]">
          {/* Chat Interface */}
          <div className="flex flex-col">
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>

          {/* Task List */}
          <div className="flex flex-col">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 h-full">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Tasks ({tasks.length})
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Your tasks will appear here as you create them
                </p>
              </div>
              <div className="p-4 overflow-y-auto h-[calc(100%-80px)]">
                <TaskList
                  tasks={tasks}
                  onTaskUpdate={handleTaskUpdate}
                  onTaskDelete={handleTaskDelete}
                />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
