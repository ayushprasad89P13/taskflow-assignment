from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    columns = relationship("ColumnModel", back_populates="board", cascade="all, delete-orphan", order_by="ColumnModel.order")

class ColumnModel(Base):
    __tablename__ = "columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan", order_by="Task.order")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    column_id = Column(Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), default="Medium")
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    column = relationship("ColumnModel", back_populates="tasks")
