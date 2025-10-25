import httpx
import os
from typing import Dict, Any, List, Optional
from app.utils.logger import logger


class FormBricksClient:
    def __init__(self):
        self.disabled = False
        self.base_url = os.getenv("FORMBRICKS_API_URL", "https://app.formbricks.com")
        self.api_key = os.getenv("FORMBRICKS_API_KEY")
        self.environment_id = os.getenv("FORMBRICKS_ENVIRONMENT_ID")
        
        if not self.api_key:
            logger.warning("FORMBRICKS_API_KEY not found - Formbricks features disabled")
            self.disabled = True
            return
        if not self.environment_id:
            logger.warning("FORMBRICKS_ENVIRONMENT_ID not found - Formbricks features disabled")
            self.disabled = True
            return
        
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_survey(
        self,
        name: str,
        questions: List[Dict[str, Any]],
        survey_type: str = "link",
        **kwargs
    ) -> Dict[str, Any]:
        if self.disabled:
            logger.warning("Formbricks client is disabled - skipping survey creation")
            return {"error": "Formbricks client is disabled"}
       
        url = f"{self.base_url}/api/v1/management/surveys"
        
        payload = {
            "environmentId": self.environment_id,
            "name": name,
            "type": survey_type,
            "status": "draft",  # Start as draft
            "questions": questions,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Survey created in Formbricks: {result.get('id')}")
                return result
        except httpx.HTTPError as e:
            logger.error(f"Error creating survey in Formbricks: {str(e)}")
            raise Exception(f"Failed to create survey in Formbricks: {str(e)}")
    
    async def get_survey(self, survey_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/management/surveys/{survey_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching survey from Formbricks: {str(e)}")
            raise Exception(f"Failed to fetch survey: {str(e)}")
    
    async def update_survey(
        self,
        survey_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/management/surveys/{survey_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers=self.headers,
                    json=update_data,
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Survey updated in Formbricks: {survey_id}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error updating survey in Formbricks: {str(e)}")
            raise Exception(f"Failed to update survey: {str(e)}")
    
    async def update_survey_status(self, survey_id: str, status: str) -> Dict[str, Any]:
       
        return await self.update_survey(survey_id, {"status": status})
    
    async def generate_contact_link(
        self,
        survey_id: str,
        contact_id: str,
        expiration_days: Optional[int] = None
    ) -> Dict[str, str]:
       
        url = f"{self.base_url}/api/v2/management/surveys/{survey_id}/contact-links/contacts/{contact_id}"
        
        params = {}
        if expiration_days:
            params["expirationDays"] = expiration_days
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract the link from response
                link = result.get("data", {}).get("link", "")
                logger.info(f"Generated personalized link for contact {contact_id}")
                
                return {"link": link}
        except httpx.HTTPError as e:
            logger.error(f"Error generating contact link: {str(e)}")
            raise Exception(f"Failed to generate contact link: {str(e)}")
    
    async def create_webhook(
        self,
        url: str,
        triggers: List[str],
        survey_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        
        webhook_url = f"{self.base_url}/api/v1/webhooks"
        
        payload = {
            "environmentId": self.environment_id,
            "url": url,
            "triggers": triggers,
            "surveyIds": survey_ids or [],
            "name": "Megapolis Survey Response Webhook",
            "source": "api"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Webhook created in Formbricks: {result.get('id')}")
                return result
        except httpx.HTTPError as e:
            logger.error(f"Error creating webhook: {str(e)}")
            raise Exception(f"Failed to create webhook: {str(e)}")
    
    async def get_responses(
        self,
        survey_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
       
        url = f"{self.base_url}/api/v1/management/surveys/{survey_id}/responses"
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching responses: {str(e)}")
            raise Exception(f"Failed to fetch responses: {str(e)}")


# Singleton instance
formbricks_client = FormBricksClient()
