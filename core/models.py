from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    pages = Column(Integer)
    publication_date = Column(Date)
    price = Column(Float)

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"