import React from 'react';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import { Board as BoardType, TaskCountPerColumn } from '../types';
import Column from './Column';
import { Task } from '../types';

interface BoardProps {
    board: BoardType;
    taskCounts: TaskCountPerColumn[];
    onDragEnd: (result: DropResult) => void;
    onAddTask: (columnId: number) => void;
    onEditTask: (task: Task) => void;
    onDeleteTask: (taskId: number) => void;
}

const Board: React.FC<BoardProps> = ({ 
    board, 
    taskCounts,
    onDragEnd, 
    onAddTask, 
    onEditTask, 
    onDeleteTask 
}) => {
    return (
        <div className="h-full flex flex-col pt-4 overflow-hidden">
            <DragDropContext onDragEnd={onDragEnd}>
                <div className="flex flex-1 overflow-x-auto space-x-4 pb-4 px-1 items-start">
                    {board.columns.map((column) => {
                        const count = taskCounts.find(c => c.column_id === column.id)?.task_count || 0;
                        return (
                            <Column
                                key={column.id}
                                column={column}
                                tasks={column.tasks}
                                taskCount={count}
                                onAddTask={onAddTask}
                                onEditTask={onEditTask}
                                onDeleteTask={onDeleteTask}
                            />
                        );
                    })}
                </div>
            </DragDropContext>
        </div>
    );
};

export default Board;
