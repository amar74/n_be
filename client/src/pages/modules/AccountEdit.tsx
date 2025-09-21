import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { useAccountContacts, useAccountDetail, useAccounts } from '@/hooks/useAccounts';
import {  AccountUpdate, ContactFormData } from '@/types/accounts';
import { ArrowLeft, Building2, Save, X, Award, Edit, Users, Mail, Phone, Plus } from 'lucide-react';
import { Logo } from '@/components/ui/logo';

const AccountEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Use the new useAccounts hook
  const {
    updateAccount,
    addContact,
    updateContact,
    deleteContact,
    promoteContactToPrimary,
    isUpdating,
    isAddingContact,
    isUpdatingContact,
    isDeletingContact,
    isPromotingContact,
  } = useAccounts();

  // Use the account data from the hook
  const { accountDetail: account, isAccountDetailLoading: isLoading, accountDetailError: error } = useAccountDetail(id || '');
  const { accountContacts: contactsResponse } = useAccountContacts(id || '');
  const [editForm, setEditForm] = useState<AccountUpdate>({});

  // Contact management state
  const [showAddContactModal, setShowAddContactModal] = useState(false);
  const [showEditContactModal, setShowEditContactModal] = useState(false);
  const [showDeleteContactDialog, setShowDeleteContactDialog] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
  const [contactForm, setContactForm] = useState<ContactFormData>({
    name: '',
    email: '',
    phone: '',
    title: '',
  });

  // Initialize form with current account data when account loads
  useEffect(() => {
    if (account && account.client_name) {
      setEditForm({
        client_name: account.client_name,
        company_website: account.company_website || '',
        client_address:
          account.client_address && typeof account.client_address === 'object'
            ? {
                line1: account.client_address.line1 || '',
                line2: account.client_address.line2 || '',
                pincode: account.client_address.pincode || undefined,
              }
            : {
                line1: '',
                line2: '',
                pincode: undefined,
              },
        client_type: account.client_type,
        market_sector: account.market_sector || '',
        notes: account.notes || '',
      });
    }
  }, [account]);

  const handleUpdateAccount = async () => {
    if (!account?.account_id) return;

    try {
      await updateAccount({ accountId: account.account_id, data: editForm });

      toast({
        title: '✅ Account Updated',
        description: 'Account information has been updated successfully.',
      });

      // Navigate back to account details
      navigate(`/module/accounts/${account.account_id}`);
    } catch (error: any) {
      console.error('Error updating account:', error);
      toast({
        title: 'Error',
        description: 'Failed to update account. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleCancel = () => {
    navigate(`/module/accounts/${id}`);
  };

  // Contact management handlers
  const handleAddContact = () => {
    setContactForm({ name: '', email: '', phone: '', title: '' });
    setSelectedContactId(null);
    setShowAddContactModal(true);
  };

  const handleEditContact = (contact: any) => {
    setContactForm({
      name: contact.name,
      email: contact.email,
      phone: contact.phone,
      title: contact.title || '',
    });
    setSelectedContactId(contact.contact_id);
    setShowEditContactModal(true);
  };

  const handleDeleteContact = (contactId: string) => {
    setSelectedContactId(contactId);
    setShowDeleteContactDialog(true);
  };

  const handlePromoteContactToPrimary = async (contactId: string, contactName: string) => {
    if (!account?.account_id) {
      toast({
        title: 'Error',
        description: 'Account not found.',
        variant: 'destructive',
      });
      return;
    }

    // Show confirmation dialog
    const confirmed = confirm(
      `Are you sure you want to promote "${contactName}" to primary contact?\n\n` +
        `This will:\n` +
        `• Make "${contactName}" the primary contact\n` +
        `• Move the current primary contact to secondary contacts\n\n` +
        `This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      await promoteContactToPrimary({
        accountId: account.account_id,
        contactId: contactId,
      });
    } catch (error: any) {
      console.error('Error promoting contact:', error);
      // Error toast is handled by the mutation
    }
  };

  const submitAddContact = async () => {
    // Validation
    if (!account?.account_id) {
      toast({
        title: 'Error',
        description: 'Account not found.',
        variant: 'destructive',
      });
      return;
    }

    if (!contactForm.name?.trim() || !contactForm.email?.trim() || !contactForm.phone?.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields (Name, Email, Phone).',
        variant: 'destructive',
      });
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(contactForm.email.trim())) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a valid email address.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await addContact({
        accountId: account.account_id,
        contact: {
          contact:{
          name: contactForm.name.trim(),
          email: contactForm.email.trim(),
          phone: contactForm.phone.trim(),
          title: contactForm.title?.trim() || undefined,
        }},
      });

      toast({
        title: '✅ Contact Added',
        description: 'Contact has been added successfully.',
      });

      setShowAddContactModal(false);
      setContactForm({ name: '', email: '', phone: '', title: '' });
    } catch (error: any) {
      console.error('Error adding contact:', error);
      toast({
        title: 'Error',
        description:
          error.response?.data?.detail?.message || 'Failed to add contact. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const submitEditContact = async () => {
    // Validation
    if (!account?.account_id || !selectedContactId) {
      toast({
        title: 'Error',
        description: 'Account or contact not found.',
        variant: 'destructive',
      });
      return;
    }

    if (!contactForm.name?.trim() || !contactForm.email?.trim() || !contactForm.phone?.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields (Name, Email, Phone).',
        variant: 'destructive',
      });
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(contactForm.email.trim())) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a valid email address.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await updateContact({
        accountId: account.account_id,
        contactId: selectedContactId,
        contact: {
          name: contactForm.name.trim(),
          email: contactForm.email.trim(),
          phone: contactForm.phone.trim(),
          title: contactForm.title?.trim() || undefined,
        },
      });

      toast({
        title: '✅ Contact Updated',
        description: 'Contact has been updated successfully.',
      });

      setShowEditContactModal(false);
      setContactForm({ name: '', email: '', phone: '', title: '' });
    } catch (error: any) {
      console.error('Error updating contact:', error);
      toast({
        title: 'Error',
        description:
          error.response?.data?.detail?.message || 'Failed to update contact. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const confirmDeleteContact = async () => {
    if (!account?.account_id || !selectedContactId) {
      toast({
        title: 'Error',
        description: 'Account or contact not found.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await deleteContact({
        accountId: account.account_id,
        contactId: selectedContactId,
      });

      toast({
        title: '✅ Contact Deleted',
        description: 'Contact has been deleted successfully.',
      });

      setShowDeleteContactDialog(false);
    } catch (error: any) {
      console.error('Error deleting contact:', error);
      toast({
        title: 'Error',
        description:
          error.response?.data?.detail?.message || 'Failed to delete contact. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setSelectedContactId(null);
    }
  };

  const getClientTypeColor = (type: string) => {
    switch (type) {
      case 'tier_1':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'tier_2':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'tier_3':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getClientTypeLabel = (type: string) => {
    switch (type) {
      case 'tier_1':
        return 'Tier 1 - Premium';
      case 'tier_2':
        return 'Tier 2 - Standard';
      case 'tier_3':
        return 'Tier 3 - Basic';
      default:
        return type;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen">
        {/* Navigation Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/module/accounts">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Accounts
                </Button>
              </Link>
              <Separator orientation="vertical" className="h-6" />
              <Logo className="h-8 w-auto" />
            </div>
          </div>
        </div>

        {/* Loading State */}
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading account details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !account || !account.client_name) {
    return (
      <div className="min-h-screen">
        {/* Navigation Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/module/accounts">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Accounts
                </Button>
              </Link>
              <Separator orientation="vertical" className="h-6" />
              <Logo className="h-8 w-auto" />
            </div>
          </div>
        </div>

        {/* Error State */}
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 text-red-500 mb-4">
              <Building2 className="h-full w-full" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Account Not Found</h3>
            <p className="text-gray-600 mb-4">
              The account you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <Button onClick={() => navigate('/module/accounts')}>Return to Accounts</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Navigation Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to={`/module/accounts/${id}`}>
              <Button variant="ghost" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Account
              </Button>
            </Link>
            <Separator orientation="vertical" className="h-6" />
            <Logo className="h-8 w-auto" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900 flex items-center">
                <Edit className="h-5 w-5 mr-2" />
                Edit Account - {account?.client_name || 'Loading...'}
              </h1>
              <p className="text-sm text-gray-500">Update account information</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={handleCancel} disabled={isUpdating}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleUpdateAccount} disabled={isUpdating || !editForm.client_name}>
              {isUpdating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Account Preview Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Avatar className="h-12 w-12 mr-4">
                <AvatarFallback className="bg-blue-100 text-blue-600 text-lg font-semibold">
                  {editForm.client_name?.charAt(0) || account?.client_name?.charAt(0) || '?'}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-xl">
                  {editForm.client_name || account?.client_name || 'Loading...'}
                </h2>
                <div className="flex items-center mt-1">
                  <Badge
                    className={`mr-2 ${getClientTypeColor(editForm.client_type || account.client_type)}`}
                  >
                    <Award className="h-3 w-3 mr-1" />
                    {getClientTypeLabel(editForm.client_type || account.client_type)}
                  </Badge>
                  {(editForm.market_sector || account.market_sector) && (
                    <span className="text-sm text-gray-600">
                      {editForm.market_sector || account.market_sector}
                    </span>
                  )}
                </div>
              </div>
            </CardTitle>
          </CardHeader>
        </Card>

        {/* Edit Form */}
        <div className="space-y-8">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>
                Update the primary account information and classification
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="client-name">Client Name *</Label>
                  <Input
                    id="client-name"
                    value={editForm.client_name || ''}
                    onChange={e => setEditForm(prev => ({ ...prev, client_name: e.target.value }))}
                    placeholder="Enter client name"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="website">Company Website</Label>
                  <Input
                    id="website"
                    type="url"
                    value={editForm.company_website || ''}
                    onChange={e =>
                      setEditForm(prev => ({ ...prev, company_website: e.target.value }))
                    }
                    placeholder="https://example.com"
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="client-type">Client Type *</Label>
                  <Select
                    value={editForm.client_type || ''}
                    onValueChange={value =>
                      setEditForm(prev => ({ ...prev, client_type: value as any }))
                    }
                  >
                    <SelectTrigger id="client-type" className="mt-1">
                      <SelectValue placeholder="Select client type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tier_1">Tier 1 - Premium</SelectItem>
                      <SelectItem value="tier_2">Tier 2 - Standard</SelectItem>
                      <SelectItem value="tier_3">Tier 3 - Basic</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="market-sector">Market Sector</Label>
                  <Select
                    value={editForm.market_sector || 'none'}
                    onValueChange={value =>
                      setEditForm(prev => ({
                        ...prev,
                        market_sector: value === 'none' ? '' : value,
                      }))
                    }
                  >
                    <SelectTrigger id="market-sector" className="mt-1">
                      <SelectValue placeholder="Select market sector" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No sector selected</SelectItem>
                      <SelectItem value="Technology">Technology</SelectItem>
                      <SelectItem value="Healthcare">Healthcare</SelectItem>
                      <SelectItem value="Finance">Finance</SelectItem>
                      <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                      <SelectItem value="Retail">Retail</SelectItem>
                      <SelectItem value="Education">Education</SelectItem>
                      <SelectItem value="Transportation">Transportation</SelectItem>
                      <SelectItem value="Energy">Energy</SelectItem>
                      <SelectItem value="Real Estate">Real Estate</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle>Address Information</CardTitle>
              <CardDescription>Manage address information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Address Fields */}
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="address-line1">Address Line 1</Label>
                    <Input
                      id="address-line1"
                      value={editForm.client_address?.line1 || ''}
                      onChange={e =>
                        setEditForm(prev => ({
                          ...prev,
                          client_address: {
                            ...prev.client_address,
                            line1: e.target.value,
                          },
                        }))
                      }
                      placeholder="Enter address line 1"
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="address-line2">Address Line 2 (Optional)</Label>
                    <Input
                      id="address-line2"
                      value={editForm.client_address?.line2 || ''}
                      onChange={e =>
                        setEditForm(prev => ({
                          ...prev,
                          client_address: {
                            ...prev.client_address,
                            line1: prev.client_address?.line1 || '',
                            line2: e.target.value,
                          },
                        }))
                      }
                      placeholder="Enter address line 2 (optional)"
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="pincode">Pincode</Label>
                    <Input
                      id="pincode"
                      type="number"
                      value={editForm.client_address?.pincode || ''}
                      onChange={e =>
                        setEditForm(prev => ({
                          ...prev,
                          client_address: {
                            ...prev.client_address,
                            line1: prev.client_address?.line1 || '',
                            pincode: e.target.value ? parseInt(e.target.value) : undefined,
                          },
                        }))
                      }
                      placeholder="Enter pincode"
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contacts */}
          {account &&
            (account.primary_contact ||
              (account.secondary_contacts && account.secondary_contacts.length > 0)) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Users className="h-5 w-5 mr-2" />
                      Contacts (
                      {(account.primary_contact ? 1 : 0) +
                        (account.secondary_contacts?.length || 0)}
                      )
                    </div>
                    <Button variant="outline" size="sm" onClick={handleAddContact}>
                      <Plus className="h-4 w-4 mr-2" />
                      Add Contact
                    </Button>
                  </CardTitle>
                  <CardDescription>
                    View and manage all contacts associated with this account
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Primary Contact */}
                    {account.primary_contact && (
                      <div className="flex items-center justify-between p-4 border rounded-lg bg-blue-50 border-blue-200">
                        <div className="flex items-center space-x-4">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-blue-100 text-blue-600 text-sm font-medium">
                              {account.primary_contact.name
                                ?.split(' ')
                                ?.map((n: string) => n[0])
                                ?.join('')
                                ?.toUpperCase() || '?'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="font-medium text-gray-900">
                                {account.primary_contact.name}
                              </h4>
                              <Badge variant="default" className="text-xs bg-blue-600">
                                PRIMARY
                              </Badge>
                              {account.primary_contact.title && (
                                <Badge variant="secondary" className="text-xs">
                                  {account.primary_contact.title}
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                              <div className="flex items-center space-x-1">
                                <Mail className="h-3 w-3" />
                                <span>{account.primary_contact.email}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Phone className="h-3 w-3" />
                                <span>{account.primary_contact.phone}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditContact(account.primary_contact)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Secondary Contacts */}
                    {account.secondary_contacts?.map((contact, index) => (
                      <div
                        key={contact.contact_id || index}
                        className="flex items-center justify-between p-4 border rounded-lg bg-gray-50"
                      >
                        <div className="flex items-center space-x-4">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-gray-100 text-gray-600 text-sm font-medium">
                              {contact.name
                                ?.split(' ')
                                ?.map((n: string) => n[0])
                                ?.join('')
                                ?.toUpperCase() || '?'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="font-medium text-gray-900">{contact.name}</h4>
                              <Badge variant="outline" className="text-xs">
                                SECONDARY
                              </Badge>
                              {contact.title && (
                                <Badge variant="secondary" className="text-xs">
                                  {contact.title}
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                              <div className="flex items-center space-x-1">
                                <Mail className="h-3 w-3" />
                                <span>{contact.email}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <Phone className="h-3 w-3" />
                                <span>{contact.phone}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEditContact(contact)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              handlePromoteContactToPrimary(contact.contact_id, contact.name);
                            }}
                            disabled={isPromotingContact}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            title="Promote to Primary Contact"
                          >
                            {isPromotingContact ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            ) : (
                              <Award className="h-4 w-4" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700"
                            onClick={() => handleDeleteContact(contact.contact_id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

          {/* Notes */}
          <Card>
            <CardHeader>
              <CardTitle>Internal Notes</CardTitle>
              <CardDescription>
                Add any internal notes or observations about this account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={editForm.notes || ''}
                  onChange={e => setEditForm(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="Add any internal notes about this account..."
                  rows={5}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex items-center justify-end space-x-4 pt-6 border-t">
            <Button variant="outline" onClick={handleCancel} disabled={isUpdating}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleUpdateAccount} disabled={isUpdating || !editForm.client_name}>
              {isUpdating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Add Contact Modal */}
      <Dialog open={showAddContactModal} onOpenChange={setShowAddContactModal}>
        <DialogContent className="sm:max-w-[425px] bg-white">
          <DialogHeader>
            <DialogTitle>Add New Contact</DialogTitle>
            <DialogDescription>
              Add a new contact to this account. All fields marked with * are required.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="contact-name">Name *</Label>
              <Input
                id="contact-name"
                value={contactForm.name}
                onChange={e => setContactForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Contact full name"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="contact-email">Email *</Label>
              <Input
                id="contact-email"
                type="email"
                value={contactForm.email}
                onChange={e => setContactForm(prev => ({ ...prev, email: e.target.value }))}
                placeholder="contact@company.com"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="contact-phone">Phone *</Label>
              <Input
                id="contact-phone"
                value={contactForm.phone}
                onChange={e => setContactForm(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="+1-555-0123"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="contact-title">Job Title</Label>
              <Input
                id="contact-title"
                value={contactForm.title}
                onChange={e => setContactForm(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Manager, Director, etc."
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowAddContactModal(false)}
              disabled={isAddingContact}
            >
              Cancel
            </Button>
            <Button
              onClick={submitAddContact}
              disabled={
                isAddingContact ||
                !contactForm.name?.trim() ||
                !contactForm.email?.trim() ||
                !contactForm.phone?.trim()
              }
            >
              {isAddingContact ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Adding...
                </>
              ) : (
                'Add Contact'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Contact Modal */}
      <Dialog open={showEditContactModal} onOpenChange={setShowEditContactModal}>
        <DialogContent className="sm:max-w-[425px] bg-white">
          <DialogHeader>
            <DialogTitle>Edit Contact</DialogTitle>
            <DialogDescription>
              Update contact information. All fields marked with * are required.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="edit-contact-name">Name *</Label>
              <Input
                id="edit-contact-name"
                value={contactForm.name}
                onChange={e => setContactForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Contact full name"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="edit-contact-email">Email *</Label>
              <Input
                id="edit-contact-email"
                type="email"
                value={contactForm.email}
                onChange={e => setContactForm(prev => ({ ...prev, email: e.target.value }))}
                placeholder="contact@company.com"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="edit-contact-phone">Phone *</Label>
              <Input
                id="edit-contact-phone"
                value={contactForm.phone}
                onChange={e => setContactForm(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="+1-555-0123"
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="edit-contact-title">Job Title</Label>
              <Input
                id="edit-contact-title"
                value={contactForm.title}
                onChange={e => setContactForm(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Manager, Director, etc."
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowEditContactModal(false)}
              disabled={isUpdatingContact}
            >
              Cancel
            </Button>
            <Button
              onClick={submitEditContact}
              disabled={
                isUpdatingContact ||
                !contactForm.name?.trim() ||
                !contactForm.email?.trim() ||
                !contactForm.phone?.trim()
              }
            >
              {isUpdatingContact ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </>
              ) : (
                'Update Contact'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Contact Confirmation */}
      <AlertDialog open={showDeleteContactDialog} onOpenChange={setShowDeleteContactDialog}>
        <AlertDialogContent className="bg-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to delete this contact?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the contact and remove all
              associated information.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingContact}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteContact}
              disabled={isDeletingContact}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeletingContact ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Deleting...
                </>
              ) : (
                'Delete Contact'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AccountEdit;
