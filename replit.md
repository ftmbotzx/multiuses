# Video Processing Bot

## Overview

This is a Telegram bot built with Pyrogram that provides video processing capabilities. Users can upload videos and perform various operations like trimming, compressing, rotating, adding watermarks, and more. The bot includes a credit system, premium subscriptions, referral program, and admin functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Pyrogram (Python Telegram Bot API)
- **Language**: Python 3.x
- **Architecture Pattern**: Plugin-based modular design
- **Database**: MongoDB with Motor (async driver)
- **File Processing**: FFmpeg for video operations
- **Async Processing**: Uses asyncio for non-blocking operations

### Key Design Decisions
- **Plugin System**: Modular approach with separate files for different functionalities (admin, credits, premium, etc.)
- **Async/Await**: Full async implementation for better performance and concurrent processing
- **Credit System**: Virtual currency system to limit usage and monetize the service
- **Progress Tracking**: Real-time progress updates during video processing operations

## Key Components

### Core Components
1. **bot.py**: Main bot entry point and initialization
2. **config.py**: Configuration management with environment variables
3. **database.py**: MongoDB integration with user management
4. **progress.py**: Progress tracking and user feedback during operations

### Plugin System
- **start.py**: User onboarding and welcome flow
- **video_handler.py**: Main video processing workflow
- **admin.py**: Administrative commands and broadcast functionality
- **credits.py**: Credit system management
- **premium.py**: Premium subscription handling
- **referral.py**: Referral program implementation

### Helper Modules
- **helpers/ffmpeg.py**: Video processing operations using FFmpeg
- **helpers/utils.py**: Utility functions for file operations
- **helpers/watermark.py**: Watermark processing functionality

## Data Flow

### User Registration Flow
1. User sends /start command
2. Bot checks if user exists in database
3. If new user, creates record with default credits
4. Handles referral bonuses if applicable
5. Displays welcome message with available options

### Video Processing Flow
1. User uploads video file
2. Bot validates user permissions and limits
3. Displays processing options (trim, compress, rotate, etc.)
4. User selects operation
5. Bot downloads video, processes with FFmpeg
6. Updates progress in real-time
7. Uploads processed video back to user
8. Deducts credits and updates usage statistics

### Credit System Flow
- Users start with default credits
- Each operation costs configurable credits
- Credits can be earned through referrals
- Premium users get unlimited daily processing
- Admin can manage user credits

## External Dependencies

### Required Services
- **MongoDB**: User data, operations history, premium subscriptions
- **FFmpeg**: Video processing operations
- **Telegram Bot API**: Core bot functionality

### Environment Variables
- `API_ID`, `API_HASH`: Telegram API credentials
- `BOT_TOKEN`: Telegram bot token
- `MONGODB_URI`: MongoDB connection string
- `OWNER_ID`, `ADMINS`: Bot administration
- Various configuration for credits, limits, and pricing

### File System Requirements
- Directories for downloads, uploads, and temporary files
- FFmpeg and FFprobe binaries in system PATH

## Deployment Strategy

### Prerequisites
- Python 3.8+ environment
- MongoDB instance (local or cloud)
- FFmpeg installation
- Telegram bot token from BotFather

### Environment Setup
1. Install Python dependencies (pyrogram, motor, python-dotenv)
2. Set up MongoDB database
3. Configure environment variables in .env file
4. Ensure FFmpeg is available in system PATH
5. Create necessary directories for file storage

### Running the Bot
- Execute `python bot.py` to start the bot
- Bot will connect to MongoDB and Telegram
- Sends startup notification to configured log channel
- Handles graceful shutdown with cleanup

### Scaling Considerations
- MongoDB can be horizontally scaled
- File storage should be moved to cloud storage for production
- Progress tracking uses in-memory storage (consider Redis for scaling)
- Multiple bot instances would need coordination for shared state

## Features

### User Features
- Video processing operations (trim, compress, rotate, etc.)
- Credit system with daily limits
- Referral program for earning credits
- Premium subscriptions for unlimited access
- Real-time progress tracking

### Admin Features
- **Comprehensive Admin Panel** (/admin command)
  - Interactive GUI with organized sections
  - User management (search, ban/unban, add credits)
  - Premium management (add premium, create codes, view stats)
  - System statistics and analytics
  - Activity logs and operation monitoring
  - Broadcast management (all users, active only, premium only)
  - Database backup and export functionality
  - System settings and file management
  - Security and maintenance tools
- User management and statistics
- Broadcasting messages to all users
- Premium code generation
- Credit management
- User banning/unbanning

### Technical Features
- Async processing for better performance
- Progress tracking with visual indicators
- Error handling and logging
- File cleanup after processing
- Modular plugin architecture for easy extensibility

## Current Status (Updated 2025-07-10)

### Deployment Status: ✅ OPERATIONAL WITH MAJOR IMPROVEMENTS
- **Bot Status**: Successfully deployed and running with enhanced features
- **Database**: MongoDB connected and operational
- **Plugins**: All 32 plugins loaded successfully (1 new plugin added)
- **Configuration**: All required environment variables configured
- **Video Processing**: FFmpeg integration with real-time progress tracking

