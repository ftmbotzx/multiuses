# Video Processor Telegram Bot

## Overview

This is a comprehensive Telegram bot for video processing operations built with Python using the Pyrogram framework. The bot provides various video manipulation features including trimming, compression, rotation, watermarking, merging, and more. The system is designed to handle concurrent operations for multiple users with a credit-based system and premium subscription model.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### July 12, 2025 - Critical Bug Fixes and Admin Update
- ✓ Fixed custom text watermark functionality - now properly uses user input instead of hardcoded "ftmdeveloperz"
- ✓ Resolved admin panel callback conflicts by adding missing callback handlers 
- ✓ Fixed admin commands like `/searchuser` by excluding them from text processing filters
- ✓ Added new admin user ID: 7298944577
- ✓ Added admin test command `/admintest` for verification
- ✓ Cleared admin cache system to ensure immediate recognition of new admins
- ✓ Fixed missing command handlers for `/redeem`, `/myplan`, `/refer`, `/refstats`, and `/credits`
- ✓ All premium and referral commands now work both as direct commands and inline buttons
- ✓ All 131 plugins loaded successfully after fixes

## System Architecture

The bot follows a modular plugin-based architecture with clear separation of concerns:

### Core Components
- **Bot Engine**: Pyrogram-based Telegram client with async support and high concurrency (1000 workers)
- **Database Layer**: MongoDB with Motor async driver for data persistence
- **Task Management**: AsyncIOScheduler for background operations and cleanup tasks
- **File Processing**: FFmpeg integration for video/audio manipulation
- **Progress Tracking**: Real-time progress updates for long-running operations
- **Web Server**: Built-in health check server using aiohttp

### Architecture Patterns
- **Plugin System**: Modular command handlers in separate files under `/plugins` directory
- **Database Abstraction**: Centralized database operations through Database class
- **Async Processing**: Non-blocking operations with proper progress tracking
- **Resource Management**: Automatic cleanup of temporary files
- **Admin Panel**: Comprehensive admin interface for bot management

## Key Components

### 1. Core Bot (`bot.py`)
- Main bot initialization with Pyrogram client configuration
- Integrated AsyncIOScheduler for background tasks
- Database connection management at startup
- Health check web server integration

### 2. Database Layer (`database/db.py`)
- MongoDB integration using Motor async driver
- Collections: users, operations, premium_codes, referrals
- User management with credit system tracking
- Premium subscription management
- Operation logging and statistics

### 3. Video Processing System
- **FFmpeg Processor** (`helpers/ffmpeg.py`): Core video processing operations
- **Downloader** (`helpers/downloader.py`): Aria2c integration for fast downloads
- **Watermark Processor** (`helpers/watermark.py`): Text and image watermark capabilities
- **Task Manager** (`helpers/task_manager.py`): Async task coordination

### 4. Plugin System
- **Video Upload Handler** (`plugins/video_upload.py`): Main video input processing
- **Option Selection** (`plugins/option_selection.py`): Processing option menus
- **Process Confirmation** (`plugins/process_confirmation.py`): User confirmation flows
- **Video Processing** (`plugins/video_processing.py`): Core processing orchestration
- **Navigation** (`plugins/navigation.py`): UI navigation between menus

### 5. Admin Management
- **Admin Panel** (`plugins/admin/admin_panel.py`): Main administrative interface
- **User Management**: Ban/unban, premium assignment, credit management
- **Statistics**: Comprehensive usage analytics and reporting
- **Broadcast System**: Mass messaging capabilities
- **Configuration Management**: Dynamic bot settings adjustment

## Data Flow

### User Registration and Authentication
1. User sends `/start` command
2. System checks if user exists in database
3. New users are created with default credits
4. Referral system processes bonus credits if applicable
5. Premium status and admin privileges are verified

### Video Processing Workflow
1. User uploads video file
2. System displays processing options menu
3. User selects operation (trim, compress, watermark, etc.)
4. Credit check and daily limit validation
5. Processing confirmation with cost display
6. Async processing with real-time progress updates
7. Processed file upload with cleanup

### Admin Operations
1. Admin commands trigger privilege verification
2. Cached admin status reduces database load
3. Operations logged for audit trail
4. Broadcast messages sent with rate limiting

## External Dependencies

### Required Services
- **MongoDB**: Primary database for user data and operations
- **FFmpeg**: Video/audio processing engine
- **Aria2c**: High-speed file downloader

### Python Packages
- **Pyrogram + TgCrypto**: Telegram client library
- **Motor**: Async MongoDB driver
- **APScheduler**: Background task scheduling
- **aiohttp**: Web server for health checks
- **Pillow**: Image processing for thumbnails
- **psutil**: System monitoring

### Optional Integrations
- **Telegram Channels**: Logging and media storage
- **Premium Code System**: Revenue management
- **Referral System**: User acquisition

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive data (API keys, database URIs)
- Configurable processing limits and credit costs
- Admin user management through environment variables
- File path configuration for different deployment environments

### Scalability Considerations
- Async operations prevent blocking
- Database connection pooling
- Temporary file cleanup automation
- Progress tracking prevents resource leaks
- Admin caching reduces database load

### Monitoring and Health Checks
- Built-in web server for container health checks
- Operation logging for debugging
- User statistics for performance monitoring
- Error tracking and admin notifications

### Security Features
- Admin privilege verification with caching
- User ban system with database persistence
- Credit-based rate limiting
- Input validation for all user data
- Secure file handling with automatic cleanup

The system is designed to be production-ready with proper error handling, resource management, and scalability considerations. The modular architecture allows for easy feature additions and maintenance.