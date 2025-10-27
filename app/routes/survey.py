
from fastapi import APIRouter, HTTPException, Depends, status, Query, Body, BackgroundTasks
from typing import List, Optional
from uuid import UUID
import traceback

from app.schemas.survey import (
    SurveyCreateRequest,
    SurveyResponse,
    SurveyListResponse,
    SurveyStatusUpdate,
    SurveyDistributionCreate,
    SurveyDistributionResponse,
    BulkDistributionResponse,
    SurveyResponseSubmission,
    SurveyResponseModel,
    SurveyAnalyticsSummary,
    SurveyAccountResponse,
    SurveyContactResponse
)
from app.services.survey import survey_service
from app.services.account import account_service
from app.services.contact import contact_service
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.utils.logger import logger


router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    request: SurveyCreateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Creating survey: {request.title} for org: {current_user.org_id}")
        
        survey = await survey_service.create_survey(
            request=request,
            org_id=current_user.org_id,
            created_by=current_user.id
        )
        
        logger.info(f"Survey created successfully: {survey.id}")
        return SurveyResponse.model_validate(survey)
        
    except ValueError as e:
        logger.warning(f"Validation error creating survey: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating survey: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the survey. Please try again."
        )


@router.get("/", response_model=SurveyListResponse)
async def list_surveys(
    status_filter: Optional[str] = Query(None, alias="status"),
    survey_type: Optional[str] = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
   
    try:
        offset = (page - 1) * page_size
        surveys, total = await survey_service.list_surveys(
            org_id=current_user.org_id,
            status=status_filter,
            survey_type=survey_type,
            limit=page_size,
            offset=offset
        )
        
        return SurveyListResponse(
            surveys=[SurveyResponse.model_validate(s) for s in surveys],
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing surveys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list surveys: {str(e)}"
        )


# ========== Survey Distribution Target Endpoints (must be before /{survey_id}) ==========
@router.get("/accounts", response_model=List[SurveyAccountResponse])
async def get_survey_accounts(
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Fetching accounts for survey distribution for org: {current_user.org_id}")
        
        # Get accounts for the organization
        accounts = await account_service.get_accounts_for_organization(current_user.org_id)
        logger.info(f"Found {len(accounts)} accounts from service")
        
        # Format the response with contacts included
        result = []
        for account in accounts:
            try:
                # Get contacts for this account
                contacts = await contact_service.get_contacts_by_account(account.account_id)
                logger.info(f"Account {account.account_id}: found {len(contacts)} contacts")
                
                # Build contacts list - ensure all fields match the schema
                contacts_list = []
                for contact in contacts:
                    try:
                        # Build contact dict - FastAPI will validate against SurveyContactResponse
                        contact_data = {
                            "id": str(contact.id),
                            "name": contact.name if contact.name else "Unnamed Contact",
                            "email": contact.email if contact.email else "no-email@example.com",
                            "title": contact.title if contact.title else ""
                        }
                        contacts_list.append(contact_data)
                        logger.debug(f"Added contact: {contact_data['name']} ({contact_data['email']})")
                    except Exception as contact_err:
                        logger.error(f"Error creating contact response for contact {contact.id}: {str(contact_err)}", exc_info=True)
                        continue
                
                # Build account dict - FastAPI will validate against SurveyAccountResponse
                account_data = {
                    "id": str(account.account_id),
                    "name": account.client_name if account.client_name else "Unnamed Account",
                    "client_type": account.client_type.value if account.client_type else "tier_1",
                    "market_sector": account.market_sector,  # Can be None, which is valid per schema
                    "contacts": contacts_list
                }
                
                result.append(account_data)
                logger.info(f"Successfully added account {account.account_id} with {len(contacts_list)} contacts")
                
            except Exception as e:
                logger.error(f"Error processing account {account.account_id}: {str(e)}", exc_info=True)
                traceback.print_exc()
                continue
        
        logger.info(f"Returning {len(result)} accounts with contacts for survey distribution")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching accounts for survey distribution: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch accounts and contacts: {str(e)}"
        )


# ========== Survey CRUD Endpoints ==========
@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: UUID,
    current_user: User = Depends(get_current_user)
):
    survey = await survey_service.get_survey(survey_id)
    
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey {survey_id} not found"
        )
    
    if survey.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this survey"
        )
    
    return SurveyResponse.model_validate(survey)


