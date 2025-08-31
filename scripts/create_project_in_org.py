import json
import requests

BASE_URL = "http://localhost:3000"  # change me
ADMIN_SECRET = "password"           # set to your ADMIN_OPS_SECRET
ORG_ID = "cmey3wcax0015ihytodpgsla2"            # change me

def main():
	url = f"{BASE_URL.rstrip('/')}/api/v2/admin/organizations/{ORG_ID}/projects"
	headers = {
		"Content-Type": "application/json",
		"x-admin-secret": ADMIN_SECRET,
	}
	# Minimum required: name
	# You can add any supported fields (styling, config, branding, placement, logo, teamIds, etc.)
	payload = {
		"name": "Acme Forms",  # change me
		"styling": {
			"allowStyleOverwrite": True,
			"brandColor": {"light": "#FFA500"}  # optional
		},
		"config": {"channel": "website", "industry": "saas"},  # optional
		# "inAppSurveyBranding": True,   # optional
		"linkSurveyBranding": True,    # optional
		# "placement": "bottomRight",    # optional
		# "clickOutsideClose": True,     # optional
		# "darkOverlay": False,          # optional
		"logo": {"url": "https://cdn.example.com/logo.png"},  # optional
		"teamIds": []  # optional: IDs of teams to link to the project
	}
	resp = requests.post(url, headers=headers, json=payload, timeout=60)
	print("Status:", resp.status_code)
	try:
		print(json.dumps(resp.json(), indent=2))
	except Exception:
		print(resp.text)

if __name__ == "__main__":
	main()