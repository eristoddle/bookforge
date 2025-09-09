// BookForge Web Interface JavaScript

class BookForgeUI {
    constructor() {
        this.files = [];
        this.currentJob = null;
        this.pollInterval = null;
        
        this.initializeEventListeners();
        this.loadJobs();
    }

    initializeEventListeners() {
        // File upload
        const fileUpload = document.getElementById('file-upload');
        const fileInput = document.getElementById('file-input');
        
        if (fileUpload && fileInput) {
            // Drag and drop
            fileUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileUpload.classList.add('dragover');
            });
            
            fileUpload.addEventListener('dragleave', () => {
                fileUpload.classList.remove('dragover');
            });
            
            fileUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                fileUpload.classList.remove('dragover');
                this.handleFiles(e.dataTransfer.files);
            });
            
            // Click to upload
            fileUpload.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        // Form submissions
        const githubForm = document.getElementById('github-form');
        const filesForm = document.getElementById('files-form');
        
        if (githubForm) {
            githubForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateFromGitHub();
            });
        }
        
        if (filesForm) {
            filesForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateFromFiles();
            });
        }

        // Theme selection
        const themeInputs = document.querySelectorAll('input[name="theme"]');
        themeInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateThemePreview(input.value);
            });
        });
    }

    handleFiles(fileList) {
        const validFiles = Array.from(fileList).filter(file => {
            const isMarkdown = file.name.toLowerCase().endsWith('.md') || 
                             file.name.toLowerCase().endsWith('.markdown');
            if (!isMarkdown) {
                this.showAlert('Only markdown files (.md, .markdown) are supported', 'warning');
            }
            return isMarkdown;
        });

        this.files = [...this.files, ...validFiles];
        this.updateFileList();
        this.updateFormVisibility();
    }

    updateFileList() {
        const fileList = document.getElementById('file-list');
        if (!fileList) return;

        if (this.files.length === 0) {
            fileList.innerHTML = '<p class="text-muted">No files selected</p>';
            return;
        }

        fileList.innerHTML = this.files.map((file, index) => `
            <div class="file-item">
                <div>
                    <div class="file-item-name">${file.name}</div>
                    <div class="file-item-size">${this.formatFileSize(file.size)}</div>
                </div>
                <div class="file-item-remove" onclick="bookforgeUI.removeFile(${index})">
                    ✕
                </div>
            </div>
        `).join('');
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileList();
        this.updateFormVisibility();
    }

    updateFormVisibility() {
        const filesFormSection = document.getElementById('files-form-section');
        if (filesFormSection) {
            filesFormSection.style.display = this.files.length > 0 ? 'block' : 'none';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async generateFromGitHub() {
        const form = document.getElementById('github-form');
        const formData = new FormData(form);
        
        const data = {
            github_url: formData.get('github_url'),
            folder_path: formData.get('folder_path') || null,
            title: formData.get('title') || null,
            author: formData.get('author') || null,
            theme: formData.get('theme'),
            language: formData.get('language'),
            description: formData.get('description') || null,
            publisher: formData.get('publisher') || null
        };

        try {
            this.showLoading('Connecting to GitHub...');
            
            const response = await fetch('/api/v1/generate/github', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentJob = result.job_id;
                this.showAlert('EPUB generation started! Tracking progress...', 'success');
                this.startJobPolling();
                this.showJobStatus();
            } else {
                throw new Error(result.detail || 'Generation failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error: ${error.message}`, 'error');
        }
    }

    async generateFromFiles() {
        if (this.files.length === 0) {
            this.showAlert('Please select at least one markdown file', 'warning');
            return;
        }

        const form = document.getElementById('files-form');
        const formData = new FormData(form);
        
        // Add files to form data
        this.files.forEach(file => {
            formData.append('files', file);
        });

        try {
            this.showLoading('Processing files...');
            
            const response = await fetch('/api/v1/generate/files', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.currentJob = result.job_id;
                this.showAlert('EPUB generation started! Tracking progress...', 'success');
                this.startJobPolling();
                this.showJobStatus();
            } else {
                throw new Error(result.detail || 'Generation failed');
            }
        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error: ${error.message}`, 'error');
        }
    }

    async startJobPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(async () => {
            if (this.currentJob) {
                await this.checkJobStatus();
            }
        }, 2000);
    }

    async checkJobStatus() {
        try {
            const response = await fetch(`/api/v1/status/${this.currentJob}`);
            const status = await response.json();
            
            if (response.ok) {
                this.updateJobStatusDisplay(status);
                
                if (status.status === 'completed') {
                    this.hideLoading();
                    this.showDownloadButton(status.download_url);
                    this.showValidationResults(status.validation_results);
                    clearInterval(this.pollInterval);
                } else if (status.status === 'failed') {
                    this.hideLoading();
                    this.showAlert(`Generation failed: ${status.error_message}`, 'error');
                    clearInterval(this.pollInterval);
                }
            }
        } catch (error) {
            console.error('Error checking job status:', error);
        }
    }

    updateJobStatusDisplay(status) {
        const statusElement = document.getElementById('job-status');
        if (!statusElement) return;

        const statusIcons = {
            pending: '⏳',
            processing: '⚙️',
            completed: '✅',
            failed: '❌'
        };

        const statusTexts = {
            pending: 'Waiting to start...',
            processing: 'Generating EPUB...',
            completed: 'EPUB generated successfully!',
            failed: 'Generation failed'
        };

        statusElement.innerHTML = `
            <div class="job-status">
                <span class="status-icon status-${status.status}">${statusIcons[status.status]}</span>
                <div>
                    <div><strong>Status:</strong> ${statusTexts[status.status]}</div>
                    <div class="text-small text-muted">Job ID: ${status.id}</div>
                </div>
            </div>
        `;
        
        statusElement.style.display = 'block';
    }

    showDownloadButton(downloadUrl) {
        const downloadSection = document.getElementById('download-section');
        if (downloadSection) {
            downloadSection.innerHTML = `
                <div class="card">
                    <h3>📚 Your EPUB is Ready!</h3>
                    <p>Your ebook has been generated successfully and is ready for download.</p>
                    <a href="${downloadUrl}" class="btn btn-success btn-large" download>
                        📥 Download EPUB
                    </a>
                </div>
            `;
            downloadSection.style.display = 'block';
        }
    }

    showValidationResults(results) {
        if (!results) return;
        
        const validationSection = document.getElementById('validation-section');
        if (validationSection) {
            let html = '<div class="card"><h3>📋 Validation Results</h3>';
            
            if (results.valid) {
                html += '<div class="alert alert-success">✅ EPUB is valid and ready for distribution!</div>';
            } else {
                html += '<div class="alert alert-error">❌ EPUB has validation issues</div>';
            }
            
            if (results.errors && results.errors.length > 0) {
                html += '<h4>Errors:</h4><ul>';
                results.errors.forEach(error => {
                    html += `<li class="text-error">${error}</li>`;
                });
                html += '</ul>';
            }
            
            if (results.warnings && results.warnings.length > 0) {
                html += '<h4>Warnings:</h4><ul>';
                results.warnings.forEach(warning => {
                    html += `<li class="text-warning">${warning}</li>`;
                });
                html += '</ul>';
            }
            
            html += '</div>';
            validationSection.innerHTML = html;
            validationSection.style.display = 'block';
        }
    }

    showJobStatus() {
        const statusSection = document.getElementById('status-section');
        if (statusSection) {
            statusSection.style.display = 'block';
        }
    }

    showLoading(message = 'Processing...') {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.innerHTML = `
                <div class="alert alert-info">
                    <div class="flex flex-center gap-2">
                        <div class="loading">⚙️</div>
                        <span>${message}</span>
                    </div>
                </div>
            `;
            loadingElement.style.display = 'block';
        }
    }

    hideLoading() {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    showAlert(message, type = 'info') {
        const alertsContainer = document.getElementById('alerts');
        if (!alertsContainer) return;

        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} fade-in`;
        alertElement.innerHTML = `
            ${message}
            <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>
        `;
        
        alertsContainer.appendChild(alertElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertElement.parentElement) {
                alertElement.remove();
            }
        }, 5000);
    }

    updateThemePreview(theme) {
        const previews = document.querySelectorAll('.theme-preview');
        previews.forEach(preview => {
            preview.classList.remove('selected');
            if (preview.dataset.theme === theme) {
                preview.classList.add('selected');
            }
        });
    }

    async loadJobs() {
        try {
            const response = await fetch('/api/v1/jobs?limit=10');
            const jobs = await response.json();
            
            this.displayRecentJobs(jobs);
        } catch (error) {
            console.error('Error loading jobs:', error);
        }
    }

    displayRecentJobs(jobs) {
        const jobsSection = document.getElementById('recent-jobs');
        if (!jobsSection || jobs.length === 0) return;

        const jobsHtml = jobs.map(job => {
            const statusIcons = {
                pending: '⏳',
                processing: '⚙️',
                completed: '✅',
                failed: '❌'
            };
            
            const date = new Date(job.created_at).toLocaleString();
            
            return `
                <div class="job-item card">
                    <div class="flex flex-between">
                        <div>
                            <span class="status-icon status-${job.status}">${statusIcons[job.status]}</span>
                            <strong>Job ${job.id.substring(0, 8)}</strong>
                        </div>
                        <div class="text-small text-muted">${date}</div>
                    </div>
                    ${job.status === 'completed' ? 
                        `<a href="/api/v1/download/${job.id}" class="btn btn-secondary btn-small mt-2">Download</a>` : 
                        ''}
                </div>
            `;
        }).join('');

        jobsSection.innerHTML = `
            <div class="card">
                <h3>📊 Recent Jobs</h3>
                ${jobsHtml}
            </div>
        `;
    }
}

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bookforgeUI = new BookForgeUI();
});

// Utility functions
function selectTheme(theme) {
    const input = document.querySelector(`input[value="${theme}"]`);
    if (input) {
        input.checked = true;
        bookforgeUI.updateThemePreview(theme);
    }
}