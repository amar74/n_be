import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import {
  Building2,
  CreditCard,
  FileText,
  Users,
  AlertCircle,
  Calendar,
  DollarSign,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface PurchaseRequestFormData {
  purchaseType: 'overhead' | 'project' | '';
  description: string;
  estimatedCost: string;
  vendor: string;
  justification: string;
  department: string;
  projectCode?: string;
  urgency: 'low' | 'medium' | 'high' | '';
  neededBy: string;
  category: string;
  requestedBy: string;
}

interface PurchaseRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PurchaseRequestFormData) => void;
}

export default function PurchaseRequestModal({
  isOpen,
  onClose,
  onSubmit,
}: PurchaseRequestModalProps) {
  const { toast } = useToast();
  const [formData, setFormData] = useState<PurchaseRequestFormData>({
    purchaseType: '',
    description: '',
    estimatedCost: '',
    vendor: '',
    justification: '',
    department: '',
    projectCode: '',
    urgency: '',
    neededBy: '',
    category: '',
    requestedBy: localStorage.getItem('userEmail') || 'user@example.com',
  });

  const [errors, setErrors] = useState<Partial<PurchaseRequestFormData>>({});

  const handleInputChange = (field: keyof PurchaseRequestFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<PurchaseRequestFormData> = {};

    if (!formData.purchaseType) {
      newErrors.purchaseType = 'project';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    if (!formData.estimatedCost || parseFloat(formData.estimatedCost) <= 0) {
      newErrors.estimatedCost = 'Valid estimated cost is required';
    }
    if (!formData.vendor.trim()) {
      newErrors.vendor = 'Vendor name is required';
    }
    if (!formData.justification.trim()) {
      newErrors.justification = 'Business justification is required';
    }
    if (!formData.department) {
      newErrors.department = 'Department is required';
    }
    if (formData.purchaseType === 'project' && !formData.projectCode) {
      newErrors.projectCode = 'Project code is required for project purchases';
    }
    if (!formData.urgency) {
      newErrors.urgency = 'medium';
    }
    if (!formData.neededBy) {
      newErrors.neededBy = 'Required date is needed';
    }
    if (!formData.category) {
      newErrors.category = 'Category is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(formData);
      toast({
        title: 'Purchase Request Submitted',
        description: 'Your purchase request has been submitted for approval.',
      });
      resetForm();
      onClose();
    }
  };

  const resetForm = () => {
    setFormData({
      purchaseType: '',
      description: '',
      estimatedCost: '',
      vendor: '',
      justification: '',
      department: '',
      projectCode: '',
      urgency: '',
      neededBy: '',
      category: '',
      requestedBy: localStorage.getItem('userEmail') || 'user@example.com',
    });
    setErrors({});
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <FileText className="h-6 w-6 text-purple-600" />
            <span>Create Purchase Request</span>
          </DialogTitle>
          <DialogDescription>
            Submit a formal request for company purchases requiring approval
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Purchase Type Selection */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Purchase Type</Label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => handleInputChange('purchaseType', 'overhead')}
                className={`p-4 border-2 rounded-lg text-left transition-all hover:border-blue-300 ${
                  formData.purchaseType === 'overhead'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Building2 className="h-6 w-6 text-blue-600" />
                  <div>
                    <h3 className="font-medium">Overhead Purchase</h3>
                    <p className="text-sm text-gray-600">
                      General business expenses, office supplies, utilities
                    </p>
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => handleInputChange('purchaseType', 'project')}
                className={`p-4 border-2 rounded-lg text-left transition-all hover:border-green-300 ${
                  formData.purchaseType === 'project'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Users className="h-6 w-6 text-green-600" />
                  <div>
                    <h3 className="font-medium">Project-Specific</h3>
                    <p className="text-sm text-gray-600">
                      Directly related to a specific client project
                    </p>
                  </div>
                </div>
              </button>
            </div>
            {errors.purchaseType && (
              <p className="text-sm text-red-600 flex items-center space-x-1">
                <AlertCircle className="h-4 w-4" />
                <span>{errors.purchaseType}</span>
              </p>
            )}
          </div>

          {/* Main Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="description">Purchase Description</Label>
                <Textarea
                  id="description"
                  placeholder="Detailed description of what you need to purchase..."
                  value={formData.description}
                  onChange={e => handleInputChange('description', e.target.value)}
                  className={errors.description ? 'border-red-500' : ''}
                />
                {errors.description && (
                  <p className="text-sm text-red-600 mt-1">{errors.description}</p>
                )}
              </div>

              <div>
                <Label htmlFor="vendor">Preferred Vendor</Label>
                <Input
                  id="vendor"
                  placeholder="Enter vendor name or 'TBD' if unknown"
                  value={formData.vendor}
                  onChange={e => handleInputChange('vendor', e.target.value)}
                  className={errors.vendor ? 'border-red-500' : ''}
                />
                {errors.vendor && <p className="text-sm text-red-600 mt-1">{errors.vendor}</p>}
              </div>

              <div>
                <Label htmlFor="estimatedCost">Estimated Cost ($)</Label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="estimatedCost"
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={formData.estimatedCost}
                    onChange={e => handleInputChange('estimatedCost', e.target.value)}
                    className={`pl-10 ${errors.estimatedCost ? 'border-red-500' : ''}`}
                  />
                </div>
                {errors.estimatedCost && (
                  <p className="text-sm text-red-600 mt-1">{errors.estimatedCost}</p>
                )}
              </div>

              <div>
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={value => handleInputChange('category', value)}
                >
                  <SelectTrigger className={errors.category ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select purchase category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="software">Software & Licenses</SelectItem>
                    <SelectItem value="hardware">Hardware & Equipment</SelectItem>
                    <SelectItem value="office-supplies">Office Supplies</SelectItem>
                    <SelectItem value="furniture">Furniture & Fixtures</SelectItem>
                    <SelectItem value="professional-services">Professional Services</SelectItem>
                    <SelectItem value="marketing">Marketing & Advertising</SelectItem>
                    <SelectItem value="travel">Travel & Transportation</SelectItem>
                    <SelectItem value="training">Training & Education</SelectItem>
                    <SelectItem value="maintenance">Maintenance & Repairs</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                {errors.category && <p className="text-sm text-red-600 mt-1">{errors.category}</p>}
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="department">Department</Label>
                <Select
                  value={formData.department}
                  onValueChange={value => handleInputChange('department', value)}
                >
                  <SelectTrigger className={errors.department ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select your department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="IT">Information Technology</SelectItem>
                    <SelectItem value="HR">Human Resources</SelectItem>
                    <SelectItem value="Finance">Finance</SelectItem>
                    <SelectItem value="Operations">Operations</SelectItem>
                    <SelectItem value="Engineering">Engineering</SelectItem>
                    <SelectItem value="Marketing">Marketing</SelectItem>
                    <SelectItem value="Sales">Sales</SelectItem>
                    <SelectItem value="Legal">Legal</SelectItem>
                    <SelectItem value="Facilities">Facilities</SelectItem>
                  </SelectContent>
                </Select>
                {errors.department && (
                  <p className="text-sm text-red-600 mt-1">{errors.department}</p>
                )}
              </div>

              {/* Project Code - Only show if project type selected */}
              {formData.purchaseType === 'project' && (
                <div>
                  <Label htmlFor="projectCode">Project Code</Label>
                  <Select
                    value={formData.projectCode}
                    onValueChange={value => handleInputChange('projectCode', value)}
                  >
                    <SelectTrigger className={errors.projectCode ? 'border-red-500' : ''}>
                      <SelectValue placeholder="Select project" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="PRJ-001">PRJ-001 - Metro Transit</SelectItem>
                      <SelectItem value="PRJ-002">PRJ-002 - Highway Infrastructure</SelectItem>
                      <SelectItem value="PRJ-003">PRJ-003 - Water Treatment</SelectItem>
                      <SelectItem value="PRJ-004">PRJ-004 - Smart City Initiative</SelectItem>
                      <SelectItem value="PRJ-005">PRJ-005 - Energy Grid Modernization</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.projectCode && (
                    <p className="text-sm text-red-600 mt-1">{errors.projectCode}</p>
                  )}
                </div>
              )}

              <div>
                <Label htmlFor="urgency">Urgency Level</Label>
                <Select
                  value={formData.urgency}
                  onValueChange={value => handleInputChange('urgency', value)}
                >
                  <SelectTrigger className={errors.urgency ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select urgency level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-800">Low</Badge>
                        <span>Standard processing (10-15 days)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="medium">
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>
                        <span>Expedited (5-7 days)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="high">
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-red-100 text-red-800">High</Badge>
                        <span>Urgent (1-3 days)</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                {errors.urgency && <p className="text-sm text-red-600 mt-1">{errors.urgency}</p>}
              </div>

              <div>
                <Label htmlFor="neededBy">Required By Date</Label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="neededBy"
                    type="date"
                    value={formData.neededBy}
                    onChange={e => handleInputChange('neededBy', e.target.value)}
                    className={`pl-10 ${errors.neededBy ? 'border-red-500' : ''}`}
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
                {errors.neededBy && <p className="text-sm text-red-600 mt-1">{errors.neededBy}</p>}
              </div>
            </div>
          </div>

          {/* Business Justification */}
          <div>
            <Label htmlFor="justification">Business Justification</Label>
            <Textarea
              id="justification"
              placeholder="Explain why this purchase is necessary for business operations..."
              value={formData.justification}
              onChange={e => handleInputChange('justification', e.target.value)}
              className={`min-h-24 ${errors.justification ? 'border-red-500' : ''}`}
            />
            {errors.justification && (
              <p className="text-sm text-red-600 mt-1">{errors.justification}</p>
            )}
          </div>

          {/* Purchase Type Summary */}
          {formData.purchaseType && (
            <div
              className={`p-4 rounded-lg border-2 ${
                formData.purchaseType === 'overhead'
                  ? 'border-blue-200 bg-blue-50'
                  : 'border-green-200 bg-green-50'
              }`}
            >
              <h4 className="font-medium mb-2">
                {formData.purchaseType === 'overhead' ? 'Overhead Purchase' : 'Project Purchase'}{' '}
                Summary
              </h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Billing:</span>
                  <span className="ml-2 font-medium">
                    {formData.purchaseType === 'overhead'
                      ? 'General company overhead'
                      : `Charged to project ${formData.projectCode || 'TBD'}`}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Approval Level:</span>
                  <span className="ml-2 font-medium">
                    {formData.purchaseType === 'overhead'
                      ? 'Department manager + Finance'
                      : 'Project manager + Department head'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} className="bg-purple-600 hover:bg-purple-700">
            Submit Request
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
