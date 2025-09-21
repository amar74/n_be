import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { useAccountContacts, useAccountDetail, useAccounts } from '@/hooks/useAccounts';
import {
  AccountDetailResponse,
  ContactFormData,
  contactFormSchema,
  ContactFormValues,
} from '@/types/accounts';
import {
  ArrowLeft,
  Building2,
  Globe,
  MapPin,
  Mail,
  Phone,
  User,
  Calendar,
  Edit,
  MoreHorizontal,
  Award,
  DollarSign,
  TrendingUp,
  Users,
  Activity,
  Trash2,
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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
import { Logo } from '@/components/ui/logo';

const AccountDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Use the new useAccounts hook
  const {
    deleteAccount,
    deleteContact,
    updateContact,
    promoteContactToPrimary,
    isDeleting,
    isDeletingContact,
    isUpdatingContact,
    isPromotingContact,
  } = useAccounts();

  // Use the account data from the hook
  const { accountDetail: account, isAccountDetailLoading: isLoading, accountDetailError: error } = useAccountDetail(id || '');
  const { accountContacts: contactsResponse } = useAccountContacts(id || '');

  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  // Contact management state
  const [showEditContactModal, setShowEditContactModal] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);

  // React Hook Form for contact editing with Zod validation
  const contactForm = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      name: '',
      email: '',
      phone: '',
      title: '',
    },
  });

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'e' && (event.metaKey || event.ctrlKey) && account?.account_id) {
        event.preventDefault();
        navigate(`/module/accounts/${account.account_id}/edit`);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [account?.account_id, navigate]);

  const handleDeleteAccount = async () => {
    if (!account?.account_id) return;

    try {
      await deleteAccount(account.account_id);

      toast({
        title: '✅ Account Deleted',
        description: 'Account has been permanently deleted.',
      });

      // Navigate back to accounts list
      navigate('/module/accounts');
    } catch (error: any) {
      console.error('Error deleting account:', error);
    } finally {
      setShowDeleteDialog(false);
    }
  };

  // Contact management handlers
  const handleEditContact = (contact: any) => {
    contactForm.reset({
      name: contact.name || '',
      email: contact.email || '',
      phone: contact.phone || '',
      title: contact.title || '',
    });
    setSelectedContactId(contact.contact_id);
    setShowEditContactModal(true);
  };

  const submitEditContact = async (values: ContactFormValues) => {
    // Validation is already handled by Zod schema
    if (!account?.account_id || !selectedContactId) {
      toast({
        title: 'Error',
        description: 'Account or contact not found.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await updateContact({
        accountId: account.account_id,
        contactId: selectedContactId,
        contact: {
          name: values.name.trim(),
          email: values.email.trim(),
          phone: values.phone.trim(),
          title: values.title?.trim() || undefined,
        },
      });

      toast({
        title: '✅ Contact Updated',
        description: 'Contact has been updated successfully.',
      });

      setShowEditContactModal(false);
      contactForm.reset();
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

  if (isLoading || (!account && !error)) {
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

  // Only show error if there's actually an error and we're not loading
  if (error && !isLoading) {
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

  // If no account data and no error, it's still loading
  if (!account) {
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
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {account?.client_name || 'Loading...'}
              </h1>
              <p className="text-sm text-gray-500">Account Details</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Link to={`/module/accounts/${account.account_id}/edit`}>
              <Button variant="outline" size="sm">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            </Link>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <Activity className="h-4 w-4 mr-2" />
                  View Activity
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Users className="h-4 w-4 mr-2" />
                  Manage Contacts
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="text-red-600"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  Delete Account
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Account Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Account Overview Card */}
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <Avatar className="h-16 w-16">
                      <AvatarFallback className="bg-blue-100 text-blue-600 text-xl font-semibold">
                        {account?.client_name?.charAt(0) || '?'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-2xl">
                        {account?.client_name || 'Loading...'}
                      </CardTitle>
                      <CardDescription className="flex items-center mt-2">
                        <Badge className={`mr-3 ${getClientTypeColor(account.client_type)}`}>
                          <Award className="h-3 w-3 mr-1" />
                          {getClientTypeLabel(account.client_type)}
                        </Badge>
                        {account.market_sector && (
                          <span className="text-sm text-gray-600">{account.market_sector}</span>
                        )}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {account.company_website && (
                    <div className="flex items-center space-x-3">
                      <Globe className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Website</p>
                        <a
                          href={account.company_website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline text-sm"
                        >
                          {account.company_website}
                        </a>
                      </div>
                    </div>
                  )}
                  {account.client_address && (
                    <div className="flex items-center space-x-3">
                      <MapPin className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Address</p>
                        <div className="text-sm text-gray-600">
                          {typeof account.client_address === 'string' ? (
                            <p>{account.client_address}</p>
                          ) : (
                            <div>
                              <p>{account.client_address.line1}</p>
                              {account.client_address.line2 && (
                                <p>{account.client_address.line2}</p>
                              )}
                              {account.client_address.pincode && (
                                <p>Pincode: {account.client_address.pincode}</p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  {/* Primary contact is now shown in the dedicated Contacts Card below per API.md */}
                  {/* Contact email is shown in primary contact section per API.md */}
                </div>
              </CardContent>
            </Card>

            {/* Contacts Card - Updated to show primary and secondary contacts per API.md */}
            {(account.primary_contact || contactsResponse?.contacts) &&
              (account.primary_contact ||
                (contactsResponse?.contacts && contactsResponse.contacts.length > 0)) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Users className="h-5 w-5 mr-2" />
                      Contacts
                      {contactsResponse?.contacts && (
                        <Badge variant="secondary" className="ml-2">
                          {(account.primary_contact ? 1 : 0) +
                            (contactsResponse.contacts.length || 0)}
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Primary Contact - Cannot be deleted, can be updated */}
                      {account.primary_contact && (
                        <div className="flex items-center space-x-4 p-4 border rounded-lg bg-blue-50 border-blue-200">
                          <Avatar>
                            <AvatarFallback className="bg-blue-100 text-blue-600 text-sm font-medium">
                              {account.primary_contact.name
                                ?.split(' ')
                                .map(n => n[0])
                                .join('') || 'PC'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="font-medium text-gray-900">
                                {account.primary_contact.name || 'Primary Contact'}
                              </h4>
                              <Badge className="text-xs bg-blue-100 text-blue-800 border-blue-300">
                                PRIMARY
                              </Badge>
                              {account.primary_contact.title && (
                                <Badge variant="secondary" className="text-xs">
                                  {account.primary_contact.title}
                                </Badge>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                              {account.primary_contact.email && (
                                <div className="flex items-center space-x-1">
                                  <Mail className="h-3 w-3" />
                                  <a
                                    href={`mailto:${account.primary_contact.email}`}
                                    className="hover:underline"
                                  >
                                    {account.primary_contact.email}
                                  </a>
                                </div>
                              )}
                              {account.primary_contact.phone && (
                                <div className="flex items-center space-x-1">
                                  <Phone className="h-3 w-3" />
                                  <a
                                    href={`tel:${account.primary_contact.phone}`}
                                    className="hover:underline"
                                  >
                                    {account.primary_contact.phone}
                                  </a>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                if (account.primary_contact) {
                                  handleEditContact(account.primary_contact);
                                }
                              }}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            {/* Primary contact cannot be deleted */}
                          </div>
                        </div>
                      )}

                      {/* Secondary Contacts - Can be updated and deleted */}
                      {contactsResponse?.contacts &&
                        contactsResponse.contacts.length > 0 &&
                        contactsResponse.contacts
                          .filter(
                            contact =>
                              // Filter out the primary contact from secondary contacts list
                              !account.primary_contact ||
                              contact.contact_id !== account.primary_contact.contact_id
                          )
                          .map((contact, index) => (
                            <div
                              key={contact.contact_id || index}
                              className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50"
                            >
                              <Avatar>
                                <AvatarFallback className="bg-gray-100 text-gray-600 text-sm font-medium">
                                  {contact.name
                                    ?.split(' ')
                                    .map(n => n[0])
                                    .join('') || 'SC'}
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
                                    <a href={`mailto:${contact.email}`} className="hover:underline">
                                      {contact.email}
                                    </a>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Phone className="h-3 w-3" />
                                    <a href={`tel:${contact.phone}`} className="hover:underline">
                                      {contact.phone}
                                    </a>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    handleEditContact(contact);
                                  }}
                                >
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
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
                                  variant="outline"
                                  size="sm"
                                  onClick={async () => {
                                    // Ensure we're not trying to delete the primary contact
                                    if (
                                      account.primary_contact &&
                                      contact.contact_id === account.primary_contact.contact_id
                                    ) {
                                      toast({
                                        title: 'Error',
                                        description:
                                          'Cannot delete the primary contact. Please assign a new primary contact first.',
                                        variant: 'destructive',
                                      });
                                      return;
                                    }

                                    if (
                                      confirm(
                                        `Are you sure you want to delete contact "${contact.name}"?`
                                      )
                                    ) {
                                      try {
                                        await deleteContact({
                                          accountId: id!,
                                          contactId: contact.contact_id,
                                        });

                                        toast({
                                          title: '✅ Contact Deleted',
                                          description:
                                            'Secondary contact has been deleted successfully.',
                                        });
                                      } catch (error: any) {
                                        console.error('Failed to delete contact:', error);
                                        toast({
                                          title: 'Error',
                                          description:
                                            error.response?.data?.detail?.message ||
                                            'Failed to delete contact. Please try again.',
                                          variant: 'destructive',
                                        });
                                      }
                                    }
                                  }}
                                  disabled={isDeletingContact}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                    </div>
                  </CardContent>
                </Card>
              )}

            {/* Notes Card */}
            {account.notes && (
              <Card>
                <CardHeader>
                  <CardTitle>Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 whitespace-pre-wrap">{account.notes}</p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Account Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Account Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {account.total_value !== null && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">Total Value</span>
                    </div>
                    <span className="text-lg font-semibold text-green-600">
                      ${account.total_value?.toLocaleString() || '0'}
                    </span>
                  </div>
                )}
                {account.opportunities !== null && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium">Opportunities</span>
                    </div>
                    <span className="text-lg font-semibold text-blue-600">
                      {account.opportunities || '0'}
                    </span>
                  </div>
                )}
                {account.last_contact && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-purple-600" />
                      <span className="text-sm font-medium">Last Contact</span>
                    </div>
                    <span className="text-sm text-gray-600">
                      {new Date(account.last_contact).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Account Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Account Timeline</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {account.created_at && (
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Account Created</p>
                      <p className="text-xs text-gray-600">
                        {new Date(account.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
                {account.updated_at && account.updated_at !== account.created_at && (
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Last Updated</p>
                      <p className="text-xs text-gray-600">
                        {new Date(account.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to delete this account?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the account "
              {account?.client_name}" and remove all associated data from our servers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteAccount}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Deleting...
                </>
              ) : (
                'Delete Account'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Contact Edit Modal */}
      <Dialog open={showEditContactModal} onOpenChange={setShowEditContactModal}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Contact</DialogTitle>
            <DialogDescription>
              Update the contact information. All fields are required.
            </DialogDescription>
          </DialogHeader>
          <Form {...contactForm}>
            <form onSubmit={contactForm.handleSubmit(submitEditContact)} className="space-y-4">
              <FormField
                control={contactForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="Contact full name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={contactForm.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email *</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="contact@example.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={contactForm.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone *</FormLabel>
                    <FormControl>
                      <Input placeholder="+1 (555) 123-4567" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={contactForm.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Job title (optional)" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowEditContactModal(false);
                    contactForm.reset();
                  }}
                  disabled={isUpdatingContact}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isUpdatingContact}>
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
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AccountDetails;
