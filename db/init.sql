-- Create the database if it doesn't exist
CREATE DATABASE medusa_db WITH OWNER medusa_db_owner;

-- Connect to the database
\c medusa_db

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE medusa_db TO medusa_db_owner;

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS app;
GRANT ALL PRIVILEGES ON SCHEMA app TO medusa_db_owner;
