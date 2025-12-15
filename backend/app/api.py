"""
FastAPI Application for Daybook Desktop Application
RESTful API endpoints for managing daybook entries
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import os

from .excel_sync import ExcelSync
from .models import DaybookEntry


# Pydantic models for request/response validation
class EntryCreate(BaseModel):
    date: Optional[str] = None
    description: str
    debit: float = Field(ge=0, default=0.0)
    credit: float = Field(ge=0, default=0.0)
    category: str = ""
    reference: str = ""


class EntryUpdate(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    debit: Optional[float] = Field(ge=0, default=None)
    credit: Optional[float] = Field(ge=0, default=None)
    category: Optional[str] = None
    reference: Optional[str] = None


class EntryResponse(BaseModel):
    entry_id: Optional[int]
    date: str
    description: str
    debit: float
    credit: float
    balance: float
    category: str
    reference: str


class SuccessResponse(BaseModel):
    success: bool
    message: str


class EntriesResponse(BaseModel):
    success: bool
    entries: List[EntryResponse]


class SummaryResponse(BaseModel):
    success: bool
    summary: dict


class HealthResponse(BaseModel):
    status: str
    version: str


def create_app(excel_file_path: str = None):
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Daybook Desktop API",
        description="RESTful API for Daybook Desktop Application with Real-Time Excel Synchronization",
        version="1.1",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Configure CORS for Electron frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Default Excel file path
    if excel_file_path is None:
        excel_file_path = os.path.join(os.getcwd(), 'daybook.xlsx')

    # Initialize Excel sync
    excel_sync = ExcelSync(excel_file_path)

    @app.get("/api/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": "1.1"}

    @app.get("/api/entries", response_model=EntriesResponse, tags=["Entries"])
    async def get_entries():
        """Get all daybook entries"""
        try:
            entries = excel_sync.read_entries()
            return {
                "success": True,
                "entries": [entry.to_dict() for entry in entries]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post("/api/entries", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED, tags=["Entries"])
    async def create_entry(entry_data: EntryCreate):
        """Create a new daybook entry"""
        try:
            # Validate that either debit or credit is provided
            if entry_data.debit == 0 and entry_data.credit == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either debit or credit amount must be greater than 0"
                )

            entry = DaybookEntry(
                description=entry_data.description,
                debit=entry_data.debit,
                credit=entry_data.credit,
                category=entry_data.category,
                reference=entry_data.reference
            )

            if entry_data.date:
                entry.date = datetime.fromisoformat(entry_data.date)

            success = excel_sync.add_entry(entry)

            if success:
                return {
                    "success": True,
                    "message": "Entry created successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create entry"
                )

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.put("/api/entries/{entry_id}", response_model=SuccessResponse, tags=["Entries"])
    async def update_entry(entry_id: int, entry_data: EntryUpdate):
        """Update an existing entry"""
        try:
            # Get existing entry
            entries = excel_sync.read_entries()
            existing_entry = None
            for e in entries:
                if e.entry_id == entry_id:
                    existing_entry = e
                    break

            if not existing_entry:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entry not found"
                )

            # Update fields
            entry = DaybookEntry(
                entry_id=entry_id,
                description=entry_data.description if entry_data.description is not None else existing_entry.description,
                debit=entry_data.debit if entry_data.debit is not None else existing_entry.debit,
                credit=entry_data.credit if entry_data.credit is not None else existing_entry.credit,
                category=entry_data.category if entry_data.category is not None else existing_entry.category,
                reference=entry_data.reference if entry_data.reference is not None else existing_entry.reference
            )

            if entry_data.date:
                entry.date = datetime.fromisoformat(entry_data.date)
            else:
                entry.date = existing_entry.date

            success = excel_sync.update_entry(entry_id, entry)

            if success:
                return {
                    "success": True,
                    "message": "Entry updated successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entry not found"
                )

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.delete("/api/entries/{entry_id}", response_model=SuccessResponse, tags=["Entries"])
    async def delete_entry(entry_id: int):
        """Delete an entry"""
        try:
            success = excel_sync.delete_entry(entry_id)

            if success:
                return {
                    "success": True,
                    "message": "Entry deleted successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Entry not found"
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/api/summary", response_model=SummaryResponse, tags=["Summary"])
    async def get_summary():
        """Get summary statistics"""
        try:
            entries = excel_sync.read_entries()

            total_debit = sum(entry.debit for entry in entries)
            total_credit = sum(entry.credit for entry in entries)
            current_balance = entries[-1].balance if entries else 0

            return {
                "success": True,
                "summary": {
                    "total_entries": len(entries),
                    "total_debit": total_debit,
                    "total_credit": total_credit,
                    "current_balance": current_balance
                }
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get("/api/export", tags=["Export"])
    async def export_file_path():
        """Get current Excel file path"""
        return {
            "success": True,
            "file_path": excel_file_path
        }

    return app
