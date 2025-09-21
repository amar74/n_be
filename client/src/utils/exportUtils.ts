import { AccountListItem } from '@/types/accounts';

// Helper to format date strings
const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString();
};

// Helper to format address
const formatAddress = (address: any): string => {
  if (!address) return '';
  const parts = [
    address.line1,
    address.line2,
    address.city,
    address.pincode
  ].filter(Boolean);
  return parts.join(', ');
};

// Convert accounts data to CSV format
export const exportToCSV = (accounts: AccountListItem[]): void => {
  // Define headers and corresponding data keys
  const headers = [
    'Client Name',
    'Client Type',
    'Market Sector',
    'Address',
    'Primary Contact Name',
    'Primary Contact Email',
    'Total Value',
    'AI Health Score',
    'Last Contact'
  ];

  // Transform accounts data into rows
  const rows = accounts.map(account => [
    account.client_name,
    account.client_type,
    account.market_sector || '',
    formatAddress(account.client_address),
    account.primary_contact_name || '',
    account.primary_contact_email || '',
    account.total_value?.toString() || '',
    account.ai_health_score?.toString() || '',
    formatDate(account.last_contact)
  ]);

  // Combine headers and rows
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\n');

  // Create and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `accounts_export_${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
};

// Convert accounts data to Excel format
export const exportToExcel = async (accounts: AccountListItem[]): Promise<void> => {
  try {
    // Dynamically import XLSX only when needed
    const XLSX = await import('xlsx');
    
    // Prepare data for Excel
    const excelData = accounts.map(account => ({
      'Client Name': account.client_name,
      'Client Type': account.client_type,
      'Market Sector': account.market_sector || '',
      'Address': formatAddress(account.client_address),
      'Primary Contact Name': account.primary_contact_name || '',
      'Primary Contact Email': account.primary_contact_email || '',
      'Total Value': account.total_value || '',
      'AI Health Score': account.ai_health_score || '',
      'Last Contact': formatDate(account.last_contact)
    }));

    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.json_to_sheet(excelData);

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, 'Accounts');

    // Generate Excel file and trigger download
    XLSX.writeFile(wb, `accounts_export_${new Date().toISOString().split('T')[0]}.xlsx`);
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    throw new Error('Failed to export to Excel. Please try again.');
  }
};
