from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import uuid
from datetime import datetime

from ..core.models import BookMetadata, GenerationJob
from ..core.book_service import BookService
from ..core.job_manager import JobManager


# API Models
class GenerateFromGitHubRequest(BaseModel):
    github_url: str = Field(..., description="GitHub repository URL")
    folder_path: Optional[str] = Field(None, description="Specific folder path in repo")
    title: Optional[str] = Field(None, description="Book title (auto-detected if not provided)")
    author: Optional[str] = Field(None, description="Book author (auto-detected if not provided)")
    theme: str = Field("modern", description="Book theme (modern, classic, minimal)")
    language: str = Field("en", description="Book language")
    description: Optional[str] = Field(None, description="Book description")
    publisher: Optional[str] = Field(None, description="Publisher name")


class GenerateFromFilesRequest(BaseModel):
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    theme: str = Field("modern", description="Book theme")
    language: str = Field("en", description="Book language")
    description: Optional[str] = Field(None, description="Book description")
    publisher: Optional[str] = Field(None, description="Publisher name")


class JobStatus(BaseModel):
    id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    job_id: str
    message: str
    status_url: str


# Initialize services
book_service = BookService()
job_manager = JobManager()

# Router
router = APIRouter(prefix="/api/v1", tags=["epub-generation"])


@router.post("/generate/github", response_model=JobResponse)
async def generate_from_github(
    request: GenerateFromGitHubRequest,
    background_tasks: BackgroundTasks
):
    """Generate EPUB from GitHub repository"""
    try:
        # Create job
        job_id = str(uuid.uuid4())
        job = GenerationJob(
            id=job_id,
            status="pending"
        )
        
        # Store job
        job_manager.create_job(job)
        
        # Start background processing
        background_tasks.add_task(
            process_github_generation,
            job_id,
            request
        )
        
        return JobResponse(
            job_id=job_id,
            message="EPUB generation started",
            status_url=f"/api/v1/status/{job_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/files", response_model=JobResponse)
async def generate_from_files(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(...),
    theme: str = Form("modern"),
    language: str = Form("en"),
    description: Optional[str] = Form(None),
    publisher: Optional[str] = Form(None),
    files: List[UploadFile] = File(...)
):
    """Generate EPUB from uploaded markdown files"""
    try:
        # Validate files
        markdown_files = []
        for file in files:
            if not file.filename.lower().endswith(('.md', '.markdown')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Only markdown files are supported: {file.filename}"
                )
            
            content = await file.read()
            markdown_files.append((file.filename, content.decode('utf-8')))
        
        if not markdown_files:
            raise HTTPException(status_code=400, detail="No valid markdown files provided")
        
        # Create job
        job_id = str(uuid.uuid4())
        job = GenerationJob(
            id=job_id,
            status="pending"
        )
        
        # Store job
        job_manager.create_job(job)
        
        # Create request object
        request_data = GenerateFromFilesRequest(
            title=title,
            author=author,
            theme=theme,
            language=language,
            description=description,
            publisher=publisher
        )
        
        # Start background processing
        background_tasks.add_task(
            process_files_generation,
            job_id,
            request_data,
            markdown_files
        )
        
        return JobResponse(
            job_id=job_id,
            message="EPUB generation started",
            status_url=f"/api/v1/status/{job_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get generation job status"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    download_url = None
    if job.status == "completed" and job.output_path:
        download_url = f"/api/v1/download/{job_id}"
    
    return JobStatus(
        id=job.id,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        download_url=download_url,
        validation_results=getattr(job, 'validation_results', None)
    )


@router.get("/download/{job_id}")
async def download_epub(job_id: str):
    """Download generated EPUB file"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="EPUB not ready for download")
    
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="EPUB file not found")
    
    filename = os.path.basename(job.output_path)
    
    return FileResponse(
        path=job.output_path,
        filename=filename,
        media_type="application/epub+zip"
    )


@router.get("/jobs")
async def list_jobs(limit: int = 50, status: Optional[str] = None):
    """List recent generation jobs"""
    jobs = job_manager.list_jobs(limit=limit, status=status)
    
    return [
        {
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "completed_at": job.completed_at
        }
        for job in jobs
    ]


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a generation job and its files"""
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete output file if exists
    if job.output_path and os.path.exists(job.output_path):
        os.remove(job.output_path)
    
    # Delete job record
    job_manager.delete_job(job_id)
    
    return {"message": "Job deleted successfully"}


# Background task functions
async def process_github_generation(job_id: str, request: GenerateFromGitHubRequest):
    """Background task for GitHub repository processing"""
    try:
        job_manager.update_job_status(job_id, "processing")
        
        # Generate EPUB
        output_path, validation_results = await book_service.generate_from_github(
            github_url=request.github_url,
            folder_path=request.folder_path,
            title=request.title,
            author=request.author,
            theme=request.theme,
            language=request.language,
            description=request.description,
            publisher=request.publisher
        )
        
        # Update job with results
        job_manager.complete_job(job_id, output_path, validation_results)
        
    except Exception as e:
        job_manager.fail_job(job_id, str(e))


async def process_files_generation(
    job_id: str,
    request: GenerateFromFilesRequest,
    markdown_files: List[tuple]
):
    """Background task for uploaded files processing"""
    try:
        job_manager.update_job_status(job_id, "processing")
        
        # Generate EPUB
        output_path, validation_results = await book_service.generate_from_files(
            markdown_files=markdown_files,
            title=request.title,
            author=request.author,
            theme=request.theme,
            language=request.language,
            description=request.description,
            publisher=request.publisher
        )
        
        # Update job with results
        job_manager.complete_job(job_id, output_path, validation_results)
        
    except Exception as e:
        job_manager.fail_job(job_id, str(e))