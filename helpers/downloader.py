import asyncio
import os
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class Aria2Downloader:
    """Aria2c downloader for faster downloads"""
    
    def __init__(self):
        self.aria2_path = "aria2c"
        
    async def download_file(self, url: str, output_path: str, progress_tracker=None) -> Optional[str]:
        """Download file using aria2c for faster downloads"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.aria2_path,
                '--max-connection-per-server=16',
                '--split=16',
                '--min-split-size=1M',
                '--max-concurrent-downloads=1',
                '--disable-ipv6=true',
                '--summary-interval=1',
                '--download-result=hide',
                '--console-log-level=error',
                '--dir', os.path.dirname(output_path),
                '--out', os.path.basename(output_path),
                url
            ]
            
            logger.info(f"Starting aria2c download with enhanced performance settings: {url}")
            logger.info(f"Using 16 connections with 16 splits for optimal download speed")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress if tracker provided
            if progress_tracker:
                total_steps = 100
                for i in range(total_steps):
                    if process.returncode is not None:
                        break
                    await asyncio.sleep(0.1)
                    if i % 10 == 0:  # Update every 10 steps
                        try:
                            await progress_tracker.update_progress(f"download_{output_path}", i * 1024 * 1024)
                        except:
                            pass
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Download completed successfully: {output_path}")
                logger.info(f"Downloaded file size: {file_size / (1024*1024):.2f} MB")
                return output_path
            else:
                logger.error(f"Aria2c download failed (return code: {process.returncode})")
                if stderr:
                    logger.error(f"Aria2c stderr: {stderr.decode()}")
                if stdout:
                    logger.info(f"Aria2c stdout: {stdout.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error using aria2c downloader: {e}")
            return None
    
    def check_aria2_installed(self) -> bool:
        """Check if aria2c is installed and accessible"""
        try:
            import subprocess
            result = subprocess.run([self.aria2_path, '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

class FileCleanup:
    """Enhanced file cleanup utility"""
    
    @staticmethod
    def cleanup_files(file_paths, delay_seconds: int = 5):
        """Clean up files with optional delay"""
        async def delayed_cleanup():
            await asyncio.sleep(delay_seconds)
            for path in file_paths if isinstance(file_paths, list) else [file_paths]:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                        logger.info(f"Cleaned up file: {path}")
                except Exception as e:
                    logger.error(f"Failed to cleanup file {path}: {e}")
        
        # Schedule cleanup as a background task
        asyncio.create_task(delayed_cleanup())
    
    @staticmethod
    def cleanup_directory(directory: str, pattern: str = "*", max_age_hours: int = 24):
        """Clean up files in directory older than specified hours"""
        try:
            import glob
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (max_age_hours * 3600)
            
            pattern_path = os.path.join(directory, pattern)
            files = glob.glob(pattern_path)
            
            cleaned_count = 0
            for file_path in files:
                try:
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to cleanup old file {file_path}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning directory {directory}: {e}")
            return 0