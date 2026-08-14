import { useEffect, useState, useCallback } from 'react';
import type { DropResult } from '@hello-pangea/dnd';
import type { Board as BoardType, Task, TaskCountPerColumn, TaskCreate, TaskUpdate } from './types';
import { api } from './api';
import BoardComponent from './components/Board';
import TaskModal from './components/TaskModal';
import { Layout } from 'lucide-react';

const BOARD_ID = 1;

function App() {
    const [board, setBoard] = useState<BoardType | null>(null);
    const [taskCounts, setTaskCounts] = useState<TaskCountPerColumn[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const [filterPriority, setFilterPriority] = useState<string>('');
    
    // Modal state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalColumnId, setModalColumnId] = useState<number | undefined>();
    const [modalExistingTask, setModalExistingTask] = useState<Task | undefined>();

    const showToast = (message: string, type: 'success' | 'error') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            const [boardData, countsData] = await Promise.all([
                api.getBoard(BOARD_ID),
                api.getTaskCounts(BOARD_ID)
            ]);
            
            // If filter is applied, we need to fetch filtered tasks and replace them in the board
            if (filterPriority) {
                const filteredTasks = await api.getTasks(filterPriority);
                // Distribute filtered tasks back to their columns
                const columnsWithFilteredTasks = boardData.columns.map(col => ({
                    ...col,
                    tasks: filteredTasks.filter(t => t.column_id === col.id)
                }));
                setBoard({ ...boardData, columns: columnsWithFilteredTasks });
            } else {
                setBoard(boardData);
            }
            
            setTaskCounts(countsData);
            setError(null);
        } catch (err: unknown) {
            if (err instanceof Error) {
                setError(err.message || 'Failed to load board data');
            } else {
                setError('Failed to load board data');
            }
        } finally {
            setLoading(false);
        }
    }, [filterPriority]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleDragEnd = async (result: DropResult) => {
        const { destination, source, draggableId } = result;

        if (!destination || !board) return;

        if (
            destination.droppableId === source.droppableId &&
            destination.index === source.index
        ) {
            return;
        }

        const sourceColId = parseInt(source.droppableId);
        const destColId = parseInt(destination.droppableId);
        const taskId = parseInt(draggableId);

        // Optimistic UI update
        const newBoard = { ...board };
        
        const sourceColIndex = newBoard.columns.findIndex(c => c.id === sourceColId);
        const destColIndex = newBoard.columns.findIndex(c => c.id === destColId);
        
        const sourceCol = newBoard.columns[sourceColIndex];
        const destCol = newBoard.columns[destColIndex];
        
        const [movedTask] = sourceCol.tasks.splice(source.index, 1);
        movedTask.column_id = destColId;
        destCol.tasks.splice(destination.index, 0, movedTask);
        
        // Update order values for destination column
        destCol.tasks.forEach((t, i) => { t.order = i; });
        if (sourceColId !== destColId) {
            sourceCol.tasks.forEach((t, i) => { t.order = i; });
        }
        
        setBoard(newBoard);

        // API Call
        try {
            await api.moveTask(taskId, {
                column_id: destColId,
                order: destination.index
            });
            // Update counts if moved to a different column
            if (sourceColId !== destColId) {
                setTaskCounts(prev => prev.map(tc => {
                    if (tc.column_id === sourceColId) return { ...tc, task_count: tc.task_count - 1 };
                    if (tc.column_id === destColId) return { ...tc, task_count: tc.task_count + 1 };
                    return tc;
                }));
            }
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            showToast(`Failed to move task: ${message}`, 'error');
            loadData();
        }
    };

    const handleOpenCreateModal = (columnId: number) => {
        setModalColumnId(columnId);
        setModalExistingTask(undefined);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (task: Task) => {
        setModalExistingTask(task);
        setModalColumnId(undefined);
        setIsModalOpen(true);
    };

    const handleSaveTask = async (taskData: TaskCreate | TaskUpdate) => {
        try {
            if (modalExistingTask) {
                await api.updateTask(modalExistingTask.id, taskData as TaskUpdate);
                showToast('Task updated successfully', 'success');
            } else {
                await api.createTask(taskData as TaskCreate);
                showToast('Task created successfully', 'success');
            }
            loadData();
        } catch (err: unknown) {
            throw err;
        }
    };

    const handleDeleteTask = async (taskId: number) => {
        if (!window.confirm('Are you sure you want to delete this task?')) return;
        
        try {
            await api.deleteTask(taskId);
            showToast('Task deleted', 'success');
            loadData();
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            showToast(`Failed to delete task: ${message}`, 'error');
        }
    };

    if (loading && !board) {
        return <div className="flex h-screen items-center justify-center bg-gray-50 text-gray-500">Loading TaskFlow...</div>;
    }

    if (error && !board) {
        return <div className="flex h-screen items-center justify-center bg-gray-50 text-red-500">{error}</div>;
    }

    return (
        <div className="flex flex-col h-screen bg-blue-50/50">
            <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <div className="bg-blue-600 p-1.5 rounded-md">
                        <Layout className="text-white" size={20} />
                    </div>
                    <h1 className="text-xl font-bold text-gray-800 tracking-tight">TaskFlow</h1>
                </div>
                
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <label htmlFor="priority-filter" className="text-sm font-medium text-gray-600">
                            Filter:
                        </label>
                        <select
                            id="priority-filter"
                            value={filterPriority}
                            onChange={(e) => setFilterPriority(e.target.value)}
                            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-md focus:ring-blue-500 focus:border-blue-500 block p-1.5"
                        >
                            <option value="">All Priorities</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                        </select>
                    </div>
                </div>
            </header>

            <main className="flex-1 overflow-hidden px-6">
                {board && (
                    <BoardComponent
                        board={board}
                        taskCounts={taskCounts}
                        onDragEnd={handleDragEnd}
                        onAddTask={handleOpenCreateModal}
                        onEditTask={handleOpenEditModal}
                        onDeleteTask={handleDeleteTask}
                    />
                )}
            </main>

            <TaskModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveTask}
                columnId={modalColumnId}
                existingTask={modalExistingTask}
            />

            {toast && (
                <div className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg text-white font-medium z-50 transition-opacity ${toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'}`}>
                    {toast.message}
                </div>
            )}
        </div>
    );
}

export default App;