### Environment Configuration Complete
- ✅ API_ID and API_HASH (Telegram API credentials)
- ✅ BOT_TOKEN (Telegram bot token)
- ✅ MONGODB_URI (Database connection)
- ✅ OWNER_ID (Admin user configuration)
- 🔧 LOG_CHANNEL_ID and MEDIA_CHANNEL_ID (Optional - can be configured later)

### Major Improvements Made (2025-07-10)
- ✅ **Enhanced Interactive Operations**: Added detailed option menus for all processing functions
- ✅ **Real-time Progress Tracking**: Implemented comprehensive progress bars for downloads and processing
- ✅ **Better User Experience**: Each operation now shows options (trim duration, compression quality, screenshot count, etc.)
- ✅ **Improved Error Handling**: Fixed database connection issues across all plugins
- ✅ **Media Type Handling**: Screenshots sent as photos, audio extracts sent as audio files
- ✅ **Progress Visualization**: Added visual progress bars with ETA and speed information

### New Interactive Features
- **Trim Video**: Choose duration (30s, 60s, 5min, 10min, or custom)
- **Compress Video**: Select quality levels (high, medium, small, tiny)
- **Rotate Video**: Multiple rotation options (90°, 180°, 270°, flip horizontal/vertical)
- **Merge Videos**: Request additional video for merging
- **Screenshot**: Multiple screenshots (1, 3, 5, 10) with quality options
- **Watermark**: Text watermark, timestamp, or custom text options
- **Resolution**: Choose from 480p, 720p, 1080p, 1440p, 4K
- **Extract Audio**: Multiple formats (MP3 high/medium/low, WAV)
- **Subtitles**: Sample or custom subtitle options

### Fixed Issues
- ✅ Database session lock conflicts resolved
- ✅ Plugin database connection initialization fixed
- ✅ MongoDB collection access errors resolved
- ✅ All command handlers working properly
- ✅ Referral system error "fetching referral info" resolved
- ✅ Progress tracking integration with FFmpeg processing
- ✅ **CRITICAL**: Premium users no longer blocked by credit requirements
- ✅ **CRITICAL**: Admin users bypass all credit and daily limits
- ✅ **CRITICAL**: Video processing privilege system working correctly

### Ready for Use
The bot is fully operational and ready to:
1. Accept user registrations via /start command
2. Process video uploads with 12 different operations (each with detailed options)
3. Handle credit system and referral program
4. Manage premium subscriptions
5. Execute admin commands for user management
6. Track progress in real-time during video processing with visual progress bars
7. Handle different media types appropriately (photos, videos, audio)

### Testing Status
- ✅ User registration working
- ✅ Database operations functional  
- ✅ Plugin system fully loaded (32 plugins)
- ✅ All database connection issues resolved
- ✅ Bot running without errors
- ✅ Progress tracking system operational
- ✅ Interactive operation menus working
- ✅ Ready for full video processing testing

### Last Update: 2025-07-11 14:35
- **CRITICAL FIXES COMPLETED**: Resolved all import errors that were preventing bot startup
- **IMPORT FIXES**: Updated all plugin files to use correct imports:
  - Changed `from db import Database` to `from database.db import Database`
  - Changed `from config import Config` to `from info import Config`
- **HELPER MODULE FIXES**: Fixed import statements in all helper modules (ffmpeg.py, downloader.py, watermark.py, utils.py)
- **PLUGIN SYSTEM**: All 81 plugins now loading successfully without errors
- **DATABASE**: MongoDB connection stable and operational with 5 registered users
- **WEB SERVER**: Running successfully on port 8080 with health check endpoints
- **STARTUP BROADCAST**: Automated notification system working properly
- **SCHEDULER**: Background task scheduler started and operational
- **BOT TOKEN UPDATED**: Successfully changed to new token (7575260816:AAF5tFxQMMZSP1BDIetM9apu0tdGP_ix-eQ)
- **NEW SESSION**: Created fresh authentication session after token change
- **BOT IDENTITY**: Now running as "Tera Dl (@ftmbotzx_teradlbot)"
- **Status**: Bot fully operational with new token - all systems green and ready for user interactions
- **FINAL CRITICAL FIXES COMPLETED**: All 3 remaining bugs have been resolved
- **CUSTOM TRIM FIX**: Custom time trim now prompts user for input and processes correctly
- **WATERMARK MODULE FIX**: Custom text and image watermarks now working properly with correct parameter handling
- **STARTUP BROADCAST FIX**: Bot now sends branded startup messages to all users after restart
- **REPLACE AUDIO SIMPLIFIED**: Removed useless "remove audio" option that only muted video
- **STREAMLINED WORKFLOW**: Replace audio now directly goes to upload new audio file
- **CLEANER CODE**: Removed redundant silence replacement functionality from FFmpeg processor
- **Previous Features**: All other watermark, trim, and video processing features remain intact and operational