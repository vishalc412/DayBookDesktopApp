"""
Event System for Domain Events
Enables event-driven architecture
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Domain event types"""

    # Transaction events
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_POSTED = "transaction.posted"
    TRANSACTION_REVERSED = "transaction.reversed"

    # Account events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_BALANCE_UPDATED = "account.balance_updated"

    # Excel sync events
    EXCEL_SYNC_REQUESTED = "excel.sync_requested"
    EXCEL_SYNC_COMPLETED = "excel.sync_completed"
    EXCEL_SYNC_FAILED = "excel.sync_failed"


@dataclass
class DomainEvent:
    """Base domain event"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    user_id: str = "system"

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()


class EventBus:
    """
    Simple in-memory event bus
    For production, consider using Redis/RabbitMQ
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe a handler to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        self._logger.info(f"Subscribed {handler.__name__} to {event_type}")

    async def publish(self, event: DomainEvent):
        """Publish an event to all subscribers"""
        self._logger.info(f"Publishing event: {event.event_type}")

        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            self._logger.warning(f"No handlers for event: {event.event_type}")
            return

        # Execute handlers concurrently
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    # Run sync handlers in executor
                    tasks.append(asyncio.to_thread(handler, event))
            except Exception as e:
                self._logger.error(f"Error in handler {handler.__name__}: {e}")

        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def clear(self):
        """Clear all handlers (useful for testing)"""
        self._handlers.clear()


# Global event bus instance
event_bus = EventBus()
