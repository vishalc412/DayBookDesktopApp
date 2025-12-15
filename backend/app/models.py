"""
Database models for Daybook entries
"""

from datetime import datetime
from typing import Optional


class DaybookEntry:
    """Model for a daybook entry"""

    def __init__(
        self,
        entry_id: Optional[int] = None,
        date: Optional[datetime] = None,
        description: str = "",
        debit: float = 0.0,
        credit: float = 0.0,
        balance: float = 0.0,
        category: str = "",
        reference: str = ""
    ):
        self.entry_id = entry_id
        self.date = date or datetime.now()
        self.description = description
        self.debit = debit
        self.credit = credit
        self.balance = balance
        self.category = category
        self.reference = reference

    def to_dict(self):
        """Convert entry to dictionary"""
        return {
            'entry_id': self.entry_id,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'debit': self.debit,
            'credit': self.credit,
            'balance': self.balance,
            'category': self.category,
            'reference': self.reference
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create entry from dictionary"""
        if 'date' in data and isinstance(data['date'], str):
            data['date'] = datetime.fromisoformat(data['date'])
        return cls(**data)
