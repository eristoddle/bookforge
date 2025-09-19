# Authentication

## Overview

BookForge supports multiple authentication methods for API access and GitHub integration.

## API Authentication

### API Keys

Generate an API key for programmatic access:

1. Log in to the BookForge web interface
2. Navigate to Settings > API Keys
3. Click "Generate New API Key"
4. Copy and store the key securely

### Using API Keys

#### HTTP Headers
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.bookforge.io/v1/books
```

#### Python API
```python
from bookforge import BookForge

bf = BookForge(api_key="YOUR_API_KEY")
```

#### Environment Variable
```bash
export BOOKFORGE_API_KEY="YOUR_API_KEY"
```

### JWT Tokens

For user-based authentication:

```bash
# Login to get JWT token
curl -X POST https://api.bookforge.io/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer JWT_TOKEN" \
  https://api.bookforge.io/v1/books
```

## GitHub Authentication

### Personal Access Tokens

Generate a GitHub Personal Access Token:

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public repos)
4. Copy the token

### Using GitHub Tokens

#### Command Line
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
bookforge github https://github.com/username/repo
```

#### Python API
```python
from bookforge import BookForge

bf = BookForge()
epub_path = bf.generate_from_github(
    "https://github.com/username/repo",
    token="ghp_xxxxxxxxxxxx"
)
```

#### Configuration File
```yaml
github:
  token: "ghp_xxxxxxxxxxxx"
```

### GitHub App Authentication

For organization-wide access:

1. Create a GitHub App in your organization
2. Install the app on repositories
3. Generate a private key
4. Use JWT authentication

```python
import jwt
import time
from bookforge import BookForge

def generate_jwt_token(app_id, private_key):
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + 600,
        'iss': app_id
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

# Use GitHub App authentication
bf = BookForge()
jwt_token = generate_jwt_token(app_id, private_key)
```

## OAuth 2.0 Flow

For web applications:

### 1. Authorization Request

Redirect users to:
```
https://api.bookforge.io/v1/oauth/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  scope=books:write&
  state=RANDOM_STATE
```

### 2. Handle Callback

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Exchange code for access token
    response = requests.post('https://api.bookforge.io/v1/oauth/token', {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'code': code,
        'grant_type': 'authorization_code'
    })
    
    token_data = response.json()
    access_token = token_data['access_token']
    
    # Use access token with BookForge
    bf = BookForge(api_key=access_token)
    return "Authentication successful!"
```

## Security Best Practices

### API Key Management

1. **Store Securely**: Never commit API keys to version control
2. **Use Environment Variables**: Store keys in environment variables
3. **Rotate Regularly**: Generate new keys periodically
4. **Limit Scope**: Use least-privilege principle

```bash
# Good: Environment variable
export BOOKFORGE_API_KEY="your-key-here"

# Bad: Hard-coded in script
api_key = "your-key-here"  # Don't do this!
```

### GitHub Token Security

1. **Minimal Scopes**: Only request necessary permissions
2. **Token Expiration**: Set appropriate expiration times
3. **Secure Storage**: Use secure credential storage

```yaml
# Good: Reference environment variable
github:
  token: "${GITHUB_TOKEN}"

# Bad: Hard-coded token
github:
  token: "ghp_hardcoded_token"  # Don't do this!
```

## Rate Limiting

### API Rate Limits

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise**: Custom limits

### Handling Rate Limits

```python
from bookforge import BookForge, RateLimitError
import time

bf = BookForge(api_key="YOUR_API_KEY")

def generate_with_retry(input_dir):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return bf.generate_from_directory(input_dir)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.retry_after or 60
                time.sleep(wait_time)
            else:
                raise
```

## Webhook Authentication

### Webhook Secrets

Verify webhook authenticity:

```python
import hmac
import hashlib
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-BookForge-Signature')
    body = request.get_data()
    
    # Verify signature
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, f"sha256={expected_signature}"):
        return "Invalid signature", 401
    
    # Process webhook
    data = request.get_json()
    # ... handle webhook data
    
    return "OK", 200
```