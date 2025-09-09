# CI/CD Integration Examples

Integrate BookForge into your continuous integration and deployment pipelines for automated ebook generation.

## 🚀 GitHub Actions

### Example 1: Documentation Auto-Build

Automatically generate an EPUB whenever documentation is updated.

```yaml
# .github/workflows/epub-build.yml
name: Generate Documentation EPUB

on:
  push:
    branches: [main]
    paths: ['docs/**']
  pull_request:
    paths: ['docs/**']

jobs:
  generate-epub:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install BookForge
      run: |
        pip install bookforge
        
    - name: Generate EPUB
      run: |
        bookforge generate docs/ \
          --title "${{ github.repository }} Documentation" \
          --author "${{ github.repository_owner }}" \
          --theme modern \
          --description "Auto-generated documentation for ${{ github.repository }}" \
          --output documentation.epub
          
    - name: Upload EPUB artifact
      uses: actions/upload-artifact@v3
      with:
        name: documentation-epub
        path: documentation.epub
        
    - name: Create Release (on tag)
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: documentation.epub
```

### Example 2: Multi-Format Publishing

Generate EPUBs for different audiences.

```yaml
# .github/workflows/multi-format.yml
name: Multi-Format Book Generation

on:
  push:
    tags: ['v*']

jobs:
  generate-books:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        book:
          - path: "user-guide"
            title: "User Guide"
            theme: "minimal"
            audience: "users"
          - path: "developer-docs"
            title: "Developer Documentation"
            theme: "modern"
            audience: "developers"
          - path: "admin-manual"
            title: "Administrator Manual"
            theme: "classic"
            audience: "admins"
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install BookForge
      run: pip install bookforge
      
    - name: Generate EPUB for ${{ matrix.book.title }}
      run: |
        bookforge generate ${{ matrix.book.path }}/ \
          --title "${{ matrix.book.title }}" \
          --author "Documentation Team" \
          --theme ${{ matrix.book.theme }} \
          --output "${{ matrix.book.audience }}-guide.epub"
          
    - name: Upload to release
      uses: softprops/action-gh-release@v1
      with:
        files: "${{ matrix.book.audience }}-guide.epub"
```

### Example 3: BookForge API Integration

Use the BookForge API in workflows.

```yaml
# .github/workflows/api-integration.yml
name: API-Based EPUB Generation

on:
  workflow_dispatch:
    inputs:
      repo_url:
        description: 'Repository URL'
        required: true
        default: 'https://github.com/owner/repo'

jobs:
  generate-via-api:
    runs-on: ubuntu-latest
    
    services:
      bookforge:
        image: bookforge/bookforge:latest
        ports:
          - 8000:8000
    
    steps:
    - name: Wait for BookForge service
      run: |
        timeout 30s bash -c 'until curl -f http://localhost:8000/health; do sleep 1; done'
        
    - name: Generate EPUB via API
      run: |
        JOB_ID=$(curl -s -X POST "http://localhost:8000/api/v1/generate/github" \
          -H "Content-Type: application/json" \
          -d '{
            "github_url": "${{ github.event.inputs.repo_url }}",
            "title": "Generated Book",
            "author": "${{ github.actor }}",
            "theme": "modern"
          }' | jq -r '.job_id')
        
        echo "Job ID: $JOB_ID"
        
        # Poll for completion
        while true; do
          STATUS=$(curl -s "http://localhost:8000/api/v1/status/$JOB_ID" | jq -r '.status')
          echo "Status: $STATUS"
          
          if [ "$STATUS" = "completed" ]; then
            curl -o generated-book.epub "http://localhost:8000/api/v1/download/$JOB_ID"
            break
          elif [ "$STATUS" = "failed" ]; then
            echo "Generation failed!"
            exit 1
          fi
          
          sleep 5
        done
        
    - name: Upload generated EPUB
      uses: actions/upload-artifact@v3
      with:
        name: generated-epub
        path: generated-book.epub
```

## 🏗️ Jenkins Pipeline

