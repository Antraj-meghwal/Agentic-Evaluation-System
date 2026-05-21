-- Runs once on fresh Docker volume. User gradeops is POSTGRES_USER (superuser).
GRANT ALL ON SCHEMA public TO gradeops;
ALTER SCHEMA public OWNER TO gradeops;
