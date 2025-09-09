from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

from .models import GenerationJob
from ..config import get_settings


class JobManager:
    """Manages EPUB generation jobs and their status"""
    
    def __init__(self):
        self.settings = get_settings()
        self.jobs_file = Path(self.settings.temp_dir) / "jobs.json"
        self._jobs: Dict[str, GenerationJob] = {}
        self._load_jobs()
    
    def create_job(self, job: GenerationJob) -> GenerationJob:
        """Create a new generation job"""
        self._jobs[job.id] = job
        self._save_jobs()
        return job
    
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get job by ID"""
        return self._jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: str) -> bool:
        """Update job status"""
        if job_id in self._jobs:
            self._jobs[job_id].status = status
            self._save_jobs()
            return True
        return False
    
    def complete_job(
        self,
        job_id: str,
        output_path: str,
        validation_results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark job as completed"""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.status = "completed"
            job.output_path = output_path
            job.completed_at = datetime.now()
            
            # Store validation results
            if validation_results:
                job.validation_results = validation_results
            
            self._save_jobs()
            return True
        return False
    
    def fail_job(self, job_id: str, error_message: str) -> bool:
        """Mark job as failed"""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            job.status = "failed"
            job.error_message = error_message
            job.completed_at = datetime.now()
            self._save_jobs()
            return True
        return False
    
    def list_jobs(
        self,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[GenerationJob]:
        """List jobs with optional filtering"""
        jobs = list(self._jobs.values())
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        # Apply limit
        return jobs[:limit]
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        if job_id in self._jobs:
            del self._jobs[job_id]
            self._save_jobs()
            return True
        return False
    
    def cleanup_old_jobs(self, days: int = 7) -> int:
        """
        Clean up jobs older than specified days
        Returns number of jobs deleted
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        jobs_to_delete = []
        
        for job_id, job in self._jobs.items():
            if job.created_at.timestamp() < cutoff_date:
                jobs_to_delete.append(job_id)
                
                # Also delete the output file if it exists
                if job.output_path and os.path.exists(job.output_path):
                    try:
                        os.remove(job.output_path)
                    except OSError:
                        pass  # File might be in use or already deleted
        
        for job_id in jobs_to_delete:
            del self._jobs[job_id]
        
        if jobs_to_delete:
            self._save_jobs()
        
        return len(jobs_to_delete)
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get statistics about jobs"""
        total_jobs = len(self._jobs)
        status_counts = {}
        
        for job in self._jobs.values():
            status_counts[job.status] = status_counts.get(job.status, 0) + 1
        
        completed_jobs = [job for job in self._jobs.values() if job.status == "completed"]
        failed_jobs = [job for job in self._jobs.values() if job.status == "failed"]
        
        avg_completion_time = None
        if completed_jobs:
            completion_times = [
                (job.completed_at - job.created_at).total_seconds()
                for job in completed_jobs
                if job.completed_at
            ]
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
        
        return {
            'total_jobs': total_jobs,
            'status_counts': status_counts,
            'success_rate': len(completed_jobs) / max(total_jobs, 1) * 100,
            'average_completion_time_seconds': avg_completion_time
        }
    
    def _load_jobs(self):
        """Load jobs from persistent storage"""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                
                for job_id, job_dict in jobs_data.items():
                    # Convert datetime strings back to datetime objects
                    if job_dict.get('created_at'):
                        job_dict['created_at'] = datetime.fromisoformat(job_dict['created_at'])
                    if job_dict.get('completed_at'):
                        job_dict['completed_at'] = datetime.fromisoformat(job_dict['completed_at'])
                    
                    job = GenerationJob(**job_dict)
                    self._jobs[job_id] = job
                    
            except (json.JSONDecodeError, KeyError, TypeError):
                # If there's an error loading jobs, start with empty dict
                self._jobs = {}
    
    def _save_jobs(self):
        """Save jobs to persistent storage"""
        try:
            jobs_data = {}
            for job_id, job in self._jobs.items():
                job_dict = {
                    'id': job.id,
                    'status': job.status,
                    'error_message': job.error_message,
                    'output_path': job.output_path,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None
                }
                
                # Add validation results if present
                if hasattr(job, 'validation_results') and job.validation_results:
                    job_dict['validation_results'] = job.validation_results
                
                jobs_data[job_id] = job_dict
            
            with open(self.jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2)
                
        except Exception:
            # If we can't save jobs, continue without persistence
            pass