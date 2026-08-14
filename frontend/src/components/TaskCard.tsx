import { Draggable } from '@hello-pangea/dnd';
import type { Task, Priority } from '../types';
import { Pencil, Trash2 } from 'lucide-react';

interface TaskCardProps {
    task: Task;
    index: number;
    onEdit: (task: Task) => void;
    onDelete: (taskId: number) => void;
}

const getPriorityColor = (priority: Priority) => {
    switch (priority) {
        case 'High': return 'bg-red-100 text-red-800 border-red-200';
        case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
        case 'Low': return 'bg-green-100 text-green-800 border-green-200';
        default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
};

const TaskCard: React.FC<TaskCardProps> = ({ task, index, onEdit, onDelete }) => {
    return (
        <Draggable draggableId={task.id.toString()} index={index}>
            {(provided, snapshot) => (
                <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    className={`p-3 mb-2 rounded-md shadow-sm border bg-white group hover:shadow-md transition-shadow ${
                        snapshot.isDragging ? 'opacity-90 scale-105 shadow-lg border-blue-300' : 'border-gray-200'
                    }`}
                >
                    <div className="flex justify-between items-start mb-2">
                        <div className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                        </div>
                        
                        <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button 
                                onClick={(e) => { e.stopPropagation(); onEdit(task); }}
                                className="text-gray-400 hover:text-blue-500 p-1"
                                title="Edit"
                            >
                                <Pencil size={14} />
                            </button>
                            <button 
                                onClick={(e) => { e.stopPropagation(); onDelete(task.id); }}
                                className="text-gray-400 hover:text-red-500 p-1"
                                title="Delete"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    </div>
                    
                    <h4 className="text-sm font-medium text-gray-900 break-words mb-1">
                        {task.title}
                    </h4>
                    
                    {task.description && (
                        <p className="text-xs text-gray-500 line-clamp-2 mt-1 break-words">
                            {task.description}
                        </p>
                    )}
                </div>
            )}
        </Draggable>
    );
};

export default TaskCard;
