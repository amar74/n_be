"""Note services for handling business logic related to meeting notes."""

from datetime import datetime
import uuid

from app.models.note import Note
from app.models.user import User
from app.schemas.note import (
    NoteCreateRequest,
    NoteUpdateRequest,
    NoteCreateResponse,
    NoteListResponse,
    NoteResponse,
    NoteUpdateResponse,
    NoteDeleteResponse
)
from app.utils.error import MegapolisHTTPException
from app.utils.logger import logger


def normalize_datetime(dt: datetime) -> datetime:
    """Remove timezone info from datetime (assuming it's already in UTC)."""
    if dt.tzinfo is not None:
        # Remove timezone info without conversion (assuming already UTC)
        return dt.replace(tzinfo=None)
    return dt


async def create_note(payload: NoteCreateRequest, user: User) -> NoteCreateResponse:
    """Create a new note for the user's organization."""
    
    # Guard clause: Check if user has an organization
    if not user.org_id:
        logger.warning(f"User {user.email} attempted to create note without organization")
        raise MegapolisHTTPException(
            status_code=400,
            message="User must be part of an organization to create notes",
            metadata={"user_id": str(user.id)}
        )

    logger.info(f"Creating note for organization {user.org_id}")
    
    try:
        # Normalize datetime to be timezone-naive for database storage
        normalized_datetime = normalize_datetime(payload.meeting_datetime)
        
        note = await Note.create(
            meeting_title=payload.meeting_title,
            meeting_datetime=normalized_datetime,
            meeting_notes=payload.meeting_notes,
            org_id=user.org_id,
            created_by=user.id,
        )
        
        logger.info(f"Successfully created note {note.id} for organization {user.org_id}")
        
        return NoteCreateResponse(
            id=note.id,
            meeting_title=note.meeting_title,
            meeting_datetime=note.meeting_datetime,
            meeting_notes=note.meeting_notes,
            org_id=note.org_id,
            created_by=note.created_by,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create note for organization {user.org_id}: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to create note",
            metadata={"organization_id": str(user.org_id)}
        )


async def get_notes_for_organization(user: User, page: int = 1, limit: int = 10) -> NoteListResponse:
    """Get all notes for the user's organization with pagination."""
    
    # Guard clause: Check if user has an organization
    if not user.org_id:
        logger.warning(f"User {user.email} attempted to get notes without organization")
        raise MegapolisHTTPException(
            status_code=400,
            message="User must be part of an organization to view notes"
        )

    try:
        offset = (page - 1) * limit
        notes = await Note.get_all_by_org(user.org_id, limit=limit, offset=offset)
        total_count = await Note.count_by_org(user.org_id)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_prev = page > 1
        
        # Convert notes to response objects
        note_responses = [
            NoteResponse(
                id=note.id,
                meeting_title=note.meeting_title,
                meeting_datetime=note.meeting_datetime,
                meeting_notes=note.meeting_notes,
                created_at=note.created_at,
                updated_at=note.updated_at,
                org_id=note.org_id,
                created_by=note.created_by
            )
            for note in notes
        ]
        
        logger.info(f"Retrieved {len(notes)} notes for organization {user.org_id}, page {page}")
        
        return NoteListResponse(
            notes=note_responses,
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Failed to get notes for organization {user.org_id}: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to retrieve notes"
        )


async def get_note_by_id(note_id: uuid.UUID, user: User) -> NoteResponse:
    """Get a specific note by ID, ensuring user has access."""
    
    # Guard clause: Check if user has an organization
    if not user.org_id:
        logger.warning(f"User {user.email} attempted to get note without organization")
        raise MegapolisHTTPException(
            status_code=400,
            message="User must be part of an organization to view notes"
        )

    try:
        note = await Note.get_by_id(note_id, user.org_id)
        
        if not note:
            logger.warning(f"Note {note_id} not found for organization {user.org_id}")
            raise MegapolisHTTPException(
                status_code=404,
                message="Note not found",
                metadata={"note_id": str(note_id)}
            )
        
        logger.info(f"Retrieved note {note_id} for organization {user.org_id}")
        
        return NoteResponse(
            id=note.id,
            meeting_title=note.meeting_title,
            meeting_datetime=note.meeting_datetime,
            meeting_notes=note.meeting_notes,
            org_id=note.org_id,
            created_by=note.created_by,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get note {note_id}: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to retrieve note"
        )


async def update_note(note_id: uuid.UUID, payload: NoteUpdateRequest, user: User) -> NoteUpdateResponse:
    """Update a note, ensuring user has access."""
    
    # Guard clause: Check if user has an organization
    if not user.org_id:
        logger.warning(f"User {user.email} attempted to update note without organization")
        raise MegapolisHTTPException(
            status_code=400,
            message="User must be part of an organization to update notes"
        )

    try:
        note = await Note.get_by_id(note_id, user.org_id)
        
        if not note:
            logger.warning(f"Note {note_id} not found for organization {user.org_id}")
            raise MegapolisHTTPException(
                status_code=404,
                message="Note not found",
                metadata={"note_id": str(note_id)}
            )
        
        # Update fields if provided
        update_data = {}
        if payload.meeting_title is not None:
            update_data['meeting_title'] = payload.meeting_title
        if payload.meeting_datetime is not None:
            update_data['meeting_datetime'] = normalize_datetime(payload.meeting_datetime)
        if payload.meeting_notes is not None:
            update_data['meeting_notes'] = payload.meeting_notes
        
        if not update_data:
            logger.warning(f"No update data provided for note {note_id}")
            raise MegapolisHTTPException(
                status_code=400,
                message="At least one field must be provided for update"
            )
        
        await note.update_fields(**update_data)
        
        logger.info(f"Successfully updated note {note_id} for organization {user.org_id}")
        
        return NoteUpdateResponse(
            id=note.id,
            meeting_title=note.meeting_title,
            meeting_datetime=note.meeting_datetime,
            meeting_notes=note.meeting_notes,
            org_id=note.org_id,
            created_by=note.created_by,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update note {note_id}: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to update note"
        )


async def delete_note(note_id: uuid.UUID, user: User) -> NoteDeleteResponse:
    """Delete a note, ensuring user has access."""
    
    # Guard clause: Check if user has an organization
    if not user.org_id:
        logger.warning(f"User {user.email} attempted to delete note without organization")
        raise MegapolisHTTPException(
            status_code=400,
            message="User must be part of an organization to delete notes"
        )

    try:
        note = await Note.get_by_id(note_id, user.org_id)
        
        if not note:
            logger.warning(f"Note {note_id} not found for organization {user.org_id}")
            raise MegapolisHTTPException(
                status_code=404,
                message="Note not found",
                metadata={"note_id": str(note_id)}
            )
        
        await note.delete()
        
        logger.info(f"Successfully deleted note {note_id} for organization {user.org_id}")
        
        return NoteDeleteResponse(
            message="Note deleted successfully",
            id=note_id
        )
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete note {note_id}: {str(e)}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Failed to delete note"
        )
