# WhereIsCowie Bot - Discord Ship Tracking Bot

## Overview

WhereIsCowie Bot is a Discord bot that provides real-time tracking of the Spirit of Adventure cruise ship using AIS (Automatic Identification System) data. The bot offers periodic updates, multiple command interfaces, and integrates with various maritime tracking APIs to provide comprehensive ship location and status information.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The bot follows a modular architecture with clear separation of concerns:

### Core Components
- **Discord Bot Framework**: Built using discord.py with command extensions
- **Ship Tracking Engine**: Dedicated module for fetching and processing ship data
- **Configuration Management**: Centralized configuration with environment variable support
- **Asynchronous Design**: Built for concurrent operations with async/await patterns

### Architecture Pattern
The application uses a **service-oriented architecture** where the bot acts as the presentation layer, the ship tracker as the business logic layer, and external APIs as the data layer.

## Key Components

### 1. Discord Bot (`main.py`)
- **Purpose**: Main bot interface and command handling
- **Features**: 
  - Command processing with aliases
  - Periodic update scheduling
  - Error handling and logging
  - Rich embed formatting for responses

### 2. Ship Tracker (`ship_tracker.py`)
- **Purpose**: Ship data fetching and processing
- **Features**:
  - Multiple API integration with fallback support
  - Session management for HTTP requests
  - Data parsing and formatting
  - Error handling with graceful degradation

### 3. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration and validation
- **Features**:
  - Environment variable loading
  - API key management
  - Feature flags for optional functionality
  - Configuration validation

## Data Flow

1. **User Command**: User issues a ship tracking command in Discord
2. **Command Processing**: Bot validates command and permissions
3. **Data Fetching**: Ship tracker queries external APIs for current ship data
4. **Data Processing**: Raw API data is parsed and formatted
5. **Response Generation**: Formatted data is embedded into Discord message
6. **User Response**: Rich embed with ship information sent to Discord channel

### Periodic Updates
- **Trigger**: Scheduled task runs at 06:00, 12:00, and 16:00 UTC daily
- **Process**: Automatic data fetch via web scraping and update to configured channels
- **Data Source**: VesselFinder website scraping (no API keys required)

## Recent Changes (July 24, 2025)
- Added CruiseMapper as primary data source with exact GPS coordinates
- CruiseMapper provides precise latitude/longitude from JavaScript config
- Automatic location detection (English Channel, Baltic Sea, Gibraltar, etc.)
- Port code translation (GIB→Gibraltar, DVR→Dover, etc.)
- Fallback to VesselFinder for backup data if CruiseMapper fails
- Removed duplicate workflows causing "Data Unavailable" errors
- Removed course display from ship tracking output (user preference)
- Added live map screenshot functionality using Selenium + Chrome
- Bot now includes map images showing ship's exact location
- Screenshots are automatically generated and cleaned up after display

## External Dependencies

### APIs and Services
- **VesselFinder API**: Primary ship tracking data source
- **MarineTraffic API**: Secondary/fallback data source
- **Discord API**: Bot communication and messaging

### Python Libraries
- **discord.py**: Discord bot framework and API wrapper
- **aiohttp**: Asynchronous HTTP client for API requests
- **python-dotenv**: Environment variable management

### Ship Identification
- **IMO Number**: 9818084 (International Maritime Organization identifier)
- **MMSI**: 232026551 (Maritime Mobile Service Identity)
- **Ship Name**: "SPIRIT OF ADVENTURE"

## Deployment Strategy

### Environment Setup
- **Environment Variables**: Bot token and API keys stored securely
- **Configuration Validation**: Startup checks ensure required credentials
- **Logging**: File and console logging for monitoring and debugging

### Runtime Features
- **Auto-Recovery**: Session management with automatic reconnection
- **Rate Limiting**: Built-in throttling to respect API limits
- **Error Handling**: Graceful degradation when services are unavailable
- **Feature Flags**: Optional functionality can be enabled/disabled

### Bot Permissions
- **Required Permissions**: Send Messages, Embed Links, Read Message History
- **Permission Integer**: 277025770496
- **Channel Management**: Requires "Manage Channels" for tracking setup

### Command Structure
- **Prefix Support**: Multiple command prefixes ('!' and '/')
- **Alias System**: Multiple aliases for user convenience
- **Permission Checking**: Role-based access for administrative commands

## Key Architectural Decisions

### Multiple API Sources
- **Problem**: Single API dependency creates failure points
- **Solution**: Implemented fallback system with multiple ship tracking APIs
- **Benefits**: Improved reliability and data availability

### Asynchronous Architecture
- **Problem**: Blocking operations would freeze bot responsiveness
- **Solution**: Full async/await implementation with aiohttp
- **Benefits**: Concurrent request handling and better performance

### Modular Design
- **Problem**: Monolithic code would be difficult to maintain
- **Solution**: Separated concerns into distinct modules
- **Benefits**: Easier testing, maintenance, and feature additions

### Environment-Based Configuration
- **Problem**: Hardcoded credentials and settings create security risks
- **Solution**: Configuration class with environment variable support
- **Benefits**: Secure credential management and deployment flexibility