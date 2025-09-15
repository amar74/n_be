from fastapi import APIRouter, Depends

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.formbricks import FormbricksLoginTokenResponse, SurveyListResponse, SurveyCreateRequest, Survey
from app.services.formbricks import get_formbricks_login_token, get_all_surveys, create_survey

router = APIRouter(prefix="/formbricks", tags=["formbricks"])



@router.get("/login-token", operation_id="getFormbricksLoginToken")
async def get_formbricks_login_token_handler(
    current_user: User = Depends(get_current_user),
) -> FormbricksLoginTokenResponse:
    return await get_formbricks_login_token(current_user)


@router.get(
    "/surveys",
    status_code=200,
    response_model=SurveyListResponse,
    operation_id="getFormbricksSurveys",
)
async def get_formbricks_surveys_handler(
    current_user: User = Depends(get_current_user),
) -> SurveyListResponse:
    """List Formbricks surveys for the current user's organization.

    Uses the organization's configured Formbricks environment ID.
    """
    return await get_all_surveys(current_user.org_id, current_user)


@router.post(
    "/surveys",
    status_code=201,
    operation_id="createFormbricksSurvey",
)
async def create_formbricks_survey_handler(
    payload: SurveyCreateRequest,
    current_user: User = Depends(get_current_user),
) -> Survey:
    """Create a new Formbricks survey in the current user's organization.

    Returns the created survey mapped to our Survey schema.
    """
    return await create_survey(current_user, payload)
