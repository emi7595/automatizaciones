"""
Enhanced Contact model with all required metadata.
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class Contact(Base):
    """Enhanced Contact model with comprehensive metadata."""
    
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=True, index=True)
    birthday = Column(Date, nullable=True, index=True)  # 9999-XX-XX for unknown year
    tags = Column(JSON, nullable=True)  # Array of strings for flexible tagging
    notes = Column(Text, nullable=True)
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', phone='{self.phone}')>"
    
    @property
    def is_birthday_unknown_year(self) -> bool:
        """Check if birthday year is placeholder (9999)."""
        if not self.birthday:
            return False
        return self.birthday.year == 9999
    
    def get_birthday_for_current_year(self) -> Date:
        """Get birthday for current year, handling unknown year case."""
        if not self.birthday:
            return None
        if self.is_birthday_unknown_year:
            # Return birthday with current year
            from datetime import date
            return date(date.today().year, self.birthday.month, self.birthday.day)
        return self.birthday
