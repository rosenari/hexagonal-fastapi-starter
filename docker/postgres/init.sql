-- Initialize PostgreSQL database for Hexagonal FastAPI Starter

-- Create database if not exists (handled by POSTGRES_DB env var)
-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be applied after tables are created)
-- These will be handled by SQLAlchemy migrations in the application