"use client"

import React from 'react'
import { Task } from '@/lib/types'
import { formatDate, getPriorityColor, getStatusColor } from '@/lib/utils'
import { CheckCircle, Circle, Clock, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface TaskListProps {
  tasks: Task[]
  onTaskUpdate: (taskId: number, updates: Partial<Task>) => void
  onTaskDelete: (taskId: number) => void
}

export function TaskList({ tasks, onTaskUpdate, onTaskDelete }: TaskListProps) {
  const handleStatusToggle = (task: Task) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed'
    onTaskUpdate(task.id, { status: newStatus })
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'high':
        return <AlertCircle className="h-4 w-4 text-orange-500" />
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'low':
        return <Circle className="h-4 w-4 text-green-500" />
      default:
        return <Circle className="h-4 w-4 text-gray-500" />
    }
  }

  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
        <Circle className="h-12 w-12 mb-4" />
        <p className="text-lg font-medium">No tasks yet</p>
        <p className="text-sm">Start a conversation to create your first task!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 transition-all duration-200 hover:shadow-md ${
            task.status === 'completed' ? 'opacity-75' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <button
                onClick={() => handleStatusToggle(task)}
                className="mt-1 transition-colors duration-200"
              >
                {task.status === 'completed' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <Circle className="h-5 w-5 text-gray-400 hover:text-green-500" />
                )}
              </button>
              
              <div className="flex-1 min-w-0">
                <h3 className={`font-medium text-gray-900 dark:text-gray-100 ${
                  task.status === 'completed' ? 'line-through' : ''
                }`}>
                  {task.title}
                </h3>
                
                {task.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {task.description}
                  </p>
                )}
                
                <div className="flex items-center space-x-4 mt-3">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                    {task.status.replace('_', ' ')}
                  </span>
                  
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                    {getPriorityIcon(task.priority)}
                    <span className="ml-1">{task.priority}</span>
                  </span>
                  
                  {task.due_date && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Due: {formatDate(task.due_date)}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onTaskDelete(task.id)}
              className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              Delete
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
