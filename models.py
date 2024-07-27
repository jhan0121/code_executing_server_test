from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class QuizType(PyEnum):
    NUM = 'NUM'
    WORD = 'WORD'
    CODE = 'CODE'

class QuizLevel(PyEnum):
    EASY = 'EASY'
    NORMAL = 'NORMAL'
    HARD = 'HARD'

class Quiz(Base):
    __tablename__ = 'quiz'
    
    quiz_id = Column(Integer, primary_key=True)
    curriculum_id = Column(Integer, ForeignKey('curriculums.curriculum_id'))
    quiz_type = Column(Enum(QuizType))
    text = Column(String)
    answer = Column(String)
    level = Column(Enum(QuizLevel))
    q1 = Column(String, nullable=True)
    q2 = Column(String, nullable=True)
    q3 = Column(String, nullable=True)
    q4 = Column(String, nullable=True)
    inputs = Column(String, nullable=True)
    outputs = Column(String, nullable=True)
    word_count = Column(Integer, nullable=True)
