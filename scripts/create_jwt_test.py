import time, jwt
secret = "your-shared-secret"  # must match SSO_JWT_SECRET
EMAIL = "rishabhgautam@gmail.com"
NAME = "Rishabh"
now = int(time.time())


EMAIL = "rishabh@admin.com"
NAME = "Jane"


payload = {
  "email": EMAIL,
  "name": NAME,
  "iat": now,
  "exp": now + 600,
  "iss": "my-python-app",   # omit if you didn’t set SSO_JWT_ISSUER
  "aud": "heyform"          # omit if you didn’t set SSO_JWT_AUDIENCE
}
print(jwt.encode(payload, secret, algorithm="HS256"))