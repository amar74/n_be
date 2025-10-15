from fastapi import APIRouter, Depends

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.formbricks import (
    FormbricksLoginTokenResponse,
    SurveyListResponse,
    SurveyCreateRequest,
    Survey,
    SurveyLinkCreateRequest,
    SurveyLinkResponse,
)
from app.services.formbricks import (
    get_formbricks_login_token,
    get_all_surveys,
    create_survey,
    create_survey_link,
)

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
    
    return await create_survey(current_user, payload)

@router.post(
    "/surveys/{survey_id}/link",
    status_code=200,
    response_model=SurveyLinkResponse,
    operation_id="createFormbricksSurveyLink",
)
async def create_formbricks_survey_link_handler(
    survey_id: str,
    payload: SurveyLinkCreateRequest,
    current_user: User = Depends(get_current_user),
) -> SurveyLinkResponse:
    
    return await create_survey_link(current_user, survey_id, payload)
