import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Palette,
  FileText,
  Target,
  Layout,
  Eye,
  Settings,
  CheckCircle,
  Download,
  Brain,
  Upload,
  Image as ImageIcon,
  Trash2,
  Wand2,
  Crop,
  Filter,
  Contrast,
  Sun,
  Zap,
  Sparkles,
  RotateCw,
  Scissors,
  Palette as PaletteIcon,
  Move3D,
  Lightbulb,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DesignOption {
  id: string;
  name: string;
  preview: string;
  colors: string[];
  description: string;
}

interface SectionDetail {
  name: string;
  required: boolean;
  pageLimit?: number;
  includeGraphics: boolean;
  includeInfographics: boolean;
  includeMatrixes: boolean;
  includeImages: boolean;
  includeTables: boolean;
  includeCharts: boolean;
  includeFlowcharts: boolean;
  selectedPages: number;
}

interface UploadedImage {
  id: string;
  name: string;
  url: string;
  size: number;
  type: string;
  purpose: 'cover' | 'background' | 'content' | 'logo';
  enhancementSettings: {
    brightness: number;
    contrast: number;
    saturation: number;
    blur: number;
    rotation: number;
    crop: { x: number; y: number; width: number; height: number } | null;
    filter: string;
    aiEnhanced: boolean;
  };
}

