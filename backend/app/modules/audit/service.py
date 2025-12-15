"""
Audit Service
Logging all system changes
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import AuditLog


class AuditService:
    """Service for audit logging"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        action: str,
        description: str,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        user_id: str = "system",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        This is append-only and immutable
        """
        # Calculate changes if both old and new data provided
        changes = None
        if old_data and new_data:
            changes = self._calculate_changes(old_data, new_data)

        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action,
            description=description,
            old_data=old_data,
            new_data=new_data,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.db.add(log_entry)
        await self.db.flush()
        return log_entry

    async def log_create(
        self,
        entity_type: str,
        entity_id: str,
        description: str,
        data: Dict[str, Any],
        user_id: str = "system"
    ) -> AuditLog:
        """Log entity creation"""
        return await self.log(
            event_type=f"{entity_type}.created",
            entity_type=entity_type,
            entity_id=entity_id,
            action="CREATE",
            description=description,
            new_data=data,
            user_id=user_id
        )

    async def log_update(
        self,
        entity_type: str,
        entity_id: str,
        description: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        user_id: str = "system"
    ) -> AuditLog:
        """Log entity update"""
        return await self.log(
            event_type=f"{entity_type}.updated",
            entity_type=entity_type,
            entity_id=entity_id,
            action="UPDATE",
            description=description,
            old_data=old_data,
            new_data=new_data,
            user_id=user_id
        )

    async def log_post(
        self,
        entity_type: str,
        entity_id: str,
        description: str,
        data: Dict[str, Any],
        user_id: str = "system"
    ) -> AuditLog:
        """Log transaction posting"""
        return await self.log(
            event_type=f"{entity_type}.posted",
            entity_type=entity_type,
            entity_id=entity_id,
            action="POST",
            description=description,
            new_data=data,
            user_id=user_id
        )

    async def log_reverse(
        self,
        entity_type: str,
        entity_id: str,
        description: str,
        data: Dict[str, Any],
        user_id: str = "system"
    ) -> AuditLog:
        """Log transaction reversal"""
        return await self.log(
            event_type=f"{entity_type}.reversed",
            entity_type=entity_type,
            entity_id=entity_id,
            action="REVERSE",
            description=description,
            new_data=data,
            user_id=user_id
        )

    def _calculate_changes(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate differences between old and new data"""
        changes = {}

        # Check for modified and added fields
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                changes[key] = {
                    "old": old_value,
                    "new": new_value
                }

        # Check for removed fields
        for key in old_data:
            if key not in new_data:
                changes[key] = {
                    "old": old_data[key],
                    "new": None
                }

        return changes
