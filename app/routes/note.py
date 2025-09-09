from fastapi import APIRouter, Depends, Query
from typing import Annotated
import uuid

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.note import (
    NoteCreateRequest,
    NoteUpdateRequest,
    NoteResponse,
    NoteListResponse,
    NoteCreateResponse,
    NoteUpdateResponse,
    NoteDeleteResponse,
)
from app.services.note import (
    create_note,
    get_notes_for_organization,
    get_note_by_id,
    update_note,
    delete_note,
)
from app.utils.logger import logger

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "/",
    response_model=NoteCreateResponse,
    status_code=201,
    operation_id="createNote"
)
async def create_note_route(
    payload: NoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)]
) -> NoteCreateResponse:
    """Create a new meeting note for the user's organization."""
    logger.info(f"POST /notes - Creating note for user {current_user.email}")
    note = await create_note(payload, current_user)
    return note


@router.get(
    "/",
    response_model=NoteListResponse,
    status_code=200,
    operation_id="getNotes"
)
async def get_notes_route(
    current_user: Annotated[User, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1, description="Page number (starting from 1)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of notes per page (1-100)")] = 10,
) -> NoteListResponse:
    """Get all meeting notes for the user's organization with pagination."""
    logger.info(f"GET /notes - Fetching notes for user {current_user.email}, page {page}, limit {limit}")
    notes = await get_notes_for_organization(current_user, page=page, limit=limit)
    return notes


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    status_code=200,
    operation_id="getNoteById"
)
async def get_note_by_id_route(
    note_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)]
) -> NoteResponse:
    """Get a specific meeting note by ID within the user's organization."""
    logger.info(f"GET /notes/{note_id} - Fetching note for user {current_user.email}")
    note = await get_note_by_id(note_id, current_user)
    return note


@router.put(
    "/{note_id}",
    response_model=NoteUpdateResponse,
    status_code=200,
    operation_id="updateNote"
)
async def update_note_route(
    note_id: uuid.UUID,
    payload: NoteUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)]
) -> NoteUpdateResponse:
    """Update a meeting note within the user's organization."""
    logger.info(f"PUT /notes/{note_id} - Updating note for user {current_user.email}")
    note = await update_note(note_id, payload, current_user)
    return note


@router.delete(
    "/{note_id}",
    response_model=NoteDeleteResponse,
    status_code=200,
    operation_id="deleteNote"
)
async def delete_note_route(
    note_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)]
) -> NoteDeleteResponse:
    """Delete a meeting note within the user's organization."""
    logger.info(f"DELETE /notes/{note_id} - Deleting note for user {current_user.email}")
    result = await delete_note(note_id, current_user)
    return result
