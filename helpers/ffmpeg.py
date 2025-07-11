import asyncio
import os
import subprocess
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class FFmpegProcessor:
    """FFmpeg video processor for various operations"""
    
    def __init__(self):
        self.ffmpeg_path = Config.FFMPEG_PATH
        self.ffprobe_path = Config.FFPROBE_PATH
    
    async def process_video(self, input_path: str, operation: str, process_id: str, progress_tracker=None) -> Optional[str]:
        """Process video based on operation type"""
        try:
            # Parse operation and parameters
            base_operation, params = self._parse_operation(operation)
            
            # Set output path based on operation type
            if base_operation == "extract_audio":
                output_path = f"{Config.UPLOADS_DIR}/{process_id}_{operation}.mp3"
            elif base_operation == "screenshot":
                output_path = f"{Config.UPLOADS_DIR}/{process_id}_{operation}.jpg"
            else:
                output_path = f"{Config.UPLOADS_DIR}/{process_id}_{operation}.mp4"
            
            # Select processing method based on operation
            if base_operation == "trim":
                return await self.trim_video(input_path, output_path, progress_tracker, params)
            elif base_operation == "compress":
                return await self.compress_video(input_path, output_path, progress_tracker, params)
            elif base_operation == "rotate":
                return await self.rotate_video(input_path, output_path, progress_tracker, params)
            elif base_operation == "mute":
                return await self.mute_video(input_path, output_path, progress_tracker)
            elif base_operation == "reverse":
                return await self.reverse_video(input_path, output_path, progress_tracker)
            elif base_operation == "extract_audio":
                return await self.extract_audio(input_path, output_path, progress_tracker, params)
            elif base_operation == "screenshot":
                return await self.take_screenshot(input_path, output_path, progress_tracker, params)
            elif base_operation == "watermark":
                return await self.add_watermark(input_path, output_path, progress_tracker, params)
            elif base_operation == "resolution":
                return await self.change_resolution(input_path, output_path, progress_tracker, params)
            elif base_operation == "replace_audio":
                return await self.replace_audio(input_path, output_path, progress_tracker)
            elif base_operation == "merge":
                return await self.merge_videos(input_path, output_path, progress_tracker)
            elif base_operation == "subtitles":
                return await self.add_subtitles(input_path, output_path, progress_tracker, params)
            else:
                logger.error(f"Unknown operation: {operation}")
                return None
                
        except Exception as e:
            logger.error(f"Error in process_video: {e}")
            return None
    
    def _parse_operation(self, operation: str) -> tuple:
        """Parse operation string into base operation and parameters"""
        # Handle specific operation variants  
        if operation.startswith("trim_"):
            if "custom" in operation:
                return "trim", {"duration": 30}  # Default for custom
            # Check for exact matches first, then numeric patterns
            elif operation == "trim_600":
                return "trim", {"duration": 600}
            elif operation == "trim_300":
                return "trim", {"duration": 300}
            elif operation == "trim_60":
                return "trim", {"duration": 60}
            elif operation == "trim_30":
                return "trim", {"duration": 30}
            else:
                # Try to extract numeric duration from custom operations like "trim_120"
                parts = operation.split("_")
                if len(parts) >= 2:
                    try:
                        duration = int(parts[-1])
                        return "trim", {"duration": duration}
                    except ValueError:
                        pass
                return "trim", {"duration": 30}
        
        elif operation.startswith("compress_"):
            if "high" in operation:
                return "compress", {"quality": "high", "crf": "18"}
            elif "medium" in operation:
                return "compress", {"quality": "medium", "crf": "23"}
            elif "small" in operation:
                return "compress", {"quality": "small", "crf": "28"}
            elif "tiny" in operation:
                return "compress", {"quality": "tiny", "crf": "35"}
            else:
                return "compress", {"quality": "medium", "crf": "23"}
        
        elif operation.startswith("rotate_"):
            if "90" in operation:
                return "rotate", {"angle": "90"}
            elif "180" in operation:
                return "rotate", {"angle": "180"}
            elif "270" in operation:
                return "rotate", {"angle": "270"}
            elif "flip_h" in operation:
                return "rotate", {"angle": "flip_h"}
            elif "flip_v" in operation:
                return "rotate", {"angle": "flip_v"}
            else:
                return "rotate", {"angle": "90"}
        
        elif operation.startswith("screenshot_"):
            if "multi_3" in operation:
                return "screenshot", {"count": 3}
            elif "multi_5" in operation:
                return "screenshot", {"count": 5}
            elif "multi_10" in operation:
                return "screenshot", {"count": 10}
            elif "hd" in operation:
                return "screenshot", {"count": 1, "quality": "hd"}
            elif "single" in operation:
                return "screenshot", {"count": 1}
            else:
                return "screenshot", {"count": 1}
        
        elif operation.startswith("extract_audio_"):
            if "mp3_high" in operation:
                return "extract_audio", {"format": "mp3", "quality": "high"}
            elif "mp3_medium" in operation:
                return "extract_audio", {"format": "mp3", "quality": "medium"}
            elif "mp3_low" in operation:
                return "extract_audio", {"format": "mp3", "quality": "low"}
            elif "wav" in operation:
                return "extract_audio", {"format": "wav", "quality": "high"}
            else:
                return "extract_audio", {"format": "mp3", "quality": "medium"}
        
        elif operation.startswith("resolution_"):
            if "480p" in operation:
                return "resolution", {"width": 854, "height": 480}
            elif "720p" in operation:
                return "resolution", {"width": 1280, "height": 720}
            elif "1080p" in operation:
                return "resolution", {"width": 1920, "height": 1080}
            elif "1440p" in operation:
                return "resolution", {"width": 2560, "height": 1440}
            elif "4k" in operation:
                return "resolution", {"width": 3840, "height": 2160}
            else:
                return "resolution", {"width": 1280, "height": 720}
        
        elif operation.startswith("watermark_"):
            if "timestamp" in operation:
                return "watermark", {"type": "timestamp"}
            elif "text" in operation:
                return "watermark", {"type": "text"}
            else:
                return "watermark", {"type": "text"}
        
        elif operation.startswith("subtitles_"):
            if "sample" in operation:
                return "subtitles", {"type": "sample"}
            else:
                return "subtitles", {"type": "sample"}
        
        # For basic operations, return as-is
        return operation, {}
    
    async def trim_video(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Trim video with specified duration"""
        try:
            duration = params.get("duration", 30) if params else 30
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-ss', '0',
                '-t', str(duration),
                '-c', 'copy',
                '-avoid_negative_ts', 'make_zero',
                '-y', output_path
            ]
            
            logger.info(f"Trimming video to {duration}s: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Trimming successful: {output_path}")
                return output_path
            else:
                logger.error("Trimming failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error trimming video: {e}")
            return None
    
    async def compress_video(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Compress video with specified quality"""
        try:
            if not params:
                params = {"crf": "23"}
            
            crf = params.get("crf", "23")
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", crf,
                "-preset", "fast",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                "-y", output_path
            ]
            
            logger.info(f"Compressing video with CRF {crf}: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Compression successful: {output_path}")
                return output_path
            else:
                logger.error("Compression failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error compressing video: {e}")
            return None
    
    async def rotate_video(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Rotate video with specified angle"""
        try:
            angle = params.get("angle", "90") if params else "90"
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Set video filter based on angle
            if angle == "90":
                vf = 'transpose=1'  # 90 degrees clockwise
            elif angle == "180":
                vf = 'transpose=2,transpose=2'  # 180 degrees
            elif angle == "270":
                vf = 'transpose=2'  # 90 degrees counter-clockwise
            elif angle == "flip_h":
                vf = 'hflip'  # horizontal flip
            elif angle == "flip_v":
                vf = 'vflip'  # vertical flip
            else:
                vf = 'transpose=1'  # default 90 degrees
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', vf,
                '-c:a', 'copy',
                '-y', output_path
            ]
            
            logger.info(f"Rotating video {angle}°: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Rotation successful: {output_path}")
                return output_path
            else:
                logger.error("Rotation failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error rotating video: {e}")
            return None
    
    async def mute_video(self, input_path: str, output_path: str, progress_tracker=None) -> Optional[str]:
        """Remove audio from video"""
        try:
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-an',
                '-c:v', 'copy',
                '-y', output_path
            ]
            
            logger.info(f"Muting video: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Muting successful: {output_path}")
                return output_path
            else:
                logger.error("Muting failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error muting video: {e}")
            return None
    
    async def reverse_video(self, input_path: str, output_path: str, progress_tracker=None) -> Optional[str]:
        """Reverse video playback"""
        try:
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', 'reverse',
                '-af', 'areverse',
                '-y', output_path
            ]
            
            logger.info(f"Reversing video: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Video reversal successful: {output_path}")
                return output_path
            else:
                logger.error("Video reversal failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error reversing video: {e}")
            return None
    
    async def extract_audio(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Extract audio from video with specified format and quality"""
        try:
            if not params:
                params = {"format": "mp3", "quality": "medium"}
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            format_type = params.get("format", "mp3")
            quality = params.get("quality", "medium")
            
            # Update output path with correct extension
            base_path = os.path.splitext(output_path)[0]
            if format_type == "wav":
                output_path = f"{base_path}.wav"
                codec_args = ["-acodec", "pcm_s16le"]
            else:  # mp3
                output_path = f"{base_path}.mp3"
                if quality == "high":
                    codec_args = ["-acodec", "libmp3lame", "-b:a", "320k"]
                elif quality == "low":
                    codec_args = ["-acodec", "libmp3lame", "-b:a", "128k"]
                else:  # medium
                    codec_args = ["-acodec", "libmp3lame", "-b:a", "192k"]
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vn'
            ] + codec_args + ['-y', output_path]
            
            logger.info(f"Extracting audio as {format_type} ({quality}): {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Audio extraction successful: {output_path}")
                return output_path
            else:
                logger.error("Audio extraction failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None
    
    async def take_screenshot(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Take screenshot(s) with specified count and quality"""
        try:
            count = params.get("count", 1) if params else 1
            quality = params.get("quality", "normal") if params else "normal"
            custom_time = params.get("custom_time") if params else None
            
            # Get video duration first
            duration = await self.get_video_duration(input_path)
            if not duration:
                duration = 10  # Default to 10 seconds
            
            if count == 1:
                # Single screenshot - use custom time if provided, otherwise 50% duration
                if custom_time is not None:
                    screenshot_time = custom_time
                else:
                    screenshot_time = duration / 2
                
                if quality == "hd":
                    cmd = [
                        self.ffmpeg_path,
                        '-i', input_path,
                        '-ss', str(screenshot_time),
                        '-vframes', '1',
                        '-vf', 'scale=1920:1080',
                        '-y', output_path
                    ]
                else:
                    cmd = [
                        self.ffmpeg_path,
                        '-i', input_path,
                        '-ss', str(screenshot_time),
                        '-vframes', '1',
                        '-y', output_path
                    ]
                
                await self._run_ffmpeg_command(cmd, progress_tracker)
                return output_path if os.path.exists(output_path) else None
            else:
                # Multiple screenshots - take them sequentially to avoid concurrency issues
                base_name = output_path.replace('.jpg', '')
                screenshots = []
                
                for i in range(count):
                    screenshot_time = (duration / (count + 1)) * (i + 1)
                    temp_output = f"{base_name}_{i+1}.jpg"
                    
                    cmd = [
                        self.ffmpeg_path,
                        '-i', input_path,
                        '-ss', str(screenshot_time),
                        '-vframes', '1',
                        '-y', temp_output
                    ]
                    
                    # Run sequentially to avoid async conflicts
                    success = await self._run_ffmpeg_command(cmd, None)  # No progress for individual screenshots
                    if success and os.path.exists(temp_output):
                        screenshots.append(temp_output)
                
                # Return all screenshots for multiple screenshot handling
                return screenshots
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    async def add_watermark(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Add watermark with specified type"""
        try:
            from helpers.watermark import WatermarkProcessor
            watermark_processor = WatermarkProcessor()
            
            if not params:
                # Default text watermark
                return await watermark_processor.add_text_watermark(
                    input_path, 
                    output_path, 
                    "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ",
                    progress_tracker
                )
            
            watermark_type = params.get("type", "text")
            
            if watermark_type == "timestamp":
                return await watermark_processor.add_timestamp_watermark(
                    input_path, 
                    output_path, 
                    progress_tracker
                )
            elif watermark_type == "image":
                image_path = params.get("image_path")
                if image_path and os.path.exists(image_path):
                    return await watermark_processor.add_image_watermark(
                        input_path, 
                        output_path, 
                        image_path,
                        progress_tracker
                    )
                else:
                    logger.error(f"Image watermark path not found: {image_path}")
                    return None
            elif watermark_type == "text" or watermark_type == "custom_text":
                text = params.get("text", "ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ")
                return await watermark_processor.add_text_watermark(
                    input_path, 
                    output_path, 
                    text,
                    progress_tracker
                )
            else:
                logger.error(f"Unknown watermark type: {watermark_type}")
                return None
            
        except Exception as e:
            logger.error(f"Error adding watermark: {e}")
            return None
    
    async def change_resolution(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Change video resolution to specified dimensions"""
        try:
            if not params:
                params = {"width": 1280, "height": 720}
            
            # Ensure input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file does not exist: {input_path}")
                return None
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            width = params.get("width", 1280)
            height = params.get("height", 720)
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vf', f'scale={width}:{height}',
                '-c:a', 'copy',
                '-y', output_path
            ]
            
            logger.info(f"Changing resolution to {width}x{height}: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Resolution change successful: {output_path}")
                return output_path
            else:
                logger.error("Resolution change failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error changing resolution: {e}")
            return None
    
    async def replace_audio(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Replace audio with new audio file or silence"""
        try:
            audio_file = params.get("audio_file") if params else None
            
            if audio_file and os.path.exists(audio_file):
                # Replace with new audio file
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-i', audio_file,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-map', '0:v:0',
                    '-map', '1:a:0',
                    '-shortest',
                    '-y', output_path
                ]
            else:
                # Replace with silence (mute)
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-f', 'lavfi',
                    '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-shortest',
                    '-y', output_path
                ]
            
            logger.info(f"Replacing audio: {input_path} -> {output_path}")
            success = await self._run_ffmpeg_command(cmd, progress_tracker)
            
            if success and os.path.exists(output_path):
                logger.info(f"Audio replacement successful: {output_path}")
                return output_path
            else:
                logger.error("Audio replacement failed or output file not created")
                return None
            
        except Exception as e:
            logger.error(f"Error replacing audio: {e}")
            return None
    
    async def merge_videos(self, input_path: str, output_path: str, progress_tracker=None) -> Optional[str]:
        """Merge video with itself (as demo)"""
        try:
            # Create a temporary file list
            list_file = f"{Config.TEMP_DIR}/merge_list.txt"
            with open(list_file, 'w') as f:
                f.write(f"file '{input_path}'\n")
                f.write(f"file '{input_path}'\n")
            
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y', output_path
            ]
            
            await self._run_ffmpeg_command(cmd, progress_tracker)
            
            # Clean up
            try:
                os.remove(list_file)
            except:
                pass
            
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            logger.error(f"Error merging videos: {e}")
            return None
    
    async def merge_multiple_videos(self, video_paths: list, process_id: str) -> Optional[str]:
        """Merge multiple videos into one"""
        try:
            if len(video_paths) < 2:
                logger.error("Need at least 2 videos to merge")
                return None
            
            output_path = f"{Config.UPLOADS_DIR}/{process_id}_merged.mp4"
            
            # Create a temporary file list
            list_file = f"{Config.TEMP_DIR}/{process_id}_merge_list.txt"
            with open(list_file, 'w') as f:
                for video_path in video_paths:
                    # Escape single quotes in file paths
                    escaped_path = video_path.replace("'", "'\"'\"'")
                    f.write(f"file '{escaped_path}'\n")
            
            cmd = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                '-y', output_path
            ]
            
            success = await self._run_ffmpeg_command(cmd, None)
            
            # Clean up list file
            try:
                os.remove(list_file)
            except:
                pass
            
            if success and os.path.exists(output_path):
                return output_path
            else:
                logger.error("Merge operation failed")
                return None
            
        except Exception as e:
            logger.error(f"Error merging multiple videos: {e}")
            return None
    
    async def add_subtitles(self, input_path: str, output_path: str, progress_tracker=None, params=None) -> Optional[str]:
        """Add hardcoded subtitle with specified type"""
        try:
            subtitle_type = params.get("type", "sample") if params else "sample"
            srt_file = params.get("srt_file") if params else None
            
            if subtitle_type == "custom" and srt_file and os.path.exists(srt_file):
                # Use SRT file for subtitles
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-vf', f"subtitles={srt_file}",
                    '-c:a', 'copy',
                    '-y', output_path
                ]
            else:
                # Use hardcoded text subtitle
                if subtitle_type == "sample":
                    subtitle_text = "ᴘʀᴏᴄᴇssᴇᴅ ʙʏ ꜰᴛᴍ ᴅᴇᴠᴇʟᴏᴘᴇʀᴢ"
                else:
                    subtitle_text = "ꜱᴀᴍᴘʟᴇ sᴜʙᴛɪᴛʟᴇ"
                
                cmd = [
                    self.ffmpeg_path,
                    '-i', input_path,
                    '-vf', f"drawtext=text='{subtitle_text}':fontsize=24:fontcolor=white:x=10:y=10:box=1:boxcolor=black@0.5",
                    '-c:a', 'copy',
                    '-y', output_path
                ]
            
            await self._run_ffmpeg_command(cmd, progress_tracker)
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            logger.error(f"Error adding subtitles: {e}")
            return None
    
    async def get_video_duration(self, input_path: str) -> Optional[float]:
        """Get video duration in seconds"""
        try:
            cmd = [
                self.ffprobe_path,
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return float(stdout.decode().strip())
            else:
                logger.error(f"Error getting video duration: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error in get_video_duration: {e}")
            return None
    
    async def _run_ffmpeg_command(self, cmd: list, progress_tracker=None) -> bool:
        """Run FFmpeg command with progress tracking"""
        try:
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion without concurrent reading
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("FFmpeg command completed successfully")
                return True
            else:
                logger.error(f"FFmpeg command failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error running FFmpeg command: {e}")
            return False
    

    
    def check_ffmpeg_installed(self) -> bool:
        """Check if FFmpeg is installed and accessible"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"FFmpeg not found: {e}")
            return False
