-- Enabled required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Created a replication role if needed
DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'zeus') THEN
      CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'prometheus0/a';
   END IF;
END
$$;

-- Grant permissions to medusa_db_owner
GRANT ALL PRIVILEGES ON DATABASE medusa_db TO medusa_db_owner;
