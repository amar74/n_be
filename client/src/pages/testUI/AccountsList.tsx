import React from 'react';
import AccountCard from './AccountCard';

const accountsData = [
  {
    id: 1,
    name: 'Los Angeles County Metropolitan Transportation Authority (Metro)',
    score: '92%',
    riskLevel: 'Low risk',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    location: 'Los Angeles, CA',
    office: 'West Coast Office',
    tier: 'Tier 1',
    category: 'Transportation',
    value: '$8.5M',
    valueColor: 'text-green-600',
    growth: '+15.3% Growth',
    borderColor: 'border-green-400',
    growthColor: 'text-green-400',
    growthBg: 'bg-green-50',
    riskColor: 'text-green-400',
    riskBg: 'bg-green-100',
    border: 'border-green-200',
    accName:'David Rodriguez'
  },
  {
    id: 2,
    name: 'Los Angeles County Metropolitan Transportation Authority (Metro)',
    score: '92%',
    riskLevel: 'Medium risk',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    location: 'Los Angeles, CA',
    office: 'West Coast Office',
    tier: 'Tier 1',
    category: 'Transportation',
    value: '$8.5M',
    valueColor: 'text-orange-400',
    growth: '+15.3% Growth',
    borderColor: 'border-orange-200',
    growthColor: 'text-orange-400',
    growthBg: 'bg-orange-50',
    riskColor: 'text-orange-400',
    riskBg: 'bg-orange-100',
    border: 'border-orange-200',
    accName:'David Rodriguez',

  },
  {
    id: 3,
    name: 'Los Angeles County Metropolitan Transportation Authority (Metro)',
    score: '92%',
    riskLevel: 'High risk',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    location: 'Los Angeles, CA',
    office: 'West Coast Office',
    tier: 'Tier 1',
    category: 'Transportation',
    value: '$8.5M',
    valueColor: 'text-red-400',
    growth: '+15.3% Growth',
    borderColor: 'border-red-200',
    growthColor: 'text-red-400',
    growthBg: 'bg-red-50',
    riskColor: 'text-red-600',
    riskBg: 'bg-red-100',
    accName:'David Rodriguez'
  },
];

const AccountsList: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 xl:gap-8">
      {accountsData.map((account) => (
        <AccountCard key={account.id} account={account}  />
      ))}
    </div>
  );
};

export default AccountsList;