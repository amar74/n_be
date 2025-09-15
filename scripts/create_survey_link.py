import os
import requests

def create_survey_link(email: str, survey_id: str):
    # Retrieve the admin secret from environment variables
    admin_secret = os.getenv("ADMIN_OPS_SECRET")
    if not admin_secret:
        raise ValueError("ADMIN_OPS_SECRET environment variable is not set")

    # Define the request headers
    headers = {
        "x-admin-secret": admin_secret,
        "Content-Type": "application/json"
    }

    # Define the request payload
    payload = {
        "email": email
    }

    # Define the URL
    url = f"http://localhost:3000/api/admin/surveys/{survey_id}/link"

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        print("Survey link created successfully.")
    else:
        print(f"Failed to create survey link. Status code: {response.status_code}, Response: {response.text}")

# Example usage
create_survey_link("alice@example.com", "srv_123")
