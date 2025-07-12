# Video Processor Telegram Bot

## Overview

This is a comprehensive Telegram bot for video processing operations built with Python using the Pyrogram framework. The bot provides various video manipulation features including trimming, compression, watermarking, audio extraction, screenshot generation, and more. It includes a credit system, premium subscriptions, referral program, and admin panel for management.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

• **Complete Video Handler Modularization (July 11, 2025)**: Successfully separated the massive 2034-line video_handler.py file into 15+ focused modules. Each callback function now has its own dedicated file with unique names. Created specialized handlers for video upload, option selection, process confirmation, custom callbacks, file uploads, navigation, watermark processing, text input, merge operations, and screenshot handling. Removed the original video_handler.py file completely, reducing plugin count from 69 to 55 with zero redundancy.

• **Duplicate Plugin Cleanup (July 12, 2025)**: Removed duplicate standalone files (credits.py, premium.py, referral.py) that existed alongside their organized subdirectory versions. Final clean architecture with 51 plugin files and no redundancy.

• **Complete Code Modularization (July 11, 2025)**: Achieved comprehensive separation of all callback functions into individual files within organized subdirectories. Completed separation of admin panel (17 functions), credits system (3 functions), premium management (4 functions), and referral system (2 functions) into dedicated files. This provides maximum maintainability and zero callback redundancy.

• **Database Connection Optimization (July 11, 2025)**: Removed redundant database connection checks from all command handlers. The database is now connected once at bot startup, eliminating the need for individual connection verification before each database operation. This improves performance and reduces code complexity.

## System Architecture

The bot follows a modular plugin-based architecture with clear separation of concerns:

### Core Components
- **Bot Engine**: Pyrogram-based Telegram client with async support
- **Database Layer**: MongoDB with Motor async driver for data persistence
- **Task Management**: AsyncIO-based task scheduler for background operations
- **File Processing**: FFmpeg integration for video/audio manipulation
- **Progress Tracking**: Real-time progress updates for long-running operations

### Architecture Patterns
- **Plugin System**: Modular command handlers in separate files
- **Database Abstraction**: Centralized database operations through Database class
- **Async Processing**: Non-blocking operations with proper progress tracking
- **Resource Management**: Automatic cleanup of temporary files

## Key Components

### 1. Core Bot (`bot.py`)
- Main bot initialization and startup logic
- Pyrogram client configuration with optimized settings
- Integrated web server for health checks
- Scheduler setup for background tasks

### 2. Database Layer (`database/db.py`)
- MongoDB integration using Motor async driver
- User management with credit system tracking
- Premium subscription handling
- Referral system implementation
- Operation logging and analytics

### 3. Video Processing (`helpers/`)
- **FFmpeg Processor**: Comprehensive video manipulation operations
- **Watermark Processor**: Text and image watermark capabilities  
- **Downloader**: Aria2-based fast file downloading
- **Task Manager**: Async task coordination and status tracking
- **Progress Tracker**: Real-time progress updates with formatted display

### 4. Plugin System (`plugins/`)
- **Video Handler**: Main video processing coordination
- **Admin Panel**: Comprehensive bot administration features
- **User Commands**: Start, credits, referral, thumbnail management
- **Sample Generator**: Automated sample video creation
- **Web Server**: Health check and monitoring endpoints

## Data Flow

### Video Processing Workflow
1. **Upload**: User sends video file to bot
2. **Validation**: Check file size, format, and user permissions
3. **Credit Check**: Verify user has sufficient credits
4. **Operation Selection**: User chooses processing operation via inline keyboard
5. **Processing**: Async task execution with progress tracking
6. **Upload**: Processed file sent back to user
7. **Cleanup**: Temporary files automatically removed

### User Management Flow
1. **Registration**: New user creation with referral bonus handling
2. **Credit System**: Track usage and deduct costs per operation
3. **Premium Features**: Enhanced limits and unlimited operations
4. **Daily Limits**: Reset usage counters for free users

## External Dependencies

### Core Technologies
- **Pyrogram**: Telegram MTProto API wrapper
- **MongoDB**: Document database via Motor async driver
- **FFmpeg**: Video/audio processing engine
- **Aria2**: High-speed file downloading
- **APScheduler**: Background task scheduling

### Processing Libraries
- **MoviePy**: Python video editing capabilities
- **Pillow**: Image processing for thumbnails
- **PyTZ**: Timezone handling for scheduling

### Web Components
- **aiohttp**: Async HTTP server for health checks
- **Flask**: Alternative web framework support

## Deployment Strategy

### Environment Configuration
- **Containerized Deployment**: Designed for Docker/container environments
- **Environment Variables**: All sensitive data via env vars
- **Port Configuration**: Configurable web server port (default 8080)
- **Resource Management**: Optimized for cloud deployment

### Scaling Considerations
- **Async Architecture**: High concurrency support with proper resource limits
- **Database Indexing**: Optimized queries for user and operation data
- **File Cleanup**: Automatic temporary file management
- **Memory Management**: Efficient handling of large video files

### Monitoring & Health Checks
- **Web Endpoints**: Health check routes for load balancers
- **Logging**: Comprehensive logging throughout the application
- **Error Handling**: Graceful degradation and user-friendly error messages
- **Admin Tools**: Built-in administration panel for monitoring

### Security Features
- **User Authentication**: Telegram-based user verification
- **Admin Controls**: Role-based access control
- **Rate Limiting**: Credit system prevents abuse
- **File Validation**: Security checks on uploaded content

The bot is designed to be highly scalable, maintainable, and user-friendly while providing professional-grade video processing capabilities through a simple Telegram interface.