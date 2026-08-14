import { Droppable } from '@hello-pangea/dnd';
import type { Column as ColumnType, Task } from '../types';
import TaskCard from './TaskCard';
import { Plus } from 'lucide-react';

interface ColumnProps {
    column: ColumnType;
    tasks: Task[];
    taskCount: number;
    onAddTask: (columnId: number) => void;
    onEditTask: (task: Task) => void;
    onDeleteTask: (taskId: number) => void;
}

const Column: React.FC<ColumnProps> = ({ 
    column, 
    tasks, 
    taskCount,
    onAddTask, 
    onEditTask, 
    onDeleteTask 
}) => {
    return (
        <div className="flex flex-col bg-gray-100 rounded-lg w-72 flex-shrink-0 max-h-full">
            <div className="p-3 font-semibold text-gray-700 flex justify-between items-center border-b border-gray-200">
                <div className="flex items-center space-x-2">
                    <h3>{column.title}</h3>
                    <span className="bg-gray-200 text-gray-600 text-xs px-2 py-0.5 rounded-full">
                        {taskCount}
                    </span>
                </div>
                <button 
                    onClick={() => onAddTask(column.id)}
                    className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-800 transition-colors"
                >
                    <Plus size={18} />
                </button>
            </div>
            
            <Droppable droppableId={column.id.toString()}>
                {(provided, snapshot) => (
                    <div 
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        className={`p-2 flex-grow overflow-y-auto transition-colors min-h-[150px] ${
                            snapshot.isDraggingOver ? 'bg-gray-200/50' : ''
                        }`}
                    >
                        {tasks.map((task, index) => (
                            <TaskCard 
                                key={task.id} 
                                task={task} 
                                index={index}
                                onEdit={onEditTask}
                                onDelete={onDeleteTask}
                            />
                        ))}
                        {provided.placeholder}
                    </div>
                )}
            </Droppable>
            
            <div className="p-2 pt-0">
                <button 
                    onClick={() => onAddTask(column.id)}
                    className="flex items-center w-full py-2 px-2 text-sm text-gray-500 hover:text-gray-800 hover:bg-gray-200 rounded transition-colors"
                >
                    <Plus size={16} className="mr-1" />
                    Add a task
                </button>
            </div>
        </div>
    );
};

export default Column;
