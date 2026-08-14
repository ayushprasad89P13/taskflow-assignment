export type Priority = 'Low' | 'Medium' | 'High';

export interface Task {
    id: number;
    column_id: number;
    title: string;
    description: string | null;
    priority: Priority;
    order: number;
    created_at: string;
}

export interface Column {
    id: number;
    board_id: number;
    title: string;
    order: number;
    created_at: string;
    tasks: Task[];
}

export interface Board {
    id: number;
    title: string;
    created_at: string;
    columns: Column[];
}

export interface TaskCreate {
    column_id: number;
    title: string;
    description?: string | null;
    priority?: Priority;
    order?: number;
}

export interface TaskUpdate {
    title?: string;
    description?: string | null;
    priority?: Priority;
}

export interface TaskMove {
    column_id: number;
    order?: number;
}

export interface TaskCountPerColumn {
    column_id: number;
    column_title: string;
    task_count: number;
}
