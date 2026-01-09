"""
Script to fix the contract risk_level enum conflict.
This renames the enum from risk_level to contract_risk_level for contracts table.
"""
import asyncio
from sqlalchemy import text
from app.db.session import get_async_session

async def fix_enum():
    async for db in get_async_session():
        try:
            # Check if contract_risk_level enum exists
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'contract_risk_level'
                )
            """))
            exists = result.scalar()
            
            if not exists:
                # Create the new enum
                await db.execute(text("""
                    CREATE TYPE contract_risk_level AS ENUM ('low', 'medium', 'high')
                """))
                print("Created contract_risk_level enum")
            
            # Check if contracts table exists and what enum it's using
            result = await db.execute(text("""
                SELECT column_name, udt_name 
                FROM information_schema.columns 
                WHERE table_name = 'contracts' AND column_name = 'risk_level'
            """))
            col_info = result.fetchone()
            
            if col_info:
                current_enum = col_info[1]
                print(f"Current enum type for contracts.risk_level: {current_enum}")
                
                if current_enum != 'contract_risk_level':
                    # Alter the column to use the new enum
                    await db.execute(text("""
                        ALTER TABLE contracts 
                        ALTER COLUMN risk_level TYPE contract_risk_level 
                        USING risk_level::text::contract_risk_level
                    """))
                    print("Updated contracts.risk_level to use contract_risk_level enum")
                else:
                    print("contracts.risk_level already uses contract_risk_level enum")
            else:
                print("contracts table or risk_level column not found")
            
            await db.commit()
            print("Fix completed successfully!")
            
        except Exception as e:
            await db.rollback()
            print(f"Error: {e}")
            raise
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(fix_enum())

