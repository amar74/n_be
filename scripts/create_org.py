import json
import requests

BASE_URL = "http://localhost:3000"  # change me
ADMIN_SECRET = "password"           # set to your ADMIN_OPS_SECRET

def main():
	url = f"{BASE_URL.rstrip('/')}/api/v2/admin/organizations"
	headers = {
		"Content-Type": "application/json",
		"x-admin-secret": ADMIN_SECRET,
	}
	payload = {
		"name": "ACME ORG"  # change me
	}
	resp = requests.post(url, headers=headers, json=payload, timeout=30)
	print("Status:", resp.status_code)
	try:
		print(json.dumps(resp.json(), indent=2))
	except Exception:
		print(resp.text)

if __name__ == "__main__":
	main()


# {
#   "data": {
#     "id": "cmey3wcax0015ihytodpgsla2",
#     "createdAt": "2025-08-30T10:16:00.586Z",
#     "updatedAt": "2025-08-30T10:16:00.586Z",
#     "name": "ACME ORG",
#     "billing": {
#       "plan": "free",
#       "limits": {
#         "monthly": {
#           "miu": 2000,
#           "responses": 1500
#         },
#         "projects": 3
#       },
#       "period": "monthly",
#       "periodStart": "2025-08-30T10:16:00.585Z",
#       "stripeCustomerId": null
#     },
#     "isAIEnabled": false,
#     "whitelabel": {}
#   }
# }