export default function PlanTab() {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedTheme, setSelectedTheme] = useState<string>("");
  const [selectedCover, setSelectedCover] = useState<string>("");
  const [selectedTabs, setSelectedTabs] = useState<string>("");
  const [totalPages, setTotalPages] = useState(50);
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [selectedImageForEdit, setSelectedImageForEdit] = useState<UploadedImage | null>(null);
  const [isEnhancementDialogOpen, setIsEnhancementDialogOpen] = useState(false);
  const [isUploadingImages, setIsUploadingImages] = useState(false);
  const [isAIDesignDialogOpen, setIsAIDesignDialogOpen] = useState(false);
  const [isGeneratingDesigns, setIsGeneratingDesigns] = useState(false);
  const [selectedAIDesign, setSelectedAIDesign] = useState<string | null>(null);
  const [customDesignInput, setCustomDesignInput] = useState("");
  const [sectionDetails, setSectionDetails] = useState<SectionDetail[]>([
    {
      name: "Contents",
      required: true,
      pageLimit: 1,
      includeGraphics: false,
      includeInfographics: false,
      includeMatrixes: false,
      includeImages: false,
      includeTables: false,
      includeCharts: false,
      includeFlowcharts: false,
      selectedPages: 1,
    },
    {
      name: "Letter",
      required: true,
      pageLimit: 2,
      includeGraphics: true,
      includeInfographics: false,
      includeMatrixes: false,
      includeImages: true,
      includeTables: false,
      includeCharts: false,
      includeFlowcharts: false,
      selectedPages: 2,
    },
    {
      name: "Executive Summary",
      required: true,
      pageLimit: 4,
      includeGraphics: true,
      includeInfographics: true,
      includeMatrixes: false,
      includeImages: true,
      includeTables: false,
      includeCharts: true,
      includeFlowcharts: false,
      selectedPages: 3,
    },
    {
      name: "Qualifications",
      required: true,
      pageLimit: 8,
      includeGraphics: true,
      includeInfographics: true,
      includeMatrixes: true,
      includeImages: true,
      includeTables: true,
      includeCharts: false,
      includeFlowcharts: false,
      selectedPages: 6,
    },
    {
      name: "Technical Approach",
      required: true,
      pageLimit: 12,
      includeGraphics: true,
      includeInfographics: true,
      includeMatrixes: false,
      includeImages: true,
      includeTables: true,
      includeCharts: true,
      includeFlowcharts: true,
      selectedPages: 10,
    },
  ]);

  const designThemes: DesignOption[] = [
    {
      id: "modern-blue",
      name: "Modern Blue",
      preview: "🔵",
      colors: ["#2563eb", "#1d4ed8", "#1e40af"],
      description: "Clean, professional design with blue accents",
    },
    {
      id: "corporate-gray",
      name: "Corporate Gray",
      preview: "⚫",
      colors: ["#374151", "#4b5563", "#6b7280"],
      description: "Traditional corporate styling with gray tones",
    },
    {
      id: "vibrant-green",
      name: "Vibrant Green",
      preview: "🟢",
      colors: ["#059669", "#047857", "#065f46"],
      description: "Fresh, environmental-focused green theme",
    },
    {
      id: "elegant-purple",
      name: "Elegant Purple",
      preview: "🟣",
      colors: ["#7c3aed", "#6d28d9", "#5b21b6"],
      description: "Sophisticated purple with premium feel",
    },
  ];

  const handleSectionChange = (
    index: number,
    field: keyof SectionDetail,
    value: any,
  ) => {
    const updatedSections = [...sectionDetails];
    updatedSections[index] = { ...updatedSections[index], [field]: value };
    setSectionDetails(updatedSections);
  };

  const handleGenerateStrategy = () => {
    toast({
      title: "Generating Pursuit Strategy",
      description:
        "AI is analyzing uploaded documents to create your pursuit strategy.",
    });
  };

  const handleGenerateManagementPlan = () => {
    toast({
      title: "Generating Management Plan",
      description:
        "Creating proposal management plan based on RFP requirements.",
    });
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setIsUploadingImages(true);
    
    Array.from(files).forEach((file) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const newImage: UploadedImage = {
            id: `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name: file.name,
            url: e.target?.result as string,
            size: file.size,
            type: file.type,
            purpose: 'content',
            enhancementSettings: {
              brightness: 0,
              contrast: 0,
              saturation: 0,
              blur: 0,
              rotation: 0,
              crop: null,
              filter: 'none',
              aiEnhanced: false,
            },
          };
          
          setUploadedImages(prev => [...prev, newImage]);
        };
        reader.readAsDataURL(file);
      }
    });
    
    setTimeout(() => {
      setIsUploadingImages(false);
      toast({
        title: "Images Uploaded",
        description: `Successfully uploaded ${files.length} image(s) for proposal design.`,
      });
    }, 1500);
  };

  const handleDeleteImage = (imageId: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== imageId));
    toast({
      title: "Image Removed",
      description: "Image has been removed from the proposal design.",
    });
  };

  const handleImagePurposeChange = (imageId: string, purpose: UploadedImage['purpose']) => {
    setUploadedImages(prev => 
      prev.map(img => 
        img.id === imageId ? { ...img, purpose } : img
      )
    );
  };

  const handleEnhancementChange = (setting: keyof UploadedImage['enhancementSettings'], value: any) => {
    if (selectedImageForEdit) {
      const updatedImage = {
        ...selectedImageForEdit,
        enhancementSettings: {
          ...selectedImageForEdit.enhancementSettings,
          [setting]: value,
        },
      };
      
      setSelectedImageForEdit(updatedImage);
      setUploadedImages(prev => 
        prev.map(img => 
          img.id === updatedImage.id ? updatedImage : img
        )
      );
    }
  };

  const handleAIEnhancement = () => {
    if (selectedImageForEdit) {
      toast({
        title: "AI Enhancement Started",
        description: "AI is analyzing and enhancing your image...",
      });
      
      // Simulate AI enhancement
      setTimeout(() => {
        handleEnhancementChange('aiEnhanced', true);
        handleEnhancementChange('brightness', 10);
        handleEnhancementChange('contrast', 15);
        handleEnhancementChange('saturation', 5);
        
        toast({
          title: "AI Enhancement Complete",
          description: "Your image has been automatically enhanced for optimal proposal presentation.",
        });
      }, 2000);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // AI Generated Design Options
  const [aiDesignOptions, setAiDesignOptions] = useState([
    {
      id: 'ai-design-1',
      name: 'Professional Executive',
      category: 'Corporate',
      coverStyle: 'Clean geometric layout with bold typography',
      tabStyle: 'Minimalist tabs with subtle gradients',
      colorScheme: ['#1a365d', '#2d3748', '#4a5568'],
      preview: '📊',
      description: 'Professional design focused on data visualization and executive summary presentation',
      features: ['Clean typography', 'Data-focused layouts', 'Professional color palette', 'Geometric elements']
    },
    {
      id: 'ai-design-2',
      name: 'Modern Infrastructure',
      category: 'Technical',
      coverStyle: 'Blueprint-inspired design with technical elements',
      tabStyle: 'Industrial tabs with construction theme',
      colorScheme: ['#2b6cb0', '#2c5282', '#2a69ac'],
      preview: '🏗️',
      description: 'Engineering-focused design perfect for infrastructure and construction proposals',
      features: ['Blueprint aesthetics', 'Technical diagrams', 'Engineering typography', 'Industrial color scheme']
    },
    {
      id: 'ai-design-3',
      name: 'Environmental Innovation',
      category: 'Sustainability',
      coverStyle: 'Nature-inspired with organic flowing elements',
      tabStyle: 'Green-themed tabs with sustainability icons',
      colorScheme: ['#22543d', '#2f855a', '#38a169'],
      preview: '🌱',
      description: 'Eco-friendly design emphasizing sustainability and environmental responsibility',
      features: ['Organic shapes', 'Sustainability focus', 'Nature-inspired palette', 'Environmental icons']
    }
  ]);

  const handleGenerateMoreDesigns = () => {
    setIsGeneratingDesigns(true);

    // Generate designs based on user input or defaults
    const generateCustomDesigns = () => {
      if (customDesignInput.trim()) {
        // AI-generated designs based on user input
        const inputLower = customDesignInput.toLowerCase();
        const designVariations = [];

        // Analyze input for keywords and generate accordingly
        if (inputLower.includes('modern') || inputLower.includes('sleek') || inputLower.includes('minimalist')) {
          designVariations.push({
            id: `ai-design-${Date.now()}-modern`,
            name: 'Modern Custom',
            category: 'Custom',
            coverStyle: `Modern ${inputLower.includes('bold') ? 'bold' : 'clean'} design with custom elements`,
            tabStyle: 'Sleek modern tabs with refined typography',
            colorScheme: ['#1a202c', '#2d3748', '#4a5568'],
            preview: '✨',
            description: `Custom modern design based on your requirements: "${customDesignInput.substring(0, 60)}${customDesignInput.length > 60 ? '...' : ''}"`,
            features: ['Modern aesthetics', 'Custom styling', 'User-specified elements', 'Contemporary design']
          });
        }

        if (inputLower.includes('colorful') || inputLower.includes('vibrant') || inputLower.includes('bright')) {
          designVariations.push({
            id: `ai-design-${Date.now()}-vibrant`,
            name: 'Vibrant Custom',
            category: 'Custom',
            coverStyle: 'Colorful design with vibrant elements and dynamic layout',
            tabStyle: 'Bright tabs with energetic color scheme',
            colorScheme: ['#e53e3e', '#dd6b20', '#d69e2e'],
            preview: '🎨',
            description: `Vibrant design tailored to: "${customDesignInput.substring(0, 60)}${customDesignInput.length > 60 ? '...' : ''}"`,
            features: ['Vibrant colors', 'Dynamic elements', 'Custom requirements', 'Energetic design']
          });
        }

        if (inputLower.includes('professional') || inputLower.includes('corporate') || inputLower.includes('business')) {
          designVariations.push({
            id: `ai-design-${Date.now()}-professional`,
            name: 'Professional Custom',
            category: 'Custom',
            coverStyle: 'Professional corporate design with sophisticated elements',
            tabStyle: 'Executive-level tabs with premium styling',
            colorScheme: ['#2c5282', '#2a69ac', '#3182ce'],
            preview: '💼',
            description: `Professional design crafted for: "${customDesignInput.substring(0, 60)}${customDesignInput.length > 60 ? '...' : ''}"`,
            features: ['Corporate styling', 'Professional layout', 'Custom elements', 'Executive appeal']
          });
        }

        // If no specific keywords, create a general custom design
        if (designVariations.length === 0) {
          designVariations.push({
            id: `ai-design-${Date.now()}-custom`,
            name: 'Custom AI Design',
            category: 'Custom',
            coverStyle: 'Tailored design based on your specific requirements',
            tabStyle: 'Custom tabs designed to match your vision',
            colorScheme: ['#553c9a', '#6b46c1', '#7c3aed'],
            preview: '🎯',
            description: `AI-generated design based on: "${customDesignInput.substring(0, 60)}${customDesignInput.length > 60 ? '...' : ''}"`,
            features: ['Custom tailored', 'AI-generated', 'User requirements', 'Personalized design']
          });
        }

        return designVariations;
      } else {
        // Default designs when no input provided
        return [
          {
            id: `ai-design-${Date.now()}-1`,
            name: 'Innovation Tech',
            category: 'Technology',
            coverStyle: 'Futuristic design with digital elements',
            tabStyle: 'Tech-inspired tabs with neon accents',
            colorScheme: ['#553c9a', '#6b46c1', '#7c3aed'],
            preview: '💻',
            description: 'Technology-focused design for digital transformation and smart city proposals',
            features: ['Digital aesthetics', 'Tech elements', 'Future-forward design', 'Smart city theme']
          },
          {
            id: `ai-design-${Date.now()}-2`,
            name: 'Healthcare Excellence',
            category: 'Healthcare',
            coverStyle: 'Medical-inspired clean design with health icons',
            tabStyle: 'Healthcare tabs with medical color scheme',
            colorScheme: ['#c53030', '#e53e3e', '#f56565'],
            preview: '🏥',
            description: 'Healthcare-focused design for medical facility and wellness proposals',
            features: ['Medical aesthetics', 'Health icons', 'Clean design', 'Trust-building elements']
          },
          {
            id: `ai-design-${Date.now()}-3`,
            name: 'Transportation Hub',
            category: 'Transportation',
            coverStyle: 'Transit-inspired with movement and flow',
            tabStyle: 'Transportation tabs with route-like design',
            colorScheme: ['#2a69ac', '#3182ce', '#4299e1'],
            preview: '🚇',
            description: 'Transportation-focused design for transit and mobility proposals',
            features: ['Movement elements', 'Transit aesthetics', 'Flow design', 'Mobility icons']
          }
        ];
      }
    };

    setTimeout(() => {
      const newDesigns = generateCustomDesigns();
      setAiDesignOptions(prev => [...prev, ...newDesigns]);
      setIsGeneratingDesigns(false);

      toast({
        title: "New Designs Generated",
        description: customDesignInput.trim()
          ? "AI has generated custom design options based on your requirements."
          : "3 additional AI-generated design options have been created based on your proposal context.",
      });
    }, 2500);
  };

  const handleSelectAIDesign = (designId: string) => {
    setSelectedAIDesign(designId);
    const selectedDesign = aiDesignOptions.find(d => d.id === designId);
    if (selectedDesign) {
      // Apply the selected design theme
      setSelectedTheme(selectedDesign.category.toLowerCase());
      toast({
        title: "Design Applied",
        description: `"${selectedDesign.name}" design has been applied to your proposal.`,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* AI-Generated Mind Map and Plans */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="border-2 hover:border-blue-500 transition-colors cursor-pointer">
          <CardHeader className="text-center">
            <div className="mx-auto bg-blue-100 p-3 rounded-lg w-fit mb-3">
              <Brain className="h-8 w-8 text-blue-600" />
            </div>
            <CardTitle className="text-lg">Summarized RFP Mind Map</CardTitle>
            <CardDescription>
              AI-generated mind map from uploaded RFP documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">
              <Eye className="h-4 w-4 mr-2" />
              View Mind Map
            </Button>
          </CardContent>
        </Card>

        <Card className="border-2 hover:border-green-500 transition-colors cursor-pointer">
          <CardHeader className="text-center">
            <div className="mx-auto bg-green-100 p-3 rounded-lg w-fit mb-3">
              <FileText className="h-8 w-8 text-green-600" />
            </div>
            <CardTitle className="text-lg">Proposal Management Plan</CardTitle>
            <CardDescription>
              Generated from RFP requirements and deadlines
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              className="w-full"
              onClick={handleGenerateManagementPlan}
            >
              <Download className="h-4 w-4 mr-2" />
              Generate Plan
            </Button>
          </CardContent>
        </Card>

        <Card className="border-2 hover:border-purple-500 transition-colors cursor-pointer">
          <CardHeader className="text-center">
            <div className="mx-auto bg-purple-100 p-3 rounded-lg w-fit mb-3">
              <Target className="h-8 w-8 text-purple-600" />
            </div>
            <CardTitle className="text-lg">Pursuit Strategy</CardTitle>
            <CardDescription>
              Win strategy based on client analysis and competition
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              className="w-full"
              onClick={handleGenerateStrategy}
            >
              <Target className="h-4 w-4 mr-2" />
              Generate Strategy
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Proposal Design Section */}
      <Card className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Palette className="h-5 w-5 text-blue-600" />
                <span>Proposal Design</span>
              </CardTitle>
              <CardDescription>
                Select design elements for your proposal theme and layout
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAIDesignDialogOpen(true)}
              className="flex items-center gap-2 text-purple-700 border-purple-300 hover:bg-purple-50"
            >
              <Brain className="h-4 w-4" />
              AI generated design options
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Theme Selection */}
          <div>
            <Label className="text-base font-medium mb-3 block">
              Proposal Theme
            </Label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {designThemes.map((theme) => (
                <Card
                  key={theme.id}
                  className={`cursor-pointer border-2 transition-colors ${
                    selectedTheme === theme.id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedTheme(theme.id)}
                >
                  <CardContent className="p-4 text-center">
                    <div className="text-4xl mb-2">{theme.preview}</div>
                    <h4 className="font-medium mb-1">{theme.name}</h4>
                    <p className="text-xs text-gray-600">{theme.description}</p>
                    <div className="flex justify-center space-x-1 mt-2">
                      {theme.colors.map((color, index) => (
                        <div
                          key={index}
                          className="w-3 h-3 rounded-full border"
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Cover Page Options */}
          <div>
            <Label className="text-base font-medium mb-3 block">
              Cover Page Layout
            </Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {["Classic", "Modern", "Minimalist"].map((style) => (
                <Card
                  key={style}
                  className={`cursor-pointer border-2 transition-colors ${
                    selectedCover === style
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedCover(style)}
                >
                  <CardContent className="p-4 text-center">
                    <Layout className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                    <h4 className="font-medium">{style}</h4>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Tab Configuration */}
          <div>
            <Label className="text-base font-medium mb-3 block">
              Proposal Tabs
            </Label>
            <div className="space-y-3">
              <Input
                placeholder="Number of tabs (e.g., 5)"
                value="5"
                onChange={() => {}}
              />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {["Standard", "Colored", "Minimalist"].map((style) => (
                  <Card
                    key={style}
                    className={`cursor-pointer border-2 transition-colors ${
                      selectedTabs === style
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                    onClick={() => setSelectedTabs(style)}
                  >
                    <CardContent className="p-4 text-center">
                      <h4 className="font-medium">{style} Tabs</h4>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          {/* Image Upload and Management */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-base font-medium">
                Design Images & Assets
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div>
                      <Badge variant="outline" className="bg-purple-100 text-purple-700">
                        <Sparkles className="h-3 w-3 mr-1" />
                        AI Enhanced
                      </Badge>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>AI-powered image enhancement available</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            
            {/* Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center mb-4 hover:border-gray-400 transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              
              {isUploadingImages ? (
                <div className="space-y-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-sm text-gray-600">Uploading images...</p>
                  <Progress value={75} className="w-32 mx-auto" />
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="h-8 w-8 text-gray-400 mx-auto" />
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      Upload images for your proposal design
                    </p>
                    <p className="text-xs text-gray-500">
                      Supports JPG, PNG, GIF up to 10MB each
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    className="mt-2"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Choose Images
                  </Button>
                </div>
              )}
            </div>

            {/* Uploaded Images Grid */}
            {uploadedImages.length > 0 && (
              <div className="space-y-4">
                <h4 className="font-medium text-sm">Uploaded Images ({uploadedImages.length})</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {uploadedImages.map((image) => (
                    <Card key={image.id} className="border border-gray-200 hover:border-gray-300 transition-colors">
                      <CardContent className="p-3">
                        <div className="relative mb-3">
                          <img
                            src={image.url}
                            alt={image.name}
                            className="w-full h-24 object-cover rounded"
                            style={{
                              filter: `brightness(${100 + image.enhancementSettings.brightness}%) contrast(${100 + image.enhancementSettings.contrast}%) saturate(${100 + image.enhancementSettings.saturation}%) blur(${image.enhancementSettings.blur}px)`,
                              transform: `rotate(${image.enhancementSettings.rotation}deg)`,
                            }}
                          />
                          {image.enhancementSettings.aiEnhanced && (
                            <div className="absolute top-1 right-1">
                              <Badge variant="outline" className="bg-purple-100 text-purple-700 text-xs">
                                <Sparkles className="h-2 w-2 mr-1" />
                                AI
                              </Badge>
                            </div>
                          )}
                          <Button
                            variant="destructive"
                            size="sm"
                            className="absolute top-1 left-1 h-6 w-6 p-0"
                            onClick={() => handleDeleteImage(image.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                        
                        <div className="space-y-2">
                          <p className="text-xs font-medium truncate">{image.name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(image.size)}</p>
                          
                          <Select
                            value={image.purpose}
                            onValueChange={(value) => handleImagePurposeChange(image.id, value as UploadedImage['purpose'])}
                          >
                            <SelectTrigger className="h-7 text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="cover">Cover Image</SelectItem>
                              <SelectItem value="background">Background</SelectItem>
                              <SelectItem value="content">Content Image</SelectItem>
                              <SelectItem value="logo">Logo/Branding</SelectItem>
                            </SelectContent>
                          </Select>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            className="w-full h-7 text-xs"
                            onClick={() => {
                              setSelectedImageForEdit(image);
                              setIsEnhancementDialogOpen(true);
                            }}
                          >
                            <Wand2 className="h-3 w-3 mr-1" />
                            Enhance
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Image Enhancement Dialog */}
      <Dialog open={isEnhancementDialogOpen} onOpenChange={setIsEnhancementDialogOpen}>
        <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Wand2 className="h-5 w-5 text-purple-600" />
              Image Enhancement Studio
            </DialogTitle>
            <DialogDescription>
              Enhance your image with AI-powered tools and manual adjustments
            </DialogDescription>
          </DialogHeader>
          
          {selectedImageForEdit && (
            <div className="space-y-6">
              {/* Image Preview */}
              <div className="text-center">
                <div className="relative inline-block">
                  <img
                    src={selectedImageForEdit.url}
                    alt={selectedImageForEdit.name}
                    className="max-w-full h-48 object-contain rounded border"
                    style={{
                      filter: `brightness(${100 + selectedImageForEdit.enhancementSettings.brightness}%) contrast(${100 + selectedImageForEdit.enhancementSettings.contrast}%) saturate(${100 + selectedImageForEdit.enhancementSettings.saturation}%) blur(${selectedImageForEdit.enhancementSettings.blur}px)`,
                      transform: `rotate(${selectedImageForEdit.enhancementSettings.rotation}deg)`,
                    }}
                  />
                  {selectedImageForEdit.enhancementSettings.aiEnhanced && (
                    <Badge className="absolute top-2 right-2 bg-purple-100 text-purple-700">
                      <Sparkles className="h-3 w-3 mr-1" />
                      AI Enhanced
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-2">{selectedImageForEdit.name}</p>
              </div>

              {/* AI Quick Enhancement */}
              <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="bg-purple-100 p-2 rounded-lg">
                        <Sparkles className="h-5 w-5 text-purple-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-purple-900">AI Auto-Enhancement</h4>
                        <p className="text-sm text-purple-700">Let AI optimize your image automatically</p>
                      </div>
                    </div>
                    <Button
                      onClick={handleAIEnhancement}
                      className="bg-purple-600 hover:bg-purple-700"
                      disabled={selectedImageForEdit.enhancementSettings.aiEnhanced}
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      {selectedImageForEdit.enhancementSettings.aiEnhanced ? 'Enhanced' : 'Enhance'}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Manual Enhancement Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Lighting & Color */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Sun className="h-4 w-4 text-yellow-600" />
                      Lighting & Color
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-xs font-medium">Brightness ({selectedImageForEdit.enhancementSettings.brightness}%)</Label>
                      <Input
                        type="range"
                        min="-50"
                        max="50"
                        value={selectedImageForEdit.enhancementSettings.brightness}
                        onChange={(e) => handleEnhancementChange('brightness', Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <Label className="text-xs font-medium">Contrast ({selectedImageForEdit.enhancementSettings.contrast}%)</Label>
                      <Input
                        type="range"
                        min="-50"
                        max="50"
                        value={selectedImageForEdit.enhancementSettings.contrast}
                        onChange={(e) => handleEnhancementChange('contrast', Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <Label className="text-xs font-medium">Saturation ({selectedImageForEdit.enhancementSettings.saturation}%)</Label>
                      <Input
                        type="range"
                        min="-50"
                        max="50"
                        value={selectedImageForEdit.enhancementSettings.saturation}
                        onChange={(e) => handleEnhancementChange('saturation', Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Effects & Transform */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Move3D className="h-4 w-4 text-blue-600" />
                      Effects & Transform
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-xs font-medium">Blur ({selectedImageForEdit.enhancementSettings.blur}px)</Label>
                      <Input
                        type="range"
                        min="0"
                        max="10"
                        value={selectedImageForEdit.enhancementSettings.blur}
                        onChange={(e) => handleEnhancementChange('blur', Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <Label className="text-xs font-medium">Rotation ({selectedImageForEdit.enhancementSettings.rotation}°)</Label>
                      <Input
                        type="range"
                        min="-180"
                        max="180"
                        value={selectedImageForEdit.enhancementSettings.rotation}
                        onChange={(e) => handleEnhancementChange('rotation', Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div>
                      <Label className="text-xs font-medium mb-2 block">Filter Effects</Label>
                      <Select
                        value={selectedImageForEdit.enhancementSettings.filter}
                        onValueChange={(value) => handleEnhancementChange('filter', value)}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">None</SelectItem>
                          <SelectItem value="sepia">Sepia</SelectItem>
                          <SelectItem value="grayscale">Grayscale</SelectItem>
                          <SelectItem value="vintage">Vintage</SelectItem>
                          <SelectItem value="professional">Professional</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    handleEnhancementChange('brightness', 0);
                    handleEnhancementChange('contrast', 0);
                    handleEnhancementChange('saturation', 0);
                    handleEnhancementChange('blur', 0);
                    handleEnhancementChange('rotation', 0);
                    handleEnhancementChange('filter', 'none');
                    handleEnhancementChange('aiEnhanced', false);
                  }}
                >
                  <RotateCw className="h-3 w-3 mr-1" />
                  Reset
                </Button>
                <Button variant="outline" size="sm">
                  <Crop className="h-3 w-3 mr-1" />
                  Crop
                </Button>
                <Button variant="outline" size="sm">
                  <Filter className="h-3 w-3 mr-1" />
                  More Filters
                </Button>
                <Button variant="outline" size="sm">
                  <PaletteIcon className="h-3 w-3 mr-1" />
                  Color Grading
                </Button>
              </div>

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setIsEnhancementDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={() => {
                  setIsEnhancementDialogOpen(false);
                  toast({
                    title: "Enhancement Applied",
                    description: "Image enhancements have been saved to your proposal design.",
                  });
                }}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Apply Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* AI Design Options Dialog */}
      <Dialog open={isAIDesignDialogOpen} onOpenChange={setIsAIDesignDialogOpen}>
        <DialogContent className="sm:max-w-[900px] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              AI Generated Design Options
            </DialogTitle>
            <DialogDescription>
              Choose from AI-generated proposal designs tailored to your project type and client needs
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Custom Design Input Section */}
            <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  Describe Your Design Vision
                </CardTitle>
                <CardDescription>
                  Tell AI about your design preferences, industry focus, color preferences, or style requirements
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-sm font-medium mb-2 block">
                    Design Requirements & Preferences
                  </Label>
                  <Textarea
                    placeholder="e.g., 'Modern and professional design with blue color scheme for infrastructure project. Need clean layouts with technical diagrams and corporate styling for city government client...'"
                    value={customDesignInput}
                    onChange={(e) => setCustomDesignInput(e.target.value)}
                    rows={3}
                    className="resize-none"
                  />
                  <div className="flex justify-between items-center mt-2">
                    <p className="text-xs text-gray-500">
                      💡 Be specific about colors, style, industry, or client type for better results
                    </p>
                    <span className="text-xs text-gray-400">
                      {customDesignInput.length}/500
                    </span>
                  </div>
                </div>

                {/* Quick Suggestion Tags */}
                <div>
                  <Label className="text-xs font-medium mb-2 block">Quick Suggestions</Label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      'Modern & minimalist',
                      'Professional corporate',
                      'Colorful & vibrant',
                      'Technical & detailed',
                      'Clean & simple',
                      'Bold & impactful'
                    ].map((suggestion) => (
                      <Button
                        key={suggestion}
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() => {
                          const currentInput = customDesignInput.trim();
                          const newInput = currentInput
                            ? `${currentInput}, ${suggestion.toLowerCase()}`
                            : suggestion;
                          setCustomDesignInput(newInput);
                        }}
                      >
                        + {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>

                {customDesignInput.trim() && (
                  <div className="bg-blue-100 p-3 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-blue-900">AI Preview</p>
                        <p className="text-xs text-blue-700">
                          Based on your input, AI will generate designs focusing on: {
                            customDesignInput.toLowerCase().includes('modern') ? 'modern aesthetics, ' : ''
                          }{
                            customDesignInput.toLowerCase().includes('professional') || customDesignInput.toLowerCase().includes('corporate') ? 'professional styling, ' : ''
                          }{
                            customDesignInput.toLowerCase().includes('colorful') || customDesignInput.toLowerCase().includes('vibrant') ? 'vibrant colors, ' : ''
                          }and your specific requirements.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Design Options Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {aiDesignOptions.map((design) => (
                <Card
                  key={design.id}
                  className={`border-2 cursor-pointer transition-all hover:shadow-lg ${
                    selectedAIDesign === design.id
                      ? 'border-purple-500 bg-purple-50 shadow-md'
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                  onClick={() => setSelectedAIDesign(design.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-3xl">{design.preview}</div>
                      <Badge variant="outline" className="text-xs">
                        {design.category}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg">{design.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {design.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {/* Color Scheme Preview */}
                    <div>
                      <Label className="text-xs font-medium">Color Scheme</Label>
                      <div className="flex space-x-1 mt-1">
                        {design.colorScheme.map((color, index) => (
                          <div
                            key={index}
                            className="w-6 h-6 rounded border"
                            style={{ backgroundColor: color }}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Design Details */}
                    <div className="space-y-2">
                      <div>
                        <Label className="text-xs font-medium">Cover Style</Label>
                        <p className="text-xs text-gray-600">{design.coverStyle}</p>
                      </div>
                      <div>
                        <Label className="text-xs font-medium">Tab Style</Label>
                        <p className="text-xs text-gray-600">{design.tabStyle}</p>
                      </div>
                    </div>

                    {/* Features */}
                    <div>
                      <Label className="text-xs font-medium mb-1 block">Key Features</Label>
                      <div className="flex flex-wrap gap-1">
                        {design.features.map((feature, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {feature}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      <Button
                        size="sm"
                        className="flex-1"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectAIDesign(design.id);
                        }}
                        disabled={selectedAIDesign === design.id}
                      >
                        {selectedAIDesign === design.id ? (
                          <>
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Selected
                          </>
                        ) : (
                          'Use Design'
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          // Future: Open design customization
                          toast({
                            title: "Coming Soon",
                            description: "Design customization will be available in the next update.",
                          });
                        }}
                      >
                        <Wand2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Generate More Designs */}
            <Card className="border-2 border-dashed border-purple-300 bg-gradient-to-r from-purple-50 to-blue-50">
              <CardContent className="p-6 text-center">
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <div className="bg-purple-100 p-3 rounded-full">
                      <Sparkles className="h-8 w-8 text-purple-600" />
                    </div>
                  </div>

                  {isGeneratingDesigns ? (
                    <div className="space-y-3">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                      <h4 className="font-semibold text-purple-900">Generating New Designs...</h4>
                      <p className="text-sm text-purple-700">
                        {customDesignInput.trim()
                          ? "AI is creating custom designs based on your specific requirements..."
                          : "AI is analyzing your proposal requirements to create personalized design options"
                        }
                      </p>
                      <Progress value={65} className="w-48 mx-auto" />
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <h4 className="font-semibold text-purple-900">
                        {customDesignInput.trim() ? "Generate Custom Designs" : "Need More Options?"}
                      </h4>
                      <p className="text-sm text-purple-700 max-w-md mx-auto">
                        {customDesignInput.trim()
                          ? "Generate personalized designs based on your custom requirements above"
                          : "Generate additional AI-powered design variations based on your proposal content and industry focus"
                        }
                      </p>
                      <Button
                        onClick={handleGenerateMoreDesigns}
                        className="bg-purple-600 hover:bg-purple-700"
                      >
                        <Zap className="h-4 w-4 mr-2" />
                        {customDesignInput.trim() ? "Generate Custom Designs" : "Generate More Designs"}
                      </Button>
                      {customDesignInput.trim() && (
                        <p className="text-xs text-purple-600 mt-2">
                          ✨ Custom designs will be created based on: "{customDesignInput.substring(0, 50)}..."
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Selected Design Preview */}
            {selectedAIDesign && (
              <Card className="border-2 border-green-200 bg-green-50">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <h4 className="font-semibold text-green-900">
                        Design Selected: {aiDesignOptions.find(d => d.id === selectedAIDesign)?.name}
                      </h4>
                      <p className="text-sm text-green-700">
                        This design will be applied to your proposal when you close this dialog
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="flex justify-between items-center pt-4 border-t">
            <div className="text-sm text-gray-600">
              💡 Tip: You can further customize any selected design in the main design section
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setIsAIDesignDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => {
                  setIsAIDesignDialogOpen(false);
                  if (selectedAIDesign) {
                    toast({
                      title: "Design Applied Successfully",
                      description: "Your selected AI design has been applied to the proposal. You can further customize it below.",
                    });
                  }
                }}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Apply Design
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Section Details */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5 text-green-600" />
            <span>Section Details Configuration</span>
          </CardTitle>
          <CardDescription>
            Configure sections, page limits, and visual elements for your
            proposal
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Label className="text-base font-medium">
              Total Page Limit: {totalPages} pages
            </Label>
            <Input
              type="number"
              value={totalPages}
              onChange={(e) => setTotalPages(Number(e.target.value))}
              className="mt-2 max-w-32"
            />
          </div>

          <div className="space-y-4">
            {sectionDetails.map((section, index) => (
              <Card key={index} className="border border-gray-200">
                <CardContent className="p-4">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{section.name}</h4>
                        {section.required && (
                          <Badge variant="outline" className="bg-red-50">
                            Required
                          </Badge>
                        )}
                      </div>
                      <div className="space-y-2">
                        <div>
                          <Label className="text-sm">Pages Allocated</Label>
                          <Input
                            type="number"
                            value={section.selectedPages}
                            onChange={(e) =>
                              handleSectionChange(
                                index,
                                "selectedPages",
                                Number(e.target.value),
                              )
                            }
                            max={section.pageLimit}
                            className="mt-1"
                          />
                          {section.pageLimit && (
                            <p className="text-xs text-gray-500">
                              Max: {section.pageLimit} pages
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div>
                      <Label className="text-sm font-medium mb-2 block">
                        Visual Elements
                      </Label>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {[
                          { key: "includeGraphics", label: "Graphics" },
                          { key: "includeInfographics", label: "Infographics" },
                          { key: "includeMatrixes", label: "Matrices" },
                          { key: "includeImages", label: "Images" },
                          { key: "includeTables", label: "Tables" },
                          { key: "includeCharts", label: "Charts" },
                          { key: "includeFlowcharts", label: "Flow Charts" },
                        ].map((element) => (
                          <div
                            key={element.key}
                            className="flex items-center space-x-2"
                          >
                            <Checkbox
                              id={`${index}-${element.key}`}
                              checked={
                                section[
                                  element.key as keyof SectionDetail
                                ] as boolean
                              }
                              onCheckedChange={(checked) =>
                                handleSectionChange(
                                  index,
                                  element.key as keyof SectionDetail,
                                  checked,
                                )
                              }
                            />
                            <Label
                              htmlFor={`${index}-${element.key}`}
                              className="text-xs"
                            >
                              {element.label}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium text-blue-900">
                  Total Pages:{" "}
                  {sectionDetails.reduce(
                    (sum, section) => sum + section.selectedPages,
                    0,
                  )}{" "}
                  / {totalPages}
                </p>
                <p className="text-sm text-blue-700">
                  AI will generate layouts based on your selections
                  {uploadedImages.length > 0 && ` and ${uploadedImages.length} uploaded image(s)`}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Layout Options */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle>Layout & Design Options</CardTitle>
          <CardDescription>
            Choose overall layout patterns for your proposal sections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label className="text-base font-medium mb-3 block">
                Primary Layout
              </Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select layout style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="standard">Standard (1 column)</SelectItem>
                  <SelectItem value="two-column">Two column</SelectItem>
                  <SelectItem value="mixed">Mixed layouts</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-base font-medium mb-3 block">
                Header & Footer Style
              </Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select header/footer" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="minimal">Minimal</SelectItem>
                  <SelectItem value="standard">Standard</SelectItem>
                  <SelectItem value="branded">Branded</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
