#!/usr/bin/env python3
"""
Seed script to create default clause categories in the database

Run with: python seed_clause_categories.py
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.models.contract import ClauseCategory
from app.models.organization import Organization
from app.models import *
from sqlalchemy import select
import uuid

DEFAULT_CATEGORIES = [
    {
        'name': 'Risk Management',
        'description': 'Clauses related to risk allocation, indemnification, and liability',
    },
    {
        'name': 'Financial',
        'description': 'Payment terms, pricing, invoicing, and financial obligations',
    },
    {
        'name': 'Intellectual Property',
        'description': 'IP ownership, licensing, and protection clauses',
    },
    {
        'name': 'Termination',
        'description': 'Termination rights, notice periods, and exit conditions',
    },
    {
        'name': 'Confidentiality',
        'description': 'NDA, confidentiality, and data protection clauses',
    },
    {
        'name': 'Service Level',
        'description': 'SLA, performance metrics, and service delivery standards',
    },
    {
        'name': 'Warranty',
        'description': 'Warranties, guarantees, and disclaimers',
    },
    {
        'name': 'Limitation of Liability',
        'description': 'Liability caps, exclusions, and damage limitations',
    },
    {
        'name': 'Dispute Resolution',
        'description': 'Arbitration, mediation, and governing law clauses',
    },
    {
        'name': 'Force Majeure',
        'description': 'Force majeure events and excusable delays',
    },
    {
        'name': 'Change Management',
        'description': 'Change orders, scope modifications, and amendments',
    },
    {
        'name': 'Compliance',
        'description': 'Regulatory compliance, certifications, and standards',
    },
]


async def seed_clause_categories():
    """Seed default clause categories into the database."""
    print("🌱 Starting clause category seeding...")
    
    try:
        async with get_session() as db:
            # Get all organizations
            result = await db.execute(select(Organization))
            organizations = result.scalars().all()
            
            if not organizations:
                print("⚠️  No organizations found in the database.")
                print("Please create an organization first.")
                return
            
            total_created = 0
            total_skipped = 0
            
            for org in organizations:
                print(f"\n📋 Processing organization: {org.name} (ID: {org.id})")
                
                # Check existing categories for this org
                existing_result = await db.execute(
                    select(ClauseCategory).where(ClauseCategory.org_id == org.id)
                )
                existing_categories = {cat.name.lower() for cat in existing_result.scalars().all()}
                
                for category_data in DEFAULT_CATEGORIES:
                    category_name_lower = category_data['name'].lower()
                    
                    if category_name_lower in existing_categories:
                        print(f"   ⏭️  Skipping '{category_data['name']}' (already exists)")
                        total_skipped += 1
                        continue
                    
                    # Create new category
                    category = ClauseCategory(
                        id=uuid.uuid4(),
                        org_id=org.id,
                        name=category_data['name'],
                        description=category_data['description'],
                        created_by=None,
                    )
                    
                    db.add(category)
                    print(f"   ✅ Created '{category_data['name']}'")
                    total_created += 1
                
                # Commit for this organization
                await db.commit()
            
            print(f"\n🎉 Seeding completed!")
            print(f"   Created: {total_created} categories")
            print(f"   Skipped: {total_skipped} categories (already exist)")
            
    except Exception as e:
        print(f"❌ Error seeding clause categories: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_clause_categories())

