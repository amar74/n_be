import json
import requests

BASE_URL = "http://localhost:3000"  # change me
ADMIN_SECRET = "password"           # set to your ADMIN_OPS_SECRET
ORG_ID = "cmey3wcax0015ihytodpgsla2"            # change me

def main():
	url = f"{BASE_URL.rstrip('/')}/api/v2/admin/organizations/{ORG_ID}/users"
	headers = {
		"Content-Type": "application/json",
		"x-admin-secret": ADMIN_SECRET,
	}
	payload = {
		"name": "Admin",          # change me
		"email": "rishabh@admin.com",      # change me
		"role": "manager",               # owner | manager | member
		"isActive": True,              # optional
		"teams": []
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
#     "id": "cmey3xlxm0016ihytzxrtwtwb",
#     "createdAt": "2025-08-30T10:16:59.723Z",
#     "updatedAt": "2025-08-30T10:16:59.723Z",
#     "email": "rishabh@admin.com",
#     "name": "Admin",
#     "lastLoginAt": null,
#     "isActive": true,
#     "role": "manager",
#     "teams": []
#   }
# }