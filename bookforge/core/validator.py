import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

from ..config import get_settings


class EPUBValidator:
    """EPUB validation using EPUBCheck and other validation tools"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def validate_epub(self, epub_path: str) -> Dict[str, Any]:
        """
        Validate EPUB file and return validation results
        Returns dict with validation status and any errors/warnings
        """
        results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'info': [],
            'file_path': epub_path
        }
        
        try:
            # Try EPUBCheck if available
            epubcheck_result = self._run_epubcheck(epub_path)
            if epubcheck_result:
                results.update(epubcheck_result)
            else:
                # Fallback to basic validation
                basic_result = self._basic_epub_validation(epub_path)
                results.update(basic_result)
                
        except Exception as e:
            results['errors'].append(f"Validation failed: {str(e)}")
        
        results['valid'] = len(results['errors']) == 0
        
        return results
    
    def _run_epubcheck(self, epub_path: str) -> Optional[Dict[str, Any]]:
        """
        Run EPUBCheck validation tool if available
        """
        try:
            # Try to find epubcheck
            epubcheck_commands = [
                'epubcheck',
                'java -jar epubcheck.jar',
                'java -jar /usr/local/bin/epubcheck.jar'
            ]
            
            for cmd_template in epubcheck_commands:
                try:
                    cmd = f"{cmd_template} {epub_path} --json"
                    result = subprocess.run(
                        cmd.split(),
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        # Parse JSON output if available
                        try:
                            output_data = json.loads(result.stdout)
                            return self._parse_epubcheck_output(output_data)
                        except json.JSONDecodeError:
                            # Fallback to text parsing
                            return self._parse_epubcheck_text(result.stdout, result.stderr)
                    
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _parse_epubcheck_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse EPUBCheck JSON output"""
        results = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        for message in output_data.get('messages', []):
            severity = message.get('severity', '').lower()
            text = message.get('message', '')
            location = message.get('locations', [{}])[0]
            
            formatted_msg = text
            if location.get('path'):
                formatted_msg += f" (in {location['path']}"
                if location.get('line'):
                    formatted_msg += f" line {location['line']}"
                formatted_msg += ")"
            
            if severity == 'error' or severity == 'fatal':
                results['errors'].append(formatted_msg)
            elif severity == 'warning':
                results['warnings'].append(formatted_msg)
            else:
                results['info'].append(formatted_msg)
        
        return results
    
    def _parse_epubcheck_text(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse EPUBCheck text output"""
        results = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        output = stdout + stderr
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'ERROR' in line.upper():
                results['errors'].append(line)
            elif 'WARNING' in line.upper():
                results['warnings'].append(line)
            elif 'INFO' in line.upper():
                results['info'].append(line)
        
        return results
    
    def _basic_epub_validation(self, epub_path: str) -> Dict[str, Any]:
        """
        Basic EPUB validation when EPUBCheck is not available
        Checks basic structure and required files
        """
        results = {
            'errors': [],
            'warnings': [],
            'info': ['Using basic validation (EPUBCheck not available)']
        }
        
        try:
            import zipfile
            
            with zipfile.ZipFile(epub_path, 'r') as epub_zip:
                # Check mimetype
                if 'mimetype' not in epub_zip.namelist():
                    results['errors'].append("Missing mimetype file")
                else:
                    mimetype_content = epub_zip.read('mimetype').decode('utf-8').strip()
                    if mimetype_content != 'application/epub+zip':
                        results['errors'].append(f"Invalid mimetype: {mimetype_content}")
                
                # Check container.xml
                if 'META-INF/container.xml' not in epub_zip.namelist():
                    results['errors'].append("Missing META-INF/container.xml")
                
                # Check for content.opf
                opf_files = [f for f in epub_zip.namelist() if f.endswith('.opf')]
                if not opf_files:
                    results['errors'].append("Missing content.opf file")
                
                # Check for navigation files
                nav_files = [f for f in epub_zip.namelist() 
                           if 'nav.xhtml' in f or 'toc.ncx' in f]
                if not nav_files:
                    results['warnings'].append("No navigation files found")
                
                # Check for XHTML files
                xhtml_files = [f for f in epub_zip.namelist() 
                             if f.endswith('.xhtml') or f.endswith('.html')]
                if not xhtml_files:
                    results['warnings'].append("No content files found")
                
                results['info'].append(f"Found {len(xhtml_files)} content files")
                
        except zipfile.BadZipFile:
            results['errors'].append("Invalid ZIP file format")
        except Exception as e:
            results['errors'].append(f"Validation error: {str(e)}")
        
        return results
    
    def install_epubcheck(self) -> bool:
        """
        Attempt to install EPUBCheck for better validation
        Returns True if successful
        """
        try:
            # Try to download EPUBCheck
            import requests
            
            epubcheck_url = "https://github.com/w3c/epubcheck/releases/latest/download/epubcheck.jar"
            install_dir = Path.home() / ".bookforge"
            install_dir.mkdir(exist_ok=True)
            
            epubcheck_path = install_dir / "epubcheck.jar"
            
            if epubcheck_path.exists():
                return True  # Already installed
            
            response = requests.get(epubcheck_url)
            response.raise_for_status()
            
            with open(epubcheck_path, 'wb') as f:
                f.write(response.content)
            
            # Test if it works
            result = subprocess.run([
                'java', '-jar', str(epubcheck_path), '--help'
            ], capture_output=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def get_validation_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable validation summary"""
        if results['valid']:
            return "✅ EPUB is valid and ready for distribution"
        
        summary = []
        
        if results['errors']:
            summary.append(f"❌ {len(results['errors'])} error(s) found:")
            for error in results['errors'][:5]:  # Show first 5 errors
                summary.append(f"  • {error}")
            if len(results['errors']) > 5:
                summary.append(f"  ... and {len(results['errors']) - 5} more errors")
        
        if results['warnings']:
            summary.append(f"⚠️  {len(results['warnings'])} warning(s):")
            for warning in results['warnings'][:3]:  # Show first 3 warnings
                summary.append(f"  • {warning}")
            if len(results['warnings']) > 3:
                summary.append(f"  ... and {len(results['warnings']) - 3} more warnings")
        
        return '\n'.join(summary)