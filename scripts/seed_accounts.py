"""
Seed script to create sample accounts with addresses and contacts
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import get_session
from app.models.account import Account, ClientType
from app.models.address import Address
from app.models.contact import Contact
from app.models.organization import Organization
from app.models.user import User
from sqlalchemy import select
import uuid
from datetime import datetime


async def seed_accounts():
    """Create sample accounts with addresses and contacts"""
    
    async with get_session() as db:
        # Get first organization
        result = await db.execute(select(Organization))
        org = result.scalar_one_or_none()
        
        if not org:
            print("❌ No organization found. Please create an organization first.")
            return
        
        print(f"✅ Found organization: {org.name} (ID: {org.id})")
        
        # Sample accounts data
        accounts_data = [
            {
                "client_name": "Los Angeles County Metropolitan Transportation Authority (Metro)",
                "company_website": "https://www.metro.net",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 2400000,  # $2.4M
                "ai_health_score": 92,
                "opportunities": 5,
                "address": {
                    "line1": "One Gateway Plaza",
                    "line2": "Suite 200",
                    "city": "Los Angeles",
                    "pincode": 90012
                },
                "contact": {
                    "name": "David Rodriguez",
                    "email": "d.rodriguez@metro.net",
                    "phone": "213-922-6000",
                    "title": "Director of Planning"
                }
            },
            {
                "client_name": "San Francisco Bay Area Rapid Transit (BART)",
                "company_website": "https://www.bart.gov",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 3200000,  # $3.2M
                "ai_health_score": 88,
                "opportunities": 7,
                "address": {
                    "line1": "2150 Webster Street",
                    "line2": None,
                    "city": "Oakland",
                    "pincode": 94612
                },
                "contact": {
                    "name": "Jennifer Kim",
                    "email": "j.kim@bart.gov",
                    "phone": "510-464-6000",
                    "title": "Chief Operating Officer"
                }
            },
            {
                "client_name": "Port of Long Beach",
                "company_website": "https://www.polb.com",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 5800000,  # $5.8M
                "ai_health_score": 95,
                "opportunities": 12,
                "address": {
                    "line1": "415 West Ocean Boulevard",
                    "line2": None,
                    "city": "Long Beach",
                    "pincode": 90802
                },
                "contact": {
                    "name": "Michael Chen",
                    "email": "m.chen@polb.com",
                    "phone": "562-283-7000",
                    "title": "Executive Director"
                }
            },
            {
                "client_name": "City of San Diego Public Works",
                "company_website": "https://www.sandiego.gov/publicworks",
                "client_type": ClientType.tier_2,
                "market_sector": "Government",
                "total_value": 1800000,  # $1.8M
                "ai_health_score": 76,
                "opportunities": 4,
                "address": {
                    "line1": "525 B Street",
                    "line2": "Suite 550",
                    "city": "San Diego",
                    "pincode": 92101
                },
                "contact": {
                    "name": "Sarah Johnson",
                    "email": "s.johnson@sandiego.gov",
                    "phone": "619-533-3000",
                    "title": "Public Works Director"
                }
            },
            {
                "client_name": "Orange County Transportation Authority",
                "company_website": "https://www.octa.net",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 4100000,  # $4.1M
                "ai_health_score": 68,
                "opportunities": 6,
                "address": {
                    "line1": "550 South Main Street",
                    "line2": None,
                    "city": "Orange",
                    "pincode": 92868
                },
                "contact": {
                    "name": "Robert Martinez",
                    "email": "r.martinez@octa.net",
                    "phone": "714-560-6282",
                    "title": "CEO"
                }
            },
            {
                "client_name": "Sacramento Regional Transit District",
                "company_website": "https://www.sacrt.com",
                "client_type": ClientType.tier_2,
                "market_sector": "Transportation",
                "total_value": 2700000,  # $2.7M
                "ai_health_score": 82,
                "opportunities": 5,
                "address": {
                    "line1": "1400 29th Street",
                    "line2": None,
                    "city": "Sacramento",
                    "pincode": 95816
                },
                "contact": {
                    "name": "Lisa Anderson",
                    "email": "l.anderson@sacrt.com",
                    "phone": "916-321-2800",
                    "title": "General Manager"
                }
            },
            {
                "client_name": "Los Angeles Department of Water and Power",
                "company_website": "https://www.ladwp.com",
                "client_type": ClientType.tier_1,
                "market_sector": "Energy",
                "total_value": 8500000,  # $8.5M
                "ai_health_score": 91,
                "opportunities": 15,
                "address": {
                    "line1": "111 North Hope Street",
                    "line2": None,
                    "city": "Los Angeles",
                    "pincode": 90012
                },
                "contact": {
                    "name": "James Wilson",
                    "email": "j.wilson@ladwp.com",
                    "phone": "213-367-4211",
                    "title": "Chief Engineer"
                }
            },
            {
                "client_name": "Caltrans District 7",
                "company_website": "https://dot.ca.gov/caltrans-near-me/district-7",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 12300000,  # $12.3M
                "ai_health_score": 45,
                "opportunities": 20,
                "address": {
                    "line1": "100 South Main Street",
                    "line2": None,
                    "city": "Los Angeles",
                    "pincode": 90012
                },
                "contact": {
                    "name": "Patricia Lee",
                    "email": "p.lee@dot.ca.gov",
                    "phone": "213-897-3656",
                    "title": "District Director"
                }
            },
            {
                "client_name": "Metropolitan Water District of Southern California",
                "company_website": "https://www.mwdh2o.com",
                "client_type": ClientType.tier_1,
                "market_sector": "Utilities",
                "total_value": 6900000,  # $6.9M
                "ai_health_score": 87,
                "opportunities": 10,
                "address": {
                    "line1": "700 North Alameda Street",
                    "line2": None,
                    "city": "Los Angeles",
                    "pincode": 90012
                },
                "contact": {
                    "name": "Thomas Garcia",
                    "email": "t.garcia@mwdh2o.com",
                    "phone": "213-217-6000",
                    "title": "General Manager"
                }
            },
            {
                "client_name": "San Diego County Regional Airport Authority",
                "company_website": "https://www.san.org",
                "client_type": ClientType.tier_2,
                "market_sector": "Transportation",
                "total_value": 3500000,  # $3.5M
                "ai_health_score": 79,
                "opportunities": 6,
                "address": {
                    "line1": "3225 North Harbor Drive",
                    "line2": None,
                    "city": "San Diego",
                    "pincode": 92101
                },
                "contact": {
                    "name": "Maria Hernandez",
                    "email": "m.hernandez@san.org",
                    "phone": "619-400-2404",
                    "title": "President & CEO"
                }
            },
            {
                "client_name": "Riverside County Transportation Commission",
                "company_website": "https://www.rctc.org",
                "client_type": ClientType.tier_2,
                "market_sector": "Transportation",
                "total_value": 2200000,  # $2.2M
                "ai_health_score": 73,
                "opportunities": 4,
                "address": {
                    "line1": "4080 Lemon Street",
                    "line2": "3rd Floor",
                    "city": "Riverside",
                    "pincode": 92501
                },
                "contact": {
                    "name": "Daniel Brown",
                    "email": "d.brown@rctc.org",
                    "phone": "951-787-7141",
                    "title": "Executive Director"
                }
            },
            {
                "client_name": "Port of Oakland",
                "company_website": "https://www.portofoakland.com",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 7200000,  # $7.2M
                "ai_health_score": 93,
                "opportunities": 14,
                "address": {
                    "line1": "530 Water Street",
                    "line2": None,
                    "city": "Oakland",
                    "pincode": 94607
                },
                "contact": {
                    "name": "Christopher Taylor",
                    "email": "c.taylor@portofoakland.com",
                    "phone": "510-627-1100",
                    "title": "Maritime Director"
                }
            },
            {
                "client_name": "Santa Clara Valley Transportation Authority",
                "company_website": "https://www.vta.org",
                "client_type": ClientType.tier_1,
                "market_sector": "Transportation",
                "total_value": 5400000,  # $5.4M
                "ai_health_score": 56,
                "opportunities": 8,
                "address": {
                    "line1": "3331 North First Street",
                    "line2": None,
                    "city": "San Jose",
                    "pincode": 95134
                },
                "contact": {
                    "name": "Amanda White",
                    "email": "a.white@vta.org",
                    "phone": "408-321-2300",
                    "title": "General Manager"
                }
            },
            {
                "client_name": "Fresno County Public Works",
                "company_website": "https://www.fresnocountyca.gov/publicworks",
                "client_type": ClientType.tier_3,
                "market_sector": "Government",
                "total_value": 1200000,  # $1.2M
                "ai_health_score": 65,
                "opportunities": 3,
                "address": {
                    "line1": "2220 Tulare Street",
                    "line2": "6th Floor",
                    "city": "Fresno",
                    "pincode": 93721
                },
                "contact": {
                    "name": "Kevin Thompson",
                    "email": "k.thompson@fresnocountyca.gov",
                    "phone": "559-600-4259",
                    "title": "Public Works Director"
                }
            },
            {
                "client_name": "Alameda County Public Works",
                "company_website": "https://www.acpwa.org",
                "client_type": ClientType.tier_2,
                "market_sector": "Government",
                "total_value": 2900000,  # $2.9M
                "ai_health_score": 81,
                "opportunities": 5,
                "address": {
                    "line1": "951 Turner Court",
                    "line2": None,
                    "city": "Hayward",
                    "pincode": 94545
                },
                "contact": {
                    "name": "Nicole Davis",
                    "email": "n.davis@acpwa.org",
                    "phone": "510-670-5400",
                    "title": "Agency Director"
                }
            }
        ]
        
        created_count = 0
        
        for account_data in accounts_data:
            try:
                # Create address
                address = Address(
                    id=uuid.uuid4(),
                    line1=account_data["address"]["line1"],
                    line2=account_data["address"]["line2"],
                    city=account_data["address"]["city"],
                    pincode=account_data["address"]["pincode"],
                    org_id=org.id
                )
                db.add(address)
                await db.flush()
                
                # Create contact
                contact = Contact(
                    id=uuid.uuid4(),
                    name=account_data["contact"]["name"],
                    email=account_data["contact"]["email"],
                    phone=account_data["contact"]["phone"],
                    title=account_data["contact"]["title"],
                    org_id=org.id
                )
                db.add(contact)
                await db.flush()
                
                # Create account
                account = Account(
                    account_id=uuid.uuid4(),
                    client_name=account_data["client_name"],
                    company_website=account_data["company_website"],
                    client_type=account_data["client_type"],
                    market_sector=account_data["market_sector"],
                    total_value=account_data["total_value"],
                    ai_health_score=account_data["ai_health_score"],
                    opportunities=account_data["opportunities"],
                    last_contact=datetime.now(),
                    client_address_id=address.id,
                    primary_contact_id=contact.id,
                    org_id=org.id
                )
                db.add(account)
                await db.flush()
                
                # Link contact to account
                contact.account_id = account.account_id
                
                created_count += 1
                print(f"✅ Created account: {account_data['client_name']}")
                
            except Exception as e:
                print(f"❌ Error creating account {account_data['client_name']}: {str(e)}")
                continue
        
        # Commit all changes
        await db.commit()
        
        print(f"\n🎉 Successfully created {created_count} accounts!")


if __name__ == "__main__":
    asyncio.run(seed_accounts())
