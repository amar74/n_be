#!/usr/bin/env python3
"""
Seed script to create a test proposal linked to an existing opportunity

Run with: poetry run python seed_proposal.py
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta, timezone

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.models.proposal import Proposal, ProposalStatus, ProposalSource, ProposalType
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.models.user import User
from app.models.account import Account
from sqlalchemy import select
import uuid


async def seed_proposal():
    """Seed a test proposal linked to an existing opportunity"""
    print("🌱 Starting proposal seeding...")
    
    try:
        async with get_session() as db:
            # Get first organization
            org_result = await db.execute(select(Organization).limit(1))
            org = org_result.scalar_one_or_none()
            
            if not org:
                print("⚠️  No organizations found in the database.")
                print("Please create an organization first.")
                return
            
            print(f"📋 Using organization: {org.name} (ID: {org.id})")
            
            # Find an opportunity with account_id
            opp_result = await db.execute(
                select(Opportunity)
                .where(Opportunity.org_id == org.id)
                .where(Opportunity.account_id.isnot(None))
                .limit(1)
            )
            opportunity = opp_result.scalar_one_or_none()
            
            if not opportunity:
                print("⚠️  No opportunities with account found.")
                print("Creating a proposal without opportunity link...")
                opportunity_id = None
                account_id = None
            else:
                opportunity_id = opportunity.id
                account_id = opportunity.account_id
                print(f"✅ Found opportunity: {opportunity.project_name} (ID: {opportunity.id})")
                print(f"   Client: {opportunity.client_name}")
                print(f"   Account ID: {account_id}")
            
            # If no opportunity with account, try to find any opportunity
            if not opportunity:
                opp_result = await db.execute(
                    select(Opportunity)
                    .where(Opportunity.org_id == org.id)
                    .limit(1)
                )
                opportunity = opp_result.scalar_one_or_none()
                if opportunity:
                    opportunity_id = opportunity.id
                    account_id = opportunity.account_id
                    print(f"✅ Found opportunity without account: {opportunity.project_name} (ID: {opportunity.id})")
                    print(f"   Client: {opportunity.client_name}")
            
            # If still no opportunity, try to find an account directly
            if not account_id:
                account_result = await db.execute(
                    select(Account)
                    .where(Account.org_id == org.id)
                    .limit(1)
                )
                account = account_result.scalar_one_or_none()
                if account:
                    account_id = account.account_id
                    print(f"✅ Found account: {account.name} (ID: {account_id})")
            
            # Get a user to assign as creator/owner
            user_result = await db.execute(
                select(User).where(User.org_id == org.id).limit(1)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                print("⚠️  No users found for this organization.")
                print("Creating proposal without user assignment...")
                user_id = None
            else:
                user_id = user.id
                print(f"✅ Using user: {user.email} (ID: {user_id})")
            
            # Generate proposal number
            year = datetime.now(timezone.utc).year
            unique_suffix = str(uuid.uuid4())[:8].upper()
            proposal_number = f"PROP-{year}-0001-{unique_suffix}"
            
            # Check if proposal number already exists
            existing_prop_result = await db.execute(
                select(Proposal).where(Proposal.proposal_number == proposal_number)
            )
            if existing_prop_result.scalar_one_or_none():
                # Use different number
                proposal_number = f"PROP-{year}-{int(datetime.now(timezone.utc).timestamp())}-{unique_suffix}"
            
            # Create proposal with "won" status so it can be used for contract creation
            proposal = Proposal(
                id=uuid.uuid4(),
                org_id=org.id,
                opportunity_id=opportunity_id,
                account_id=account_id,
                created_by=user_id,
                owner_id=user_id,
                proposal_number=proposal_number,
                title=opportunity.project_name if opportunity else f"Test Proposal for {org.name}",
                summary="This is a test proposal created for contract module testing. It includes comprehensive project details and pricing information.",
                status=ProposalStatus.won,  # Set to "won" so it can be used for contract creation
                source=ProposalSource.opportunity if opportunity_id else ProposalSource.manual,
                proposal_type=ProposalType.proposal,
                version=1,
                total_value=125000.00,  # $125,000 contract value
                currency="USD",
                estimated_cost=95000.00,  # Estimated cost
                expected_margin=24.0,  # 24% margin
                submission_date=date.today() - timedelta(days=30),
                client_response_date=date.today() - timedelta(days=20),
                won_at=datetime.now(timezone.utc) - timedelta(days=15),
                approval_completed=True,
                notes="Test proposal seeded for contract creation testing",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            
            db.add(proposal)
            await db.commit()
            
            print(f"\n✅ Successfully created proposal:")
            print(f"   Proposal Number: {proposal_number}")
            print(f"   Title: {proposal.title}")
            print(f"   Status: {proposal.status.value}")
            print(f"   Value: ${proposal.total_value:,.2f} {proposal.currency}")
            print(f"   Opportunity ID: {opportunity_id}")
            print(f"   Account ID: {account_id}")
            print(f"   Proposal ID: {proposal.id}")
            print(f"\n🎉 Proposal seeded successfully!")
            print(f"   You can now use this proposal to create a contract in the frontend.")
            
    except Exception as e:
        print(f"❌ Error seeding proposal: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_proposal())

