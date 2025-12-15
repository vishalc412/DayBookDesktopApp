"""
Audit Trail Models
Immutable append-only audit log
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
import uuid

from app.core.database import Base


class AuditLog(Base):
    """
    Audit Log Entry
    Immutable record of all system changes
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # What happened
    event_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)

    # Who did it
    user_id = Column(String(50), default="system", nullable=False)

    # Details
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, POST, REVERSE
    description = Column(Text, nullable=False)

    # Data snapshot (JSON diff)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    changes = Column(JSON, nullable=True)  # Detailed changes

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.event_type} - {self.entity_type}:{self.entity_id}>"