@router.patch("/{survey_id}", response_model=SurveyResponse)
async def update_survey(
    survey_id: UUID,
    request: SurveyCreateRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Verify ownership
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey {survey_id} not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this survey"
            )
        
        # Update survey fields
        survey.title = request.title
        survey.description = request.description
        survey.survey_type = SurveyType[request.survey_type.value]
        survey.questions = request.questions
        survey.settings = request.settings
        
        from app.db.session import get_request_transaction
        db = get_request_transaction()
        await db.flush()
        await db.refresh(survey)
        
        logger.info(f"Survey {survey_id} updated successfully")
        return SurveyResponse.model_validate(survey)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating survey: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update survey: {str(e)}"
        )


@router.patch("/{survey_id}/status", response_model=SurveyResponse)
async def update_survey_status(
    survey_id: UUID,
    status_update: SurveyStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        # Verify ownership
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey {survey_id} not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this survey"
            )
        
        updated_survey = await survey_service.update_survey_status(
            survey_id=survey_id,
            status=status_update.status.value
        )
        
        return SurveyResponse.model_validate(updated_survey)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating survey status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update survey status: {str(e)}"
        )


@router.post("/{survey_id}/distribute", response_model=BulkDistributionResponse)
async def distribute_survey(
    survey_id: UUID,
    distribution: SurveyDistributionCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        # Ensure survey_id matches
        distribution.survey_id = survey_id
        
        # Verify survey ownership
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey {survey_id} not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to distribute this survey"
            )
        
        distributions = await survey_service.distribute_survey(
            request=distribution,
            org_id=current_user.org_id
        )
        
        return BulkDistributionResponse(
            success=True,
            message=f"Survey distributed to {len(distributions)} contacts",
            distributions_created=len(distributions),
            distributions=[
                SurveyDistributionResponse.model_validate(d) for d in distributions
            ]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error distributing survey: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to distribute survey: {str(e)}"
        )


@router.get("/{survey_id}/analytics", response_model=SurveyAnalyticsSummary)
async def get_survey_analytics(
    survey_id: UUID,
    current_user: User = Depends(get_current_user)
):
    
    try:
        # Verify ownership
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey {survey_id} not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this survey's analytics"
            )
        
        analytics = await survey_service.get_survey_analytics(survey_id)
        return analytics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting survey analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get survey analytics: {str(e)}"
        )

@router.post("/responses", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_survey_response(
    response_data: SurveyResponseSubmission
):
    try:
        logger.info(f"Received survey response for survey {response_data.survey_id}")
        
        # Create the response in our database
        response = await survey_service.create_survey_response(
            survey_id=response_data.survey_id,
            contact_id=response_data.contact_id,
            account_id=response_data.account_id,
            responses=response_data.responses,
            metadata=response_data.metadata
        )
        
        return {
            "status": "success", 
            "message": "Response submitted successfully",
            "response_id": str(response.id)
        }
        
    except Exception as e:
        logger.error(f"Error submitting survey response: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit survey response"
        )


@router.get("/accounts/{account_id}/contacts", response_model=List[dict])
async def get_account_contacts_for_survey(
    account_id: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        from app.services.contact import contact_service
        contacts = await contact_service.get_contacts_by_account(account_id)
        return [contact.to_dict() for contact in contacts]
    except Exception as e:
        logger.error(f"Error fetching contacts for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch contacts"
        )


@router.get("/{survey_id}/distributions", response_model=List[SurveyDistributionResponse])
async def get_survey_distributions(
    survey_id: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        distributions = await survey_service.get_survey_distributions(survey_id)
        return [SurveyDistributionResponse.model_validate(d) for d in distributions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey distributions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch distributions"
        )


@router.get("/{survey_id}/responses", response_model=List[SurveyResponseModel])
async def get_survey_responses(
    survey_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Fetching responses for survey {survey_id}, page={page}, page_size={page_size}")
        
        survey = await survey_service.get_survey(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.org_id != current_user.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        responses, total = await survey_service.get_survey_responses(
            survey_id, page, page_size
        )
        
        logger.info(f"Found {len(responses)} responses for survey {survey_id}")
        
        # Validate and return responses
        validated_responses = []
        for r in responses:
            try:
                validated = SurveyResponseModel.model_validate(r)
                validated_responses.append(validated)
            except Exception as e:
                logger.error(f"Error validating response {r.id}: {str(e)}", exc_info=True)
                # Continue with other responses
                continue
        
        logger.info(f"Successfully validated {len(validated_responses)} responses")
        return validated_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching survey responses: {str(e)}", exc_info=True)
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch responses: {str(e)}"
        )
