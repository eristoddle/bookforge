# REST API Reference

BookForge provides a comprehensive REST API for generating EPUBs programmatically. This API is perfect for integrating ebook generation into your applications, CI/CD pipelines, or third-party services.

## 🌐 Base URL

```
http://localhost:8000/api/v1
```

## 📋 API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate/github` | POST | Generate EPUB from GitHub repository |
| `/generate/files` | POST | Generate EPUB from uploaded files |
| `/status/{job_id}` | GET | Get job status |
| `/download/{job_id}` | GET | Download generated EPUB |
| `/jobs` | GET | List recent jobs |
| `/jobs/{job_id}` | DELETE | Delete a job |

## 🔐 Authentication

Currently, the API does not require authentication for basic usage. For production deployments, consider adding authentication middleware.

## 📖 Endpoints

### Generate EPUB from GitHub

Generate an EPUB from a GitHub repository containing markdown files.

**Endpoint:** `POST /api/v1/generate/github`

**Request Body:**
```json
{
  "github_url": "https://github.com/username/repository",
  "folder_path": "docs",
  "title": "My Book Title",
  "author": "Author Name",
  "theme": "modern",
  "language": "en",
  "description": "Book description",
  "publisher": "Publisher Name"
}
```

**Parameters:**
- `github_url` (required): GitHub repository URL
- `folder_path` (optional): Specific folder path in the repository
- `title` (optional): Book title (auto-detected if not provided)
- `author` (optional): Author name (auto-detected if not provided)
- `theme` (optional): Theme name (`modern`, `classic`, `minimal`)
- `language` (optional): Language code (default: `en`)
- `description` (optional): Book description
- `publisher` (optional): Publisher name

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "EPUB generation started",
  "status_url": "/api/v1/status/123e4567-e89b-12d3-a456-426614174000"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate/github" \
     -H "Content-Type: application/json" \
     -d '{
       "github_url": "https://github.com/username/my-book",
       "title": "My Amazing Book",
       "author": "Your Name",
       "theme": "modern"
     }'
```

### Generate EPUB from Files

Upload markdown files and generate an EPUB.

**Endpoint:** `POST /api/v1/generate/files`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `title` (required): Book title
- `author` (required): Author name
- `theme` (optional): Theme name (default: `modern`)
- `language` (optional): Language code (default: `en`)
- `description` (optional): Book description
- `publisher` (optional): Publisher name
- `files` (required): One or more markdown files

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "EPUB generation started",
  "status_url": "/api/v1/status/123e4567-e89b-12d3-a456-426614174000"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate/files" \
     -F "title=My Book" \
     -F "author=Author Name" \
     -F "theme=classic" \
     -F "files=@chapter1.md" \
     -F "files=@chapter2.md"
```

### Check Job Status

Get the status of a generation job.

**Endpoint:** `GET /api/v1/status/{job_id}`

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "created_at": "2023-01-01T12:00:00Z",
  "completed_at": "2023-01-01T12:01:30Z",
  "error_message": null,
  "download_url": "/api/v1/download/123e4567-e89b-12d3-a456-426614174000",
  "validation_results": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

**Status Values:**
- `pending`: Job is waiting to be processed
- `processing`: Job is currently being processed
- `completed`: Job completed successfully
- `failed`: Job failed with an error

**Example:**
```bash
curl "http://localhost:8000/api/v1/status/123e4567-e89b-12d3-a456-426614174000"
```

### Download EPUB

Download the generated EPUB file.

**Endpoint:** `GET /api/v1/download/{job_id}`

**Response:** Binary EPUB file with `Content-Type: application/epub+zip`

**Example:**
```bash
curl -O "http://localhost:8000/api/v1/download/123e4567-e89b-12d3-a456-426614174000"
```

### List Jobs

Get a list of recent generation jobs.

**Endpoint:** `GET /api/v1/jobs`

**Query Parameters:**
- `limit` (optional): Maximum number of jobs to return (default: 50)
- `status` (optional): Filter by job status

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "created_at": "2023-01-01T12:00:00Z",
    "completed_at": "2023-01-01T12:01:30Z"
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs?limit=10&status=completed"
```

### Delete Job

Delete a job and its associated files.

**Endpoint:** `DELETE /api/v1/jobs/{job_id}`

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/123e4567-e89b-12d3-a456-426614174000"
```

## 🔄 Workflow Example

Here's a complete workflow for generating an EPUB:

1. **Start Generation:**
   ```bash
   RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/generate/github" \
        -H "Content-Type: application/json" \
        -d '{"github_url": "https://github.com/user/repo", "title": "My Book"}')
   
   JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
   echo "Job ID: $JOB_ID"
   ```

2. **Poll for Completion:**
   ```bash
   while true; do
     STATUS=$(curl -s "http://localhost:8000/api/v1/status/$JOB_ID" | jq -r '.status')
     echo "Status: $STATUS"
     
     if [ "$STATUS" = "completed" ]; then
       break
     elif [ "$STATUS" = "failed" ]; then
       echo "Job failed!"
       exit 1
     fi
     
     sleep 5
   done
   ```

3. **Download EPUB:**
   ```bash
   curl -O "http://localhost:8000/api/v1/download/$JOB_ID"
   echo "EPUB downloaded!"
   ```

## 🐍 Python Client Example

```python
import requests
import time
import json

class BookForgeClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def generate_from_github(self, github_url, **kwargs):
        """Generate EPUB from GitHub repository"""
        data = {"github_url": github_url, **kwargs}
        response = requests.post(f"{self.base_url}/generate/github", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_status(self, job_id):
        """Get job status"""
        response = requests.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def download_epub(self, job_id, filename=None):
        """Download generated EPUB"""
        response = requests.get(f"{self.base_url}/download/{job_id}")
        response.raise_for_status()
        
        if not filename:
            filename = f"book_{job_id[:8]}.epub"
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return filename
    
    def wait_for_completion(self, job_id, timeout=300):
        """Wait for job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)
            
            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Job failed: {status.get('error_message')}")
            
            time.sleep(5)
        
        raise TimeoutError("Job did not complete within timeout")

# Usage example
client = BookForgeClient()

# Generate EPUB
result = client.generate_from_github(
    github_url="https://github.com/user/repo",
    title="My Book",
    author="Author Name",
    theme="modern"
)

job_id = result['job_id']
print(f"Started job: {job_id}")

# Wait for completion
status = client.wait_for_completion(job_id)
print("Job completed!")

# Download EPUB
filename = client.download_epub(job_id)
print(f"Downloaded: {filename}")
```

## ❌ Error Handling

The API returns standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (job or resource not found)
- **422**: Validation Error (invalid input data)
- **500**: Internal Server Error

Error responses include details:
```json
{
  "detail": "Error description"
}
```

## 📊 Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on your needs.

## 🔗 Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI, where you can test endpoints directly from your browser.