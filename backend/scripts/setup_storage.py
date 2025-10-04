#!/usr/bin/env python3
"""
Supabase Storage Configuration Script for Planning Explorer
Sets up storage buckets for user files, reports, and other assets
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupabaseStorageSetup:
    """Configure Supabase storage buckets and policies"""

    def __init__(self):
        self.supabase_client = None
        self.buckets_config = {
            "user-reports": {
                "name": "user-reports",
                "public": False,
                "file_size_limit": 50 * 1024 * 1024,  # 50MB
                "allowed_mime_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/json", "text/csv"]
            },
            "user-uploads": {
                "name": "user-uploads",
                "public": False,
                "file_size_limit": 10 * 1024 * 1024,  # 10MB
                "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "application/pdf", "text/plain"]
            },
            "public-assets": {
                "name": "public-assets",
                "public": True,
                "file_size_limit": 5 * 1024 * 1024,  # 5MB
                "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "image/svg+xml"]
            },
            "system-exports": {
                "name": "system-exports",
                "public": False,
                "file_size_limit": 100 * 1024 * 1024,  # 100MB
                "allowed_mime_types": ["application/json", "text/csv", "application/zip"]
            }
        }

    def connect(self) -> bool:
        """Connect to Supabase"""
        try:
            self.supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            logger.info("✅ Connected to Supabase successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            return False

    def create_bucket(self, bucket_config: Dict[str, Any]) -> bool:
        """Create a storage bucket with configuration"""
        try:
            bucket_name = bucket_config["name"]

            # Create bucket
            result = self.supabase_client.storage.create_bucket(
                bucket_name,
                options={
                    "public": bucket_config["public"],
                    "file_size_limit": bucket_config["file_size_limit"],
                    "allowed_mime_types": bucket_config["allowed_mime_types"]
                }
            )

            if result:
                logger.info(f"✅ Created bucket '{bucket_name}' successfully")
                return True
            else:
                logger.warning(f"⚠️ Bucket '{bucket_name}' may already exist")
                return True

        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"✅ Bucket '{bucket_name}' already exists")
                return True
            else:
                logger.error(f"❌ Failed to create bucket '{bucket_name}': {e}")
                return False

    def create_storage_policies(self) -> bool:
        """Create RLS policies for storage buckets"""

        policies_sql = """
        -- Storage policies for user-reports bucket
        CREATE POLICY "Users can upload own reports" ON storage.objects
            FOR INSERT WITH CHECK (
                bucket_id = 'user-reports' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        CREATE POLICY "Users can view own reports" ON storage.objects
            FOR SELECT USING (
                bucket_id = 'user-reports' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        CREATE POLICY "Users can update own reports" ON storage.objects
            FOR UPDATE USING (
                bucket_id = 'user-reports' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        CREATE POLICY "Users can delete own reports" ON storage.objects
            FOR DELETE USING (
                bucket_id = 'user-reports' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        -- Storage policies for user-uploads bucket
        CREATE POLICY "Users can upload own files" ON storage.objects
            FOR INSERT WITH CHECK (
                bucket_id = 'user-uploads' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        CREATE POLICY "Users can view own uploads" ON storage.objects
            FOR SELECT USING (
                bucket_id = 'user-uploads' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        CREATE POLICY "Users can delete own uploads" ON storage.objects
            FOR DELETE USING (
                bucket_id = 'user-uploads' AND
                auth.uid()::text = (storage.foldername(name))[1]
            );

        -- Public assets policies
        CREATE POLICY "Public assets are viewable by all" ON storage.objects
            FOR SELECT USING (bucket_id = 'public-assets');

        CREATE POLICY "Only admins can manage public assets" ON storage.objects
            FOR ALL USING (
                bucket_id = 'public-assets' AND
                EXISTS (
                    SELECT 1 FROM user_profiles
                    WHERE user_id = auth.uid() AND role = 'admin'
                )
            );

        -- System exports policies (admin only)
        CREATE POLICY "Only admins can manage system exports" ON storage.objects
            FOR ALL USING (
                bucket_id = 'system-exports' AND
                EXISTS (
                    SELECT 1 FROM user_profiles
                    WHERE user_id = auth.uid() AND role = 'admin'
                )
            );

        -- Bucket-level policies
        CREATE POLICY "Users can access own report bucket" ON storage.buckets
            FOR SELECT USING (id = 'user-reports');

        CREATE POLICY "Users can access uploads bucket" ON storage.buckets
            FOR SELECT USING (id = 'user-uploads');

        CREATE POLICY "Everyone can access public assets bucket" ON storage.buckets
            FOR SELECT USING (id = 'public-assets');

        CREATE POLICY "Admins can access system exports bucket" ON storage.buckets
            FOR SELECT USING (
                id = 'system-exports' AND
                EXISTS (
                    SELECT 1 FROM user_profiles
                    WHERE user_id = auth.uid() AND role = 'admin'
                )
            );
        """

        logger.info("📋 Storage RLS Policies SQL:")
        logger.info("=" * 80)
        logger.info(policies_sql)
        logger.info("=" * 80)
        logger.info("⚠️ Please execute the above SQL in your Supabase SQL Editor after creating buckets")

        return True

    def verify_storage_setup(self) -> Dict[str, Any]:
        """Verify storage buckets are set up correctly"""
        results = {
            "buckets_created": 0,
            "buckets_accessible": 0,
            "total_buckets": len(self.buckets_config),
            "bucket_details": [],
            "policies_needed": True
        }

        logger.info("🔍 Verifying storage bucket setup...")

        for bucket_name in self.buckets_config.keys():
            try:
                # Try to get bucket info
                bucket_info = self.supabase_client.storage.get_bucket(bucket_name)

                if bucket_info:
                    results["buckets_created"] += 1
                    results["bucket_details"].append(f"✅ Bucket '{bucket_name}' exists")

                    # Try to list files (this tests access)
                    try:
                        files = self.supabase_client.storage.from_(bucket_name).list()
                        results["buckets_accessible"] += 1
                        results["bucket_details"].append(f"   - Access verified, {len(files)} files found")
                    except Exception as e:
                        results["bucket_details"].append(f"   - Access limited: {str(e)[:50]}...")

                else:
                    results["bucket_details"].append(f"❌ Bucket '{bucket_name}' not found")

            except Exception as e:
                results["bucket_details"].append(f"❌ Bucket '{bucket_name}' error: {str(e)[:50]}...")

        return results

    def setup_storage(self) -> bool:
        """Complete storage setup process"""
        logger.info("🚀 Starting Supabase Storage Setup for Planning Explorer")
        logger.info("=" * 60)

        # Connect to Supabase
        if not self.connect():
            return False

        # Create all buckets
        buckets_created = 0
        for bucket_config in self.buckets_config.values():
            if self.create_bucket(bucket_config):
                buckets_created += 1

        logger.info(f"📊 Summary: {buckets_created}/{len(self.buckets_config)} buckets created/verified")

        # Generate storage policies
        logger.info("🔒 Generating storage RLS policies...")
        self.create_storage_policies()

        # Verify setup
        verification = self.verify_storage_setup()

        # Print results
        logger.info("\n📋 Storage Setup Results:")
        logger.info(f"   Buckets created/existing: {verification['buckets_created']}/{verification['total_buckets']}")
        logger.info(f"   Buckets accessible: {verification['buckets_accessible']}/{verification['total_buckets']}")

        for detail in verification["bucket_details"]:
            logger.info(f"   {detail}")

        success = verification["buckets_created"] >= len(self.buckets_config) * 0.8

        if success:
            logger.info("\n✅ Storage setup completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Execute the storage RLS policies in Supabase SQL Editor")
            logger.info("2. Test file upload/download functionality")
            logger.info("3. Configure file cleanup policies if needed")
        else:
            logger.error("\n❌ Storage setup completed with issues")

        return success

    def generate_storage_integration_code(self):
        """Generate helper code for storage integration"""
        integration_code = '''
# Supabase Storage Integration Helper Functions
# Add these to your FastAPI application

from supabase import Client
from typing import Optional, BinaryIO
import os
from datetime import datetime, timedelta

class PlanningExplorerStorage:
    """Storage helper for Planning Explorer"""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def upload_user_report(self, user_id: str, file_data: BinaryIO, filename: str) -> Optional[str]:
        """Upload a user report file"""
        try:
            file_path = f"{user_id}/reports/{datetime.now().strftime('%Y/%m')}/{filename}"

            result = self.client.storage.from_('user-reports').upload(
                file_path,
                file_data,
                file_options={
                    "content-type": "application/pdf",
                    "upsert": False
                }
            )

            if result:
                return self.client.storage.from_('user-reports').get_public_url(file_path)

        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    async def upload_user_file(self, user_id: str, file_data: BinaryIO, filename: str, content_type: str) -> Optional[str]:
        """Upload a user file"""
        try:
            file_path = f"{user_id}/uploads/{filename}"

            result = self.client.storage.from_('user-uploads').upload(
                file_path,
                file_data,
                file_options={
                    "content-type": content_type,
                    "upsert": True
                }
            )

            if result:
                return self.client.storage.from_('user-uploads').get_public_url(file_path)

        except Exception as e:
            print(f"Upload failed: {e}")
            return None

    async def delete_user_file(self, user_id: str, file_path: str, bucket: str = 'user-uploads') -> bool:
        """Delete a user file"""
        try:
            full_path = f"{user_id}/{file_path}"
            result = self.client.storage.from_(bucket).remove([full_path])
            return len(result) > 0
        except Exception as e:
            print(f"Delete failed: {e}")
            return False

    async def get_signed_url(self, file_path: str, bucket: str, expires_in: int = 3600) -> Optional[str]:
        """Get a signed URL for private file access"""
        try:
            result = self.client.storage.from_(bucket).create_signed_url(
                file_path,
                expires_in
            )
            return result['signedURL'] if result else None
        except Exception as e:
            print(f"Signed URL generation failed: {e}")
            return None

# Usage example:
# storage = PlanningExplorerStorage(supabase_client)
# url = await storage.upload_user_report(user_id, file_data, "market_analysis.pdf")
'''

        logger.info("\n💻 Storage Integration Code:")
        logger.info("=" * 80)
        logger.info(integration_code)
        logger.info("=" * 80)


def main():
    """Main setup function"""
    setup = SupabaseStorageSetup()
    success = setup.setup_storage()

    if success:
        setup.generate_storage_integration_code()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)