#!/usr/bin/env python3
"""
Seed script to create sample clauses for each category in the clause library

Run with: python seed_clause_library.py
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.models.contract import ClauseLibraryItem, ClauseCategory, ClauseRiskLevel
from app.models.organization import Organization
from sqlalchemy import select
import uuid

# Sample clauses for each category
SAMPLE_CLAUSES = {
    'Risk Management': [
        {
            'title': 'Mutual Indemnification',
            'clause_text': 'Each party agrees to indemnify, defend, and hold harmless the other party, its affiliates, officers, directors, employees, and agents from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys\' fees) arising out of or relating to (i) breach of this Agreement by the indemnifying party, (ii) negligence or willful misconduct of the indemnifying party, or (iii) infringement of any third-party intellectual property rights by the indemnifying party.',
            'acceptable_alternatives': [
                'Unilateral indemnification in favor of Client',
                'Indemnification limited to direct damages only',
                'Indemnification with a cap on liability'
            ],
            'fallback_positions': [
                'No indemnification clause',
                'Indemnification limited to claims arising from Client\'s use of the services'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Insurance Requirements',
            'clause_text': 'Service Provider shall maintain, at its own expense, comprehensive general liability insurance, professional liability insurance, and workers\' compensation insurance, each with minimum coverage of $2,000,000 per occurrence and $5,000,000 aggregate. Service Provider shall provide Client with certificates of insurance upon request and shall name Client as an additional insured on its general liability policy.',
            'acceptable_alternatives': [
                'Lower coverage amounts ($1M/$3M)',
                'Self-insurance with appropriate reserves',
                'Insurance with higher deductibles'
            ],
            'fallback_positions': [
                'No insurance requirement',
                'Insurance requirement limited to professional liability only'
            ],
            'risk_level': ClauseRiskLevel.preferred
        }
    ],
    'Financial': [
        {
            'title': 'Payment Terms - Net 30',
            'clause_text': 'Client shall pay all undisputed invoices within thirty (30) days of the invoice date. Late payments shall bear interest at a rate of 1.5% per month or the maximum rate allowed by law, whichever is less. Client may withhold payment of any disputed amounts in good faith, provided that Client provides written notice of the dispute within ten (10) days of invoice receipt.',
            'acceptable_alternatives': [
                'Net 45 payment terms',
                'Net 15 payment terms with early payment discount',
                'Milestone-based payment schedule'
            ],
            'fallback_positions': [
                'Net 60 payment terms',
                'Payment upon completion of all services'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Price Adjustment Clause',
            'clause_text': 'All fees and prices specified in this Agreement are fixed for the initial term. For any renewal or extension period, Service Provider may increase fees by no more than the percentage increase in the Consumer Price Index (CPI) for the preceding twelve (12) months, provided that Service Provider provides written notice of any such increase at least sixty (60) days prior to the renewal date.',
            'acceptable_alternatives': [
                'Fixed pricing for renewal terms',
                'Price adjustment based on market rates with Client approval',
                'Annual increase cap of 5%'
            ],
            'fallback_positions': [
                'Unlimited price increases with notice',
                'Market rate pricing at renewal'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Intellectual Property': [
        {
            'title': 'Work Product Ownership',
            'clause_text': 'All work product, deliverables, materials, and intellectual property created by Service Provider in the performance of this Agreement ("Work Product") shall be and remain the exclusive property of Client. Service Provider hereby assigns to Client all right, title, and interest in and to the Work Product, including all intellectual property rights therein. Service Provider retains no rights to use the Work Product except as expressly set forth in this Agreement.',
            'acceptable_alternatives': [
                'Joint ownership of work product',
                'Service Provider retains rights to pre-existing IP and methodologies',
                'Client receives license to use work product'
            ],
            'fallback_positions': [
                'Service Provider retains ownership, Client receives license',
                'Work product ownership based on funding source'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Background IP Protection',
            'clause_text': 'Each party retains all right, title, and interest in its pre-existing intellectual property ("Background IP"). Nothing in this Agreement shall be construed to grant either party any ownership rights in the other party\'s Background IP. Service Provider grants Client a non-exclusive, royalty-free license to use Service Provider\'s Background IP solely as necessary to use the Work Product.',
            'acceptable_alternatives': [
                'Non-exclusive license to Background IP for term of Agreement',
                'Background IP license with restrictions on use',
                'Background IP owned by party that developed it'
            ],
            'fallback_positions': [
                'No license to Background IP',
                'Background IP becomes part of Work Product'
            ],
            'risk_level': ClauseRiskLevel.preferred
        }
    ],
    'Termination': [
        {
            'title': 'Termination for Convenience',
            'clause_text': 'Either party may terminate this Agreement at any time for convenience upon sixty (60) days\' prior written notice to the other party. Upon termination for convenience, Client shall pay Service Provider for all services performed and expenses incurred through the effective date of termination, plus any cancellation fees set forth in the applicable Statement of Work. Service Provider shall deliver to Client all work product completed through the date of termination.',
            'acceptable_alternatives': [
                'Thirty (30) days\' notice for termination for convenience',
                'Ninety (90) days\' notice for termination for convenience',
                'Termination for convenience with payment for remaining term'
            ],
            'fallback_positions': [
                'No termination for convenience right',
                'Termination for convenience only by Client'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Termination for Cause',
            'clause_text': 'Either party may terminate this Agreement immediately upon written notice if the other party (i) materially breaches this Agreement and fails to cure such breach within thirty (30) days after written notice of the breach, (ii) becomes insolvent or files for bankruptcy, or (iii) ceases to conduct business in the ordinary course. Upon termination for cause, the non-breaching party shall have all rights and remedies available at law or in equity.',
            'acceptable_alternatives': [
                'Fifteen (15) day cure period for material breach',
                'Ten (10) day cure period for payment breaches, thirty (30) days for other breaches',
                'Immediate termination for certain breaches with no cure period'
            ],
            'fallback_positions': [
                'Sixty (60) day cure period for all breaches',
                'Termination for cause requires court order'
            ],
            'risk_level': ClauseRiskLevel.preferred
        }
    ],
    'Confidentiality': [
        {
            'title': 'Mutual Non-Disclosure',
            'clause_text': 'Each party agrees to hold in strict confidence and not to disclose, disseminate, or use for any purpose other than as necessary to perform this Agreement, any Confidential Information of the other party. "Confidential Information" includes all non-public, proprietary, or confidential information disclosed by one party to the other, whether orally, in writing, or in any other form. This obligation shall survive termination of this Agreement for a period of five (5) years, except for trade secrets which shall be protected in perpetuity.',
            'acceptable_alternatives': [
                'Three (3) year confidentiality obligation',
                'Confidentiality obligation for term of Agreement plus two (2) years',
                'Perpetual confidentiality for all information marked as confidential'
            ],
            'fallback_positions': [
                'One (1) year confidentiality obligation',
                'Confidentiality obligation only during term of Agreement'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Data Protection and Security',
            'clause_text': 'Service Provider shall implement and maintain reasonable administrative, physical, and technical safeguards to protect Client\'s data from unauthorized access, use, disclosure, alteration, or destruction. Service Provider shall comply with all applicable data protection laws and regulations, including but not limited to GDPR, CCPA, and HIPAA, as applicable. Service Provider shall promptly notify Client of any data breach affecting Client\'s data.',
            'acceptable_alternatives': [
                'Industry-standard security measures',
                'Security measures as specified in separate security addendum',
                'Compliance with specific security standards (e.g., SOC 2, ISO 27001)'
            ],
            'fallback_positions': [
                'Best efforts security measures',
                'Security measures as determined by Service Provider'
            ],
            'risk_level': ClauseRiskLevel.preferred
        }
    ],
    'Service Level': [
        {
            'title': 'Service Level Agreement',
            'clause_text': 'Service Provider shall maintain a minimum service availability of 99.9% as measured on a monthly basis, excluding scheduled maintenance windows and force majeure events. If Service Provider fails to meet this service level, Client shall be entitled to a service credit equal to 10% of the monthly service fee for each 0.1% below the target availability, up to a maximum of 100% of the monthly service fee. Service credits shall be applied to the next invoice.',
            'acceptable_alternatives': [
                '99.5% availability with 5% service credits',
                '99.95% availability with 15% service credits',
                'Availability targets and credits as specified in Statement of Work'
            ],
            'fallback_positions': [
                'Best efforts availability with no service credits',
                'No specific availability targets'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Response Time Commitments',
            'clause_text': 'Service Provider shall respond to Client\'s support requests within the following timeframes: (i) critical issues (system down or major functionality unavailable) within two (2) hours, (ii) high priority issues within four (4) business hours, and (iii) standard priority issues within one (1) business day. Response times are measured from the time Client submits a support request during Service Provider\'s standard business hours.',
            'acceptable_alternatives': [
                'Response times based on severity levels with different targets',
                'Response times during business hours only',
                'Response times with escalation procedures'
            ],
            'fallback_positions': [
                'Best efforts response with no specific timeframes',
                'Response times subject to Service Provider\'s availability'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Warranty': [
        {
            'title': 'Performance Warranty',
            'clause_text': 'Service Provider warrants that (i) the services will be performed in a professional and workmanlike manner by qualified personnel, (ii) the services will conform to the specifications set forth in the applicable Statement of Work, and (iii) Service Provider has the right and authority to enter into this Agreement and to perform the services. EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT, SERVICE PROVIDER MAKES NO WARRANTIES, EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.',
            'acceptable_alternatives': [
                'Warranty limited to material compliance with specifications',
                'Warranty with specific remedy for breach',
                'Warranty period of one (1) year from delivery'
            ],
            'fallback_positions': [
                'Services provided "as is" with no warranties',
                'Best efforts warranty only'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Remedy for Breach of Warranty',
            'clause_text': 'If Service Provider breaches any warranty set forth in this Agreement, Service Provider shall, at Client\'s option, either (i) re-perform the non-conforming services at no additional cost to Client, or (ii) refund to Client the fees paid for the non-conforming services. This shall be Client\'s exclusive remedy for breach of warranty, except for claims arising from Service Provider\'s fraud, gross negligence, or willful misconduct.',
            'acceptable_alternatives': [
                'Remedy includes costs of correcting non-conforming services',
                'Remedy includes additional damages up to amount paid for services',
                'Remedy period of ninety (90) days from discovery of breach'
            ],
            'fallback_positions': [
                'No specific remedy, general damages only',
                'Remedy limited to re-performance only'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Limitation of Liability': [
        {
            'title': 'Liability Cap',
            'clause_text': 'IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER PARTY FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION LOSS OF PROFITS, LOSS OF DATA, OR LOSS OF BUSINESS OPPORTUNITIES, ARISING OUT OF OR RELATING TO THIS AGREEMENT, REGARDLESS OF THE THEORY OF LIABILITY. EACH PARTY\'S TOTAL LIABILITY FOR ALL CLAIMS ARISING OUT OF OR RELATING TO THIS AGREEMENT SHALL NOT EXCEED THE AMOUNT PAID BY CLIENT TO SERVICE PROVIDER UNDER THIS AGREEMENT IN THE TWELVE (12) MONTHS PRECEDING THE EVENT GIVING RISE TO THE CLAIM.',
            'acceptable_alternatives': [
                'Liability cap equal to annual contract value',
                'Liability cap of two (2) times annual fees',
                'No cap on direct damages, cap only on indirect damages'
            ],
            'fallback_positions': [
                'Unlimited liability',
                'Liability cap equal to total contract value'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Exclusions from Liability Cap',
            'clause_text': 'The liability cap set forth in this Agreement shall not apply to (i) breaches of confidentiality obligations, (ii) indemnification obligations, (iii) fraud, gross negligence, or willful misconduct, (iv) infringement of intellectual property rights, or (v) payment obligations. For these categories of claims, each party\'s liability shall be unlimited to the extent permitted by applicable law.',
            'acceptable_alternatives': [
                'Liability cap applies to all claims without exception',
                'Limited exceptions for fraud and willful misconduct only',
                'Exceptions apply but with sub-caps'
            ],
            'fallback_positions': [
                'All exceptions apply with unlimited liability',
                'Exceptions defined broadly to include all breaches'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Dispute Resolution': [
        {
            'title': 'Arbitration Clause',
            'clause_text': 'Any dispute, controversy, or claim arising out of or relating to this Agreement, including its interpretation, performance, or breach, shall be resolved through binding arbitration administered by the American Arbitration Association (AAA) under its Commercial Arbitration Rules. The arbitration shall be conducted by a single arbitrator in [City, State], and judgment on the award rendered by the arbitrator may be entered in any court having jurisdiction thereof. The prevailing party shall be entitled to recover its reasonable attorneys\' fees and costs.',
            'acceptable_alternatives': [
                'Mediation before arbitration',
                'Arbitration under JAMS rules',
                'Arbitration with three arbitrators for disputes over $500,000'
            ],
            'fallback_positions': [
                'Litigation in state or federal courts',
                'No dispute resolution clause'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Governing Law',
            'clause_text': 'This Agreement shall be governed by and construed in accordance with the laws of the State of [State], without regard to its conflict of laws principles. The parties agree that the state and federal courts located in [County], [State] shall have exclusive jurisdiction over any disputes not subject to arbitration.',
            'acceptable_alternatives': [
                'Governing law of Client\'s state',
                'Governing law of Service Provider\'s state',
                'New York law with New York courts'
            ],
            'fallback_positions': [
                'Governing law as determined by court',
                'No governing law clause'
            ],
            'risk_level': ClauseRiskLevel.preferred
        }
    ],
    'Force Majeure': [
        {
            'title': 'Force Majeure Events',
            'clause_text': 'Neither party shall be liable for any failure or delay in performance under this Agreement due to causes beyond its reasonable control, including but not limited to acts of God, war, terrorism, earthquakes, floods, fires, epidemics, pandemics, labor strikes, government actions, or failures of third-party services or infrastructure ("Force Majeure Events"). The affected party shall provide prompt notice to the other party of any Force Majeure Event and shall use commercially reasonable efforts to resume performance as soon as practicable.',
            'acceptable_alternatives': [
                'Force majeure limited to specific events listed',
                'Force majeure includes cyber attacks and data breaches',
                'Force majeure with obligation to find alternative means of performance'
            ],
            'fallback_positions': [
                'No force majeure clause',
                'Force majeure applies only to natural disasters'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Termination for Extended Force Majeure',
            'clause_text': 'If a Force Majeure Event prevents either party from performing its obligations under this Agreement for a period exceeding sixty (60) consecutive days, the other party may terminate this Agreement upon written notice. Upon such termination, each party shall be relieved of its obligations under this Agreement, except for obligations that accrued prior to the Force Majeure Event and obligations of confidentiality and payment for services rendered.',
            'acceptable_alternatives': [
                'Thirty (30) day period before termination right',
                'Ninety (90) day period before termination right',
                'Termination with prorated refund of prepaid fees'
            ],
            'fallback_positions': [
                'No termination right for extended force majeure',
                'Unlimited extension for force majeure events'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Change Management': [
        {
            'title': 'Change Order Process',
            'clause_text': 'Either party may request changes to the scope, specifications, or deliverables under this Agreement by submitting a written change request. Service Provider shall provide Client with an estimate of the impact of the requested change on the schedule, fees, and resources within ten (10) business days. No change shall be effective unless and until it is set forth in a written change order executed by both parties. Client shall pay Service Provider for all work performed in connection with approved change orders.',
            'acceptable_alternatives': [
                'Change orders approved by email confirmation',
                'Five (5) business day response time for change requests',
                'Changes automatically approved if not objected to within timeframe'
            ],
            'fallback_positions': [
                'Verbal change orders accepted',
                'No formal change order process'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Scope Creep Protection',
            'clause_text': 'Service Provider shall not be obligated to perform any services beyond the scope set forth in the applicable Statement of Work unless a change order is executed. If Client requests services outside the scope of work, Service Provider may (i) decline to perform such services, or (ii) perform such services subject to a change order and payment of additional fees. Service Provider\'s failure to object to scope creep shall not constitute a waiver of its right to compensation.',
            'acceptable_alternatives': [
                'Scope defined as work reasonably necessary to complete deliverables',
                'Minor scope changes included in base fee',
                'Scope changes with mutual good faith negotiation'
            ],
            'fallback_positions': [
                'No protection against scope creep',
                'All requested services included in base fee'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ],
    'Compliance': [
        {
            'title': 'Regulatory Compliance',
            'clause_text': 'Service Provider represents and warrants that it shall comply with all applicable laws, regulations, and industry standards in the performance of the services, including but not limited to export control laws, anti-corruption laws (e.g., FCPA, UK Bribery Act), data protection laws, and employment laws. Service Provider shall maintain all necessary licenses, permits, and certifications required to perform the services.',
            'acceptable_alternatives': [
                'Compliance with laws of Service Provider\'s jurisdiction',
                'Compliance with laws of Client\'s jurisdiction',
                'Compliance with specific regulatory requirements as identified'
            ],
            'fallback_positions': [
                'Best efforts compliance',
                'Compliance as determined by Service Provider'
            ],
            'risk_level': ClauseRiskLevel.preferred
        },
        {
            'title': 'Audit Rights',
            'clause_text': 'Upon reasonable notice and during normal business hours, Service Provider shall allow Client or its designated representative to audit Service Provider\'s compliance with this Agreement, including its data security practices, compliance with applicable laws, and accuracy of invoices and records. Service Provider shall provide reasonable cooperation with such audits. Client shall bear the costs of audits unless the audit reveals material non-compliance, in which case Service Provider shall bear the costs.',
            'acceptable_alternatives': [
                'Annual audit rights with advance notice',
                'Audit rights limited to specific areas',
                'Audit with third-party auditors approved by Service Provider'
            ],
            'fallback_positions': [
                'No audit rights',
                'Audit rights only with court order'
            ],
            'risk_level': ClauseRiskLevel.acceptable
        }
    ]
}


async def seed_clause_library():
    """Seed sample clauses into the clause library for each category."""
    print("🌱 Starting clause library seeding...")
    
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
                
                # Get existing categories for this org
                categories_result = await db.execute(
                    select(ClauseCategory).where(ClauseCategory.org_id == org.id)
                )
                categories = {cat.name: cat for cat in categories_result.scalars().all()}
                
                if not categories:
                    print(f"   ⚠️  No categories found for this organization. Skipping.")
                    continue
                
                # Get existing clauses for this org to avoid duplicates
                clauses_result = await db.execute(
                    select(ClauseLibraryItem).where(ClauseLibraryItem.org_id == org.id)
                )
                existing_clauses = {(clause.title.lower(), clause.category.lower()) for clause in clauses_result.scalars().all()}
                
                # Seed clauses for each category
                for category_name, clauses_data in SAMPLE_CLAUSES.items():
                    if category_name not in categories:
                        print(f"   ⚠️  Category '{category_name}' not found. Skipping.")
                        continue
                    
                    category = categories[category_name]
                    
                    for clause_data in clauses_data:
                        clause_key = (clause_data['title'].lower(), category_name.lower())
                        
                        if clause_key in existing_clauses:
                            print(f"   ⏭️  Skipping '{clause_data['title']}' in '{category_name}' (already exists)")
                            total_skipped += 1
                            continue
                        
                        # Create new clause
                        clause = ClauseLibraryItem(
                            id=uuid.uuid4(),
                            org_id=org.id,
                            title=clause_data['title'],
                            category=category_name,
                            clause_text=clause_data['clause_text'],
                            acceptable_alternatives=clause_data.get('acceptable_alternatives', []),
                            fallback_positions=clause_data.get('fallback_positions', []),
                            risk_level=clause_data.get('risk_level', ClauseRiskLevel.preferred),
                            created_by=None,
                            version=1,
                        )
                        
                        db.add(clause)
                        print(f"   ✅ Created '{clause_data['title']}' in '{category_name}'")
                        total_created += 1
                
                # Commit for this organization
                await db.commit()
            
            print(f"\n🎉 Seeding completed!")
            print(f"   Created: {total_created} clauses")
            print(f"   Skipped: {total_skipped} clauses (already exist)")
            
    except Exception as e:
        print(f"❌ Error seeding clause library: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_clause_library())

