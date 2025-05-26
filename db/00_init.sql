-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a replication role if needed
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'zeus') THEN
      CREATE ROLE zeus WITH REPLICATION LOGIN PASSWORD 'prometheus0/a';
   END IF;
END
$$;

-- Grant permissions to medusa_db_owner
ALTER USER medusa_db_owner WITH SUPERUSER;