### Example 1: Documentation Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        BOOKFORGE_OUTPUT_DIR = 'build/epubs'
        REPO_NAME = "${env.JOB_NAME}".split('/')[0]
    }
    
    triggers {
        // Build on documentation changes
        pollSCM('H/5 * * * *')
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    sh 'pip install bookforge'
                    sh "mkdir -p ${BOOKFORGE_OUTPUT_DIR}"
                }
            }
        }
        
        stage('Generate EPUB') {
            steps {
                script {
                    sh """
                        bookforge generate docs/ \
                            --title "${REPO_NAME} Documentation" \
                            --author "DevOps Team" \
                            --theme modern \
                            --output ${BOOKFORGE_OUTPUT_DIR}/${REPO_NAME}-docs.epub
                    """
                }
            }
        }
        
        stage('Validate') {
            steps {
                script {
                    sh """
                        if [ -f ${BOOKFORGE_OUTPUT_DIR}/${REPO_NAME}-docs.epub ]; then
                            echo "✅ EPUB generated successfully"
                            ls -la ${BOOKFORGE_OUTPUT_DIR}/
                        else
                            echo "❌ EPUB generation failed"
                            exit 1
                        fi
                    """
                }
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: "${BOOKFORGE_OUTPUT_DIR}/*.epub", fingerprint: true
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: BOOKFORGE_OUTPUT_DIR,
                    reportFiles: '*.epub',
                    reportName: 'Generated EPUBs'
                ])
            }
        }
        
        stage('Deploy to S3') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                        aws s3 cp ${BOOKFORGE_OUTPUT_DIR}/${REPO_NAME}-docs.epub \
                            s3://company-docs-bucket/epubs/ \
                            --content-type "application/epub+zip"
                    """
                }
            }
        }
    }
    
    post {
        success {
            slackSend channel: '#dev-docs',
                     color: 'good',
                     message: "📚 EPUB generated successfully for ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}"
        }
        
        failure {
            slackSend channel: '#dev-docs',
                     color: 'danger',
                     message: "❌ EPUB generation failed for ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}"
        }
    }
}
```

### Example 2: Multi-Branch Pipeline

```groovy
// Multi-branch Jenkinsfile
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'THEME',
            choices: ['modern', 'classic', 'minimal'],
            description: 'EPUB theme to use'
        )
        booleanParam(
            name: 'VALIDATE_EPUB',
            defaultValue: true,
            description: 'Run EPUB validation'
        )
    }
    
    stages {
        stage('Generate Branch Documentation') {
            steps {
                script {
                    def branchName = env.BRANCH_NAME ?: 'unknown'
                    def validateFlag = params.VALIDATE_EPUB ? '--validate' : '--no-validate'
                    
                    sh """
                        bookforge generate docs/ \
                            --title "${env.JOB_NAME} Docs (${branchName})" \
                            --author "Team ${branchName}" \
                            --theme ${params.THEME} \
                            --description "Documentation for ${branchName} branch" \
                            ${validateFlag} \
                            --output docs-${branchName}.epub
                    """
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                expression { params.VALIDATE_EPUB }
            }
            steps {
                script {
                    sh """
                        if bookforge preview docs/ | grep -q "Total chapters: 0"; then
                            echo "❌ No content found in documentation"
                            exit 1
                        fi
                    """
                }
            }
        }
    }
}
```

## 🐳 Docker Integration

### Example 1: Containerized Generation

```dockerfile
# Dockerfile for EPUB generation
FROM python:3.9-slim

# Install BookForge
RUN pip install bookforge

# Create working directory
WORKDIR /workspace

# Copy documentation
COPY docs/ ./docs/

# Generate EPUB
RUN bookforge generate docs/ \
    --title "Containerized Documentation" \
    --author "DevOps Team" \
    --theme modern \
    --output /output/documentation.epub

# Volume for output
VOLUME ["/output"]

CMD ["echo", "EPUB generated in /output/"]
```

### Example 2: Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  bookforge-api:
    image: bookforge/bookforge:latest
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - EPUB_VALIDATION=true
    volumes:
      - ./generated_epubs:/app/generated_epubs
      - ./temp_books:/app/temp_books
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  epub-generator:
    build: .
    depends_on:
      - bookforge-api
    volumes:
      - ./docs:/workspace/docs
      - ./output:/output
    command: |
      bash -c "
        echo 'Waiting for BookForge API...'
        until curl -f http://bookforge-api:8000/health; do sleep 1; done
        echo 'Generating EPUB...'
        bookforge generate docs/ \
          --title 'Development Documentation' \
          --author 'Dev Team' \
          --output /output/dev-docs.epub
      "
```

## ⚙️ GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - generate
  - deploy

variables:
  EPUB_OUTPUT_DIR: "generated-epubs"

validate-docs:
  stage: validate
  image: python:3.9
  before_script:
    - pip install bookforge
  script:
    - bookforge preview docs/
    - echo "Documentation structure validated"
  only:
    changes:
      - docs/**/*

generate-epub:
  stage: generate
  image: python:3.9
  before_script:
    - pip install bookforge
    - mkdir -p $EPUB_OUTPUT_DIR
  script:
    - |
      bookforge generate docs/ \
        --title "$CI_PROJECT_NAME Documentation" \
        --author "$GITLAB_USER_NAME" \
        --theme modern \
        --description "Generated from commit $CI_COMMIT_SHORT_SHA" \
        --output $EPUB_OUTPUT_DIR/documentation.epub
  artifacts:
    paths:
      - $EPUB_OUTPUT_DIR/
    expire_in: 1 week
  only:
    - main
    - develop

deploy-to-pages:
  stage: deploy
  dependencies:
    - generate-epub
  script:
    - mkdir public
    - cp $EPUB_OUTPUT_DIR/* public/
    - echo "EPUB available for download" > public/index.html
  artifacts:
    paths:
      - public
  only:
    - main
```

## 🚢 Kubernetes CronJob

```yaml
# epub-generator-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: documentation-epub-generator
  namespace: docs
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: epub-generator
            image: bookforge/bookforge:latest
            env:
            - name: GITHUB_TOKEN
              valueFrom:
                secretKeyRef:
                  name: github-token
                  key: token
            command:
            - /bin/bash
            - -c
            - |
              bookforge github https://github.com/company/docs \
                --title "Company Documentation" \
                --author "Documentation Team" \
                --theme modern \
                --output /shared/company-docs-$(date +%Y%m%d).epub
              
              # Upload to S3 or other storage
              aws s3 cp /shared/company-docs-$(date +%Y%m%d).epub \
                s3://company-docs/latest/
            volumeMounts:
            - name: shared-storage
              mountPath: /shared
          volumes:
          - name: shared-storage
            persistentVolumeClaim:
              claimName: docs-storage
          restartPolicy: OnFailure
```

## 📊 Monitoring and Notifications

### Slack Integration

```bash
#!/bin/bash
# slack-notify.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
JOB_STATUS=$1
EPUB_FILE=$2

if [ "$JOB_STATUS" = "success" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"📚 EPUB Generation Complete\",
            \"attachments\": [{
                \"color\": \"good\",
                \"fields\": [{
                    \"title\": \"File\",
                    \"value\": \"$EPUB_FILE\",
                    \"short\": true
                }, {
                    \"title\": \"Status\",
                    \"value\": \"✅ Success\",
                    \"short\": true
                }]
            }]
        }" \
        $WEBHOOK_URL
else
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"❌ EPUB Generation Failed\",
            \"attachments\": [{
                \"color\": \"danger\",
                \"fields\": [{
                    \"title\": \"Error\",
                    \"value\": \"$EPUB_FILE\",
                    \"short\": false
                }]
            }]
        }" \
        $WEBHOOK_URL
fi
```

### Usage in Pipeline

```bash
# In your CI script
if bookforge generate docs/ --title "My Book" --output book.epub; then
    ./slack-notify.sh success "book.epub"
else
    ./slack-notify.sh failed "Generation error occurred"
fi
```

## 🔧 Best Practices for CI/CD

1. **Cache Dependencies**: Cache pip packages to speed up builds
2. **Parallel Builds**: Generate multiple formats simultaneously
3. **Validation Gates**: Always validate EPUBs before deployment
4. **Artifact Management**: Store EPUBs with version tags
5. **Monitoring**: Set up alerts for failed generations
6. **Security**: Use secrets for API tokens and credentials
7. **Testing**: Test with sample content before production
8. **Rollback**: Keep previous versions available
9. **Documentation**: Document your pipeline configuration
10. **Performance**: Monitor generation times and optimize

These examples show how BookForge integrates seamlessly into any CI/CD pipeline, enabling automated, high-quality ebook generation as part of your development workflow.