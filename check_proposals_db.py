#!/usr/bin/env python3
"""
Script to check if proposals database tables exist and verify data storage
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.db.session import engine, AsyncSessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def check_database():
    """Check if proposals tables exist and verify data storage"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if proposals table exists using sync engine for inspection
            sync_engine = engine.sync_engine
            inspector = inspect(sync_engine)
            tables = inspector.get_table_names()
            
            print("\n" + "=" * 60)
            print("DATABASE TABLES CHECK")
            print("=" * 60)
            print(f"Total tables found: {len(tables)}")
            
            # Check proposals-related tables
            proposal_tables = {
                "proposals": "proposals" in tables,
                "proposal_sections": "proposal_sections" in tables,
                "proposal_documents": "proposal_documents" in tables,
                "proposal_approvals": "proposal_approvals" in tables,
            }
            
            for table_name, exists in proposal_tables.items():
                status = "✅ EXISTS" if exists else "❌ MISSING"
                print(f"  {table_name:25s}: {status}")
            
            if not all(proposal_tables.values()):
                print("\n⚠️  WARNING: Some proposal tables are missing!")
                print("   Run migrations: poetry run python manage.py upgrade")
                return False
            
            # Check proposals table structure
            if "proposals" in tables:
                print("\n" + "=" * 60)
                print("PROPOSALS TABLE STRUCTURE")
                print("=" * 60)
                columns = inspector.get_columns("proposals")
                
                # Check for critical columns
                critical_columns = [
                    "id", "org_id", "proposal_number", "title", "status",
                    "proposal_type", "version", "currency", "created_at"
                ]
                
                column_names = [col["name"] for col in columns]
                for col_name in critical_columns:
                    exists = col_name in column_names
                    status = "✅" if exists else "❌"
                    print(f"  {col_name:25s}: {status}")
                    
                    if not exists:
                        print(f"\n❌ ERROR: Critical column '{col_name}' is missing!")
                        return False
                
                # Check for unique constraint on proposal_number
                indexes = inspector.get_indexes("proposals")
                unique_indexes = [idx for idx in indexes if idx.get("unique", False)]
                has_unique_proposal_number = any(
                    "proposal_number" in idx["column_names"] 
                    for idx in unique_indexes
                )
                
                print(f"\n  proposal_number unique constraint: {'✅ EXISTS' if has_unique_proposal_number else '❌ MISSING'}")
                
                # Count existing proposals
                print("\n" + "=" * 60)
                print("PROPOSALS DATA CHECK")
                print("=" * 60)
                
                try:
                    result = await session.execute(text("SELECT COUNT(*) FROM proposals"))
                    count = result.scalar()
                    print(f"Total proposals in database: {count}")
                    
                    if count > 0:
                        # Get recent proposals
                        result = await session.execute(
                            text("""
                                SELECT id, proposal_number, title, status, 
                                       proposal_type, currency, version, created_at 
                                FROM proposals 
                                ORDER BY created_at DESC 
                                LIMIT 5
                            """)
                        )
                        proposals = result.fetchall()
                        
                        print(f"\nRecent proposals (last {len(proposals)}):")
                        print("-" * 60)
                        for prop in proposals:
                            print(f"  • {prop[1]} | {prop[2][:40]:40s} | {prop[3]:15s}")
                            print(f"    ID: {prop[0]}, Type: {prop[4]}, Currency: {prop[5]}, Version: {prop[6]}")
                            print(f"    Created: {prop[7]}")
                            print()
                        
                        # Check for any recent proposals (last hour)
                        result = await session.execute(
                            text("""
                                SELECT COUNT(*) 
                                FROM proposals 
                                WHERE created_at > NOW() - INTERVAL '1 hour'
                            """)
                        )
                        recent_count = result.scalar()
                        print(f"Proposals created in last hour: {recent_count}")
                    else:
                        print("⚠️  No proposals found in database yet.")
                        print("   This is normal if no proposals have been created.")
                    
                except Exception as e:
                    print(f"❌ ERROR querying proposals: {e}")
                    return False
            
            print("\n" + "=" * 60)
            print("✅ DATABASE CHECK COMPLETE")
            print("=" * 60)
            return True
            
    except OperationalError as e:
        print(f"\n❌ DATABASE CONNECTION ERROR: {e}")
        print("   Check your DATABASE_URL in .env file")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)

