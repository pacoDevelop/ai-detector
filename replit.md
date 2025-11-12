# Overview

This is an AI Detector Generator application built with Streamlit that creates "canary tokens" to detect when AI models access GitHub repositories. The system generates hidden trap files containing prompts that instruct AI models to self-identify by sending an email notification when they process the repository. Users can create custom detection templates, manage multiple repositories, track generation history, monitor alerts, and optionally upload files directly to GitHub via API.

**Latest Update (2025-11-12)**: Implemented all advanced features including GitHub API integration, custom templates with multi-language support, batch repository management, alert dashboard, and persistent history tracking. Database uses SQLite for reliability.

# User Preferences

Preferred communication style: Simple, everyday language (Spanish primary).

# System Architecture

## Frontend Architecture

**Technology**: Streamlit web application
- **Multi-tab interface** with 5 distinct sections:
  - Generator: Creates new AI detector tokens
  - History: Views previously generated tokens
  - Custom Templates: Manages detection prompt templates
  - Multiple Repositories: Bulk repository management
  - Alert Dashboard: Monitors AI detection events
- **Rationale**: Streamlit provides rapid prototyping for data-driven applications with minimal frontend code, suitable for internal tools and MVPs

## Backend Architecture

**ORM Pattern**: SQLAlchemy with declarative base
- **Database Models**:
  - `GeneratedToken`: Tracks created canary tokens with metadata (email, repo, timestamp, files)
  - `Repository`: Manages monitored repositories with sync status
  - `CustomTemplate`: Stores user-defined detection prompt templates
- **Session Management**: SessionLocal factory pattern for database operations
- **Rationale**: SQLAlchemy provides database-agnostic ORM, enabling easy migration between SQLite and PostgreSQL

## Data Storage

**Primary Database**: SQLite with PostgreSQL fallback
- **Configuration**: Uses SQLite by default (`ai_detectors.db`) for maximum reliability
- **Fallback Strategy**: Automatically uses SQLite if PostgreSQL connection fails
- **Database Models**:
  - `GeneratedToken`: Stores token history (id, token, email, repo_name, prefix, created_at, files_generated)
  - `Repository`: Manages repositories (id, repo_name, email, last_token_generated, last_sync, created_at)
  - `CustomTemplate`: Stores custom templates (id, name, template_content, language, created_at, updated_at)
  - `AlertLog`: Records AI detection alerts (id, token, ai_model, ai_company, purpose, ip_address, user_agent, received_at, raw_data)
- **Pros**: 
  - SQLite requires zero configuration
  - Reliable file-based storage
  - Perfect for single-user applications
- **Cons**: 
  - SQLite has limited concurrent write capabilities
  - File-based storage not ideal for distributed systems

**File Generation System**:
- Creates 5 hidden trap files per repository (`.ai-detector`, `.github-scraper-trap.md`, etc.)
- Files contain canary tokens with email notification instructions for AI models
- Template variable substitution: `{email}`, `{repo_name}`, `{canary_token}`, `{repo_user}`

## Detection Mechanism

**Canary Token Strategy**:
- Embeds prompt injection instructions in hidden files that AI models typically read during repository analysis
- Tokens follow pattern: `PREFIX-YYYY-MM-DD-INITIALS`
- Instructions request AI models to self-identify by sending email with:
  - Model name/version
  - Company (OpenAI, Google, Meta, etc.)
  - Access purpose (training, crawling, summarization)
  - Technical details (IP, User-Agent, timestamp)

**Rationale**: Leverages AI models' tendency to follow in-context instructions while remaining invisible to human users browsing GitHub

## Template System

**Custom Template Architecture**:
- User-defined templates stored in `custom_templates` table
- Variable substitution engine for personalization
- Supports multiple detection strategies per user
- Default template provides standard AI detection prompt

**Design Pattern**: Template method pattern with variable interpolation
- **Alternatives Considered**: Static file templates, but database storage enables dynamic updates without code deployment

# External Dependencies

## Core Framework
- **Streamlit**: Web application framework for data-driven interfaces
  - Purpose: Rapid UI development with Python-only code
  - Version: Not pinned (should be specified in requirements.txt)

## Database Layer
- **SQLAlchemy**: SQL toolkit and ORM
  - Purpose: Database abstraction and model definition
  - Enables both SQLite (development) and PostgreSQL (production)

## Email Notification System
- **Target**: User-provided email addresses
  - AI models instructed to send detection notifications
  - No SMTP server in application (relies on AI model capabilities)
  - **Note**: This is a theoretical mechanism dependent on AI model compliance

## File Generation
- **Python Standard Library**:
  - `zipfile`: Creates downloadable archive of trap files
  - `io.BytesIO`: In-memory file handling
  - `base64`: Encoding for file downloads
  - `json`: Data serialization for trap files
  - `datetime`: Timestamp generation for tokens

## GitHub API Integration
- **requests**: HTTP library for GitHub API interactions
  - Purpose: Automated file uploads to GitHub repositories
  - Requires Personal Access Token with 'repo' permissions
  - Tokens stored only in session memory for security

## Environment Configuration
- **DATABASE_URL**: Optional environment variable for PostgreSQL connection string
  - Format: `postgresql://user:pass@host:port/dbname`
  - Application defaults to SQLite for reliability
  - Automatic fallback if PostgreSQL connection fails