-- MinIO Bucket Setup Documentation
-- Description: Instructions for setting up MinIO bucket for FedFina Enhanced Reporting
-- Date: July 31, 2025
-- Author: AI Assistant

/*
This file contains the setup instructions for MinIO bucket configuration.
Since MinIO uses its own CLI and API, the actual setup is done via MinIO commands.
*/

-- =============================================================================
-- MINIO BUCKET SETUP INSTRUCTIONS
-- =============================================================================

/*
1. ACCESS MINIO CONSOLE OR CLI
   - MinIO Console: http://localhost:9000 (or your MinIO endpoint)
   - Username: minioadmin (default)
   - Password: minioadmin (default)
   - Or use MinIO CLI: mc

2. CREATE BUCKET
   - Bucket Name: fedfina-reports
   - Region: us-east-1 (or your preferred region)
   - Versioning: Enabled (recommended)
   - Object Lock: Disabled (unless required for compliance)

3. SET BUCKET POLICY (Optional - for public read access to reports)
   - This allows direct access to reports via URLs
   - Only enable if reports should be publicly accessible

4. CREATE FOLDER STRUCTURE
   The bucket will automatically create folders when files are uploaded:
   - fedfina-reports/
     ├── {account_id}/
     │   ├── audio/
     │   │   └── {conversation_id}.wav
     │   ├── transcripts/
     │   │   └── {conversation_id}.json
     │   └── reports/
     │       └── {conversation_id}.pdf

5. MINIO CLI COMMANDS (if using CLI)
   mc config host add myminio http://localhost:9000 minioadmin minioadmin
   mc mb myminio/fedfina-reports
   mc policy set download myminio/fedfina-reports
*/

-- =============================================================================
-- ENVIRONMENT VARIABLES TO ADD
-- =============================================================================

/*
Add these variables to your .env files:

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fedfina-reports
MINIO_USE_SSL=false
MINIO_REGION=us-east-1

# For production, use proper credentials:
# MINIO_ACCESS_KEY=your-access-key
# MINIO_SECRET_KEY=your-secret-key
# MINIO_USE_SSL=true
*/

-- =============================================================================
-- BUCKET POLICY EXAMPLE (JSON)
-- =============================================================================

/*
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": ["*"]
            },
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::fedfina-reports/*"
            ]
        }
    ]
}
*/

-- =============================================================================
-- TESTING THE SETUP
-- =============================================================================

/*
1. Test bucket access:
   mc ls myminio/fedfina-reports

2. Test file upload:
   echo "test content" > test.txt
   mc cp test.txt myminio/fedfina-reports/test/

3. Test file download:
   mc cp myminio/fedfina-reports/test/test.txt downloaded_test.txt

4. Test presigned URL generation:
   mc share download myminio/fedfina-reports/test/test.txt
*/

-- =============================================================================
-- SECURITY CONSIDERATIONS
-- =============================================================================

/*
1. Access Control:
   - Use IAM policies for fine-grained access control
   - Implement bucket policies for public/private access
   - Use presigned URLs for temporary access

2. Encryption:
   - Enable server-side encryption for sensitive data
   - Use client-side encryption for highly sensitive files

3. Monitoring:
   - Enable access logging
   - Monitor bucket usage and costs
   - Set up alerts for unusual access patterns

4. Backup:
   - Implement cross-region replication
   - Regular backup verification
   - Disaster recovery procedures
*/

-- =============================================================================
-- INTEGRATION WITH APPLICATION
-- =============================================================================

/*
The MinIOService will handle:
1. Bucket creation (if not exists)
2. Folder structure creation
3. File upload with proper naming
4. Presigned URL generation
5. File deletion (if needed)
6. Error handling and retries

Key methods to implement:
- create_bucket_if_not_exists()
- upload_file()
- generate_presigned_url()
- delete_file()
- list_files()
*/ 