import { Board, Task, TaskCreate, TaskMove, TaskUpdate, TaskCountPerColumn } from './types';

const API_BASE_URL = 'http://localhost:8000';

async function fetchWithHandleError(url: string, options?: RequestInit) {
    const response = await fetch(url, options);
    if (!response.ok) {
        let errorMsg = 'An error occurred';
        try {
            const errorData = await response.json();
            errorMsg = errorData.detail || errorMsg;
        } catch {
            // Ignore JSON parse error if response is not JSON
        }
        throw new Error(errorMsg);
    }
    if (response.status === 204) {
        return null; // No content for DELETE
    }
    return response.json();
}

export const api = {
    getBoard: (boardId: number): Promise<Board> => 
        fetchWithHandleError(`${API_BASE_URL}/boards/${boardId}`),
        
    createTask: (task: TaskCreate): Promise<Task> => 
        fetchWithHandleError(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task),
        }),
        
    updateTask: (taskId: number, task: TaskUpdate): Promise<Task> => 
        fetchWithHandleError(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(task),
        }),
        
    moveTask: (taskId: number, move: TaskMove): Promise<Task> => 
        fetchWithHandleError(`${API_BASE_URL}/tasks/${taskId}/move`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(move),
        }),
        
    deleteTask: (taskId: number): Promise<void> => 
        fetchWithHandleError(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE',
        }),
        
    getTasks: (priority?: string): Promise<Task[]> => {
        const url = priority 
            ? `${API_BASE_URL}/tasks?priority=${encodeURIComponent(priority)}` 
            : `${API_BASE_URL}/tasks`;
        return fetchWithHandleError(url);
    },
    
    getTaskCounts: (boardId: number): Promise<TaskCountPerColumn[]> =>
        fetchWithHandleError(`${API_BASE_URL}/boards/${boardId}/task-counts`),
};
