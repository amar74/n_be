import React, { useState, useRef, useEffect, SetStateAction, Dispatch } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Building2,
  FileText,
  Plus,
  TrendingUp,
  Users,
  Calendar,
  DollarSign,
  Award,
  FileCheck,
  ShoppingCart,
  Calculator,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Target,
  Play,
  Pause,
  AlertTriangle,
  Clock,
  CheckCircle,
  Shield,
  Zap,
  Eye,
  Receipt,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export function DashboardCarousel({ dashboards, currentDashboard, setCurrentDashboard }: { dashboards: any[]; currentDashboard: number; setCurrentDashboard: Dispatch<SetStateAction<number>>; }) {
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const nextDashboard = () => {
    setCurrentDashboard(prev => (prev + 1) % dashboards.length);
  };

  const prevDashboard = () => {
    setCurrentDashboard(prev => (prev - 1 + dashboards.length) % dashboards.length);
  };

  const toggleAutoScroll = () => {
    setIsAutoScrolling(prev => !prev);
  };

  // Auto-scroll effect
  useEffect(() => {
    if (isAutoScrolling) {
      intervalRef.current = setInterval(() => {
        setCurrentDashboard(prev => (prev + 1) % dashboards.length);
      }, 5000); // 5 seconds
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    // Cleanup interval on component unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isAutoScrolling, dashboards.length]);

  // Clear auto-scroll when user manually navigates
  const handleManualNavigation = (direction: 'next' | 'prev') => {
    if (isAutoScrolling) {
      setIsAutoScrolling(false);
    }
    if (direction === 'next') {
      nextDashboard();
    } else {
      prevDashboard();
    }
  };

  return (
    <>
      <div className="relative">
        {/* Dashboard Header with Navigation */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            {React.createElement(dashboards[currentDashboard].icon, {
              className: `h-6 w-6 text-${dashboards[currentDashboard].color}-600`,
            })}
            <h3 className="text-2xl font-semibold text-[#111827]">
              {dashboards[currentDashboard].name} Dashboard
            </h3>
            {isAutoScrolling && (
              <Badge
                variant="outline"
                className="bg-green-50 text-green-700 border-[#E5E7EB] px-4 py-2 rounded-lg font-medium"
              >
                Auto-scrolling
              </Badge>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleManualNavigation('prev')}
              className="p-3 bg-white hover:bg-[#F9FAFB] text-[#1F2937] border border-[#E5E7EB] rounded-lg transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg"
              title="Previous Dashboard"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>

            <Button
              variant={isAutoScrolling ? 'default' : 'outline'}
              size="sm"
              onClick={toggleAutoScroll}
              className={`p-3 rounded-lg transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg ${isAutoScrolling
                  ? 'bg-[#3B82F6] hover:bg-[#2563EB] text-white'
                  : 'bg-white hover:bg-[#F9FAFB] text-[#1F2937] border border-[#E5E7EB]'}`}
              title={isAutoScrolling ? 'Pause auto-scroll' : 'Resume auto-scroll'}
            >
              {isAutoScrolling ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>

            <span className="text-base text-[#1F2937] px-4 font-medium">
              {currentDashboard + 1} of {dashboards.length}
            </span>

            <Button
              variant="outline"
              size="sm"
              onClick={() => handleManualNavigation('next')}
              className="p-3 bg-white hover:bg-[#F9FAFB] text-[#1F2937] border border-[#E5E7EB] rounded-lg transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg"
              title="Next Dashboard"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="min-h-[500px]">
          {currentDashboard === 1 && (
            // Accounts Dashboard Content
            <div className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <Card className="border border-[#E5E7EB] bg-white rounded-lg hover:border-[#3B82F6] transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-6">
                    <CardTitle className="text-base font-semibold text-[#111827]">
                      Total Accounts
                    </CardTitle>
                    <Building2 className="h-5 w-5 text-purple-600" />
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <div className="text-2xl font-semibold text-purple-600">45</div>
                    <p className="text-base text-[#1F2937] mt-2 leading-relaxed">
                      <span className="text-green-600">+3</span> new this month
                    </p>
                  </CardContent>
                </Card>

                <Card className="border border-[#E5E7EB] bg-white rounded-lg hover:border-[#3B82F6] transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-6">
                    <CardTitle className="text-base font-semibold text-[#111827]">
                      Annual Revenue
                    </CardTitle>
                    <DollarSign className="h-5 w-5 text-green-600" />
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <div className="text-2xl font-semibold text-green-600">$12.4M</div>
                    <p className="text-base text-[#1F2937] mt-2 leading-relaxed">
                      <span className="text-green-600">+8%</span> from last year
                    </p>
                  </CardContent>
                </Card>

                <Card className="border border-[#E5E7EB] bg-white rounded-lg hover:border-[#3B82F6] transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-6">
                    <CardTitle className="text-base font-semibold text-[#111827]">
                      Client Satisfaction
                    </CardTitle>
                    <Award className="h-5 w-5 text-blue-600" />
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <div className="text-2xl font-semibold text-blue-600">92%</div>
                    <p className="text-base text-[#1F2937] mt-2 leading-relaxed">Average rating</p>
                  </CardContent>
                </Card>

                <Card className="border border-[#E5E7EB] bg-white rounded-lg hover:border-[#3B82F6] transition-all duration-200 hover:transform hover:-translate-y-0.5 active:scale-98 shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 p-6">
                    <CardTitle className="text-base font-semibold text-[#111827]">
                      Accounts waiting for approval
                    </CardTitle>
                    <Clock className="h-5 w-5 text-orange-600" />
                  </CardHeader>
                  <CardContent className="p-6 pt-0">
                    <div className="text-2xl font-semibold text-orange-600">5</div>
                    <p className="text-base text-[#1F2937] mt-2 leading-relaxed">
                      Pending manager review
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card className="border border-[#E5E7EB] bg-white rounded-lg shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)]">
                <CardHeader className="p-8">
                  <CardTitle className="text-xl font-semibold text-[#111827]">
                    Top Accounts by Revenue
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 pt-0">
                  <div className="space-y-6">
                    <div className="flex justify-between items-center p-6 bg-green-50 rounded-lg transition-all duration-200 hover:bg-green-100">
                      <div>
                        <p className="font-semibold text-base text-[#111827]">
                          LA Metro (Transportation Authority)
                        </p>
                        <p className="text-base text-[#1F2937] mt-1 leading-relaxed">
                          Government • 1 Active Project (K Line LRT)
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-lg text-green-600">$8.5M</p>
                        <Badge className="bg-green-100 text-green-700 px-3 py-1 rounded-lg font-medium mt-2">
                          Strategic
                        </Badge>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-6 bg-purple-50 rounded-lg transition-all duration-200 hover:bg-purple-100">
                      <div>
                        <p className="font-semibold text-base text-[#111827]">
                          City of Springfield
                        </p>
                        <p className="text-base text-[#1F2937] mt-1 leading-relaxed">
                          Government • 3 Active Projects
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-lg text-purple-600">$5.2M</p>
                        <Badge className="bg-purple-100 text-purple-700 px-3 py-1 rounded-lg font-medium mt-2">
                          Strong
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 0 && (
            // Opportunities Dashboard Content
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Pipeline</CardTitle>
                    <Target className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">24</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+4</span> this month
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Pipeline Value</CardTitle>
                    <DollarSign className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">$8.2M</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+15%</span> vs last quarter
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-purple-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Win Probability</CardTitle>
                    <TrendingUp className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">72%</div>
                    <p className="text-xs text-muted-foreground">Average across pipeline</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-orange-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Pursuits</CardTitle>
                    <Award className="h-4 w-4 text-orange-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600">8</div>
                    <p className="text-xs text-muted-foreground">In proposal stage</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="border-2">
                <CardHeader>
                  <CardTitle>Top Opportunities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-medium">Metro Transit Expansion</p>
                        <p className="text-sm text-muted-foreground">City of Springfield</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">$2.4M</p>
                        <p className="text-sm text-muted-foreground">85% Win Rate</p>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <div>
                        <p className="font-medium">Highway Infrastructure</p>
                        <p className="text-sm text-muted-foreground">State DOT</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-blue-600">$1.8M</p>
                        <p className="text-sm text-muted-foreground">70% Win Rate</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 2 && (
            // Proposals Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Proposals</CardTitle>
                    <FileText className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">12</div>
                    <p className="text-xs text-muted-foreground">In various stages</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">68%</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+5%</span> improvement
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-purple-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg. Creation Time</CardTitle>
                    <Calendar className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">8.2 days</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">-60%</span> with AI
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-orange-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                    <DollarSign className="h-4 w-4 text-orange-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600">$5.2M</div>
                    <p className="text-xs text-muted-foreground">In proposal stage</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="border-2">
                <CardHeader>
                  <CardTitle>Recent Proposals</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <div>
                        <p className="font-medium">Metro Transit Expansion</p>
                        <p className="text-sm text-muted-foreground">Due: Dec 15, 2024</p>
                      </div>
                      <Badge className="bg-green-100 text-green-700">In Review</Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-amber-50 rounded-lg">
                      <div>
                        <p className="font-medium">Highway Infrastructure</p>
                        <p className="text-sm text-muted-foreground">Due: Jan 20, 2025</p>
                      </div>
                      <Badge className="bg-blue-100 text-blue-700">In Progress</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 8 && (
            // KPI Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-violet-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Overall Performance</CardTitle>
                    <BarChart3 className="h-4 w-4 text-violet-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-violet-600">92%</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+8%</span> vs target
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Revenue Growth</CardTitle>
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">+18%</div>
                    <p className="text-xs text-muted-foreground">YoY revenue increase</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Client Satisfaction</CardTitle>
                    <Award className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">4.7/5</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+0.3</span> improvement
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-orange-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Project Efficiency</CardTitle>
                    <Target className="h-4 w-4 text-orange-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-orange-600">87%</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+5%</span> efficiency gain
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Business Performance Metrics */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <TrendingUp className="h-5 w-5 text-violet-600" />
                      <span>Key Business Metrics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Pipeline Conversion</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: '72%' }}
                            ></div>
                          </div>
                          <span className="text-sm font-bold text-green-600">72%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Team Productivity</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: '89%' }}
                            ></div>
                          </div>
                          <span className="text-sm font-bold text-blue-600">89%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Cost Efficiency</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full">
                            <div
                              className="bg-purple-600 h-2 rounded-full"
                              style={{ width: '85%' }}
                            ></div>
                          </div>
                          <span className="text-sm font-bold text-purple-600">85%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Resource Utilization</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full">
                            <div
                              className="bg-orange-600 h-2 rounded-full"
                              style={{ width: '92%' }}
                            ></div>
                          </div>
                          <span className="text-sm font-bold text-orange-600">92%</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                      <span>Department Performance</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Business Development</span>
                        <Badge variant="outline" className="bg-green-50 text-green-700">
                          Exceeding
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Project Delivery</span>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700">
                          On Target
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Finance & Operations</span>
                        <Badge variant="outline" className="bg-green-50 text-green-700">
                          Exceeding
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Client Relations</span>
                        <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                          Needs Focus
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Predictive Analytics and Benchmarking */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2 border-blue-200 bg-blue-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Target className="h-5 w-5 text-blue-600" />
                      <span>Predictive Analytics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600 mb-2">$5.8M</div>
                        <p className="text-sm text-gray-600">Projected Q4 Revenue</p>
                        <p className="text-xs text-blue-600">Based on current pipeline</p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Win Probability</span>
                          <span className="text-sm font-bold text-green-600">74%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Risk Factor</span>
                          <span className="text-sm font-bold text-yellow-600">Medium</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Confidence Level</span>
                          <span className="text-sm font-bold text-blue-600">High</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2 border-green-200 bg-green-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Award className="h-5 w-5 text-green-600" />
                      <span>Industry Benchmarking</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Profit Margin</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-green-600">16.2%</span>
                          <Badge className="bg-green-100 text-green-700 text-xs">
                            Above Industry
                          </Badge>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Client Retention</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-blue-600">94%</span>
                          <Badge className="bg-blue-100 text-blue-700 text-xs">Top Quartile</Badge>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Project Delivery</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-purple-600">87%</span>
                          <Badge className="bg-purple-100 text-purple-700 text-xs">
                            Industry Average
                          </Badge>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Innovation Index</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-orange-600">91%</span>
                          <Badge className="bg-orange-100 text-orange-700 text-xs">
                            Leading Edge
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="text-center">
                <Link to="/kpis">
                  <Button className="bg-violet-600 hover:bg-violet-700">
                    <BarChart3 className="h-4 w-4 mr-2" />
                    View Full KPI Dashboard
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {currentDashboard === 3 && (
            // Resources Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-teal-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Resources</CardTitle>
                    <Users className="h-4 w-4 text-teal-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-teal-600">156</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+12</span> new this month
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg Utilization</CardTitle>
                    <BarChart3 className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">85%</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+3%</span> from last quarter
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">On Bench</CardTitle>
                    <Calendar className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">8</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-red-600">-2</span> from last week
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-purple-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Monthly Impact</CardTitle>
                    <DollarSign className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">$2.1M</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-green-600">+15%</span> profit impact
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card className="border-2">
                <CardHeader>
                  <CardTitle>Top Resources by Utilization & Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <div>
                        <p className="font-medium">Northeast Office</p>
                        <p className="text-sm text-muted-foreground">
                          Project Management • 45 Staff • 96% AI Accuracy
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">92% Utilized</p>
                        <Badge className="bg-green-100 text-green-700">Excellent</Badge>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <div>
                        <p className="font-medium">Southeast Office</p>
                        <p className="text-sm text-muted-foreground">
                          Technical Engineering • 38 Staff • 92% Match Rate
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-blue-600">88% Utilized</p>
                        <Badge className="bg-blue-100 text-blue-700">Strong</Badge>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                      <div>
                        <p className="font-medium">Midwest Office</p>
                        <p className="text-sm text-muted-foreground">
                          Design & Planning • 32 Staff • 25 Competitors Tracked
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-yellow-600">76% Utilized</p>
                        <Badge className="bg-yellow-100 text-yellow-700">Needs Focus</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 4 && (
            // Contracts Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-emerald-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Contracts</CardTitle>
                    <FileCheck className="h-4 w-4 text-emerald-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-emerald-600">12</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-yellow-600">3</span> awaiting review
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-red-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">High Risk</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-red-600">3</div>
                    <p className="text-xs text-muted-foreground">Require immediate attention</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">In Legal Review</CardTitle>
                    <Clock className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">5</div>
                    <p className="text-xs text-muted-foreground">In review queue</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Completed</CardTitle>
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">28</div>
                    <p className="text-xs text-muted-foreground">This quarter</p>
                  </CardContent>
                </Card>
              </div>

              {/* AI Risk Analysis Summary */}
              <Card className="border-2 border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-blue-600" />
                    <span>AI Risk Analysis Summary</span>
                  </CardTitle>
                  <CardDescription>
                    Real-time clause analysis across all active contracts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-red-600 mb-2">47</div>
                      <p className="text-sm text-gray-600">High Risk Clauses</p>
                      <p className="text-xs text-red-600">Across 12 contracts</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-600 mb-2">134</div>
                      <p className="text-sm text-gray-600">Medium Risk Clauses</p>
                      <p className="text-xs text-yellow-600">Need review</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600 mb-2">298</div>
                      <p className="text-sm text-gray-600">Low Risk Clauses</p>
                      <p className="text-xs text-green-600">Acceptable</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Contract Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Clock className="h-5 w-5 text-purple-600" />
                      <span>Recent Contract Activity</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-3">
                          <div className="bg-red-100 p-2 rounded-full">
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">Metro Transit Expansion</p>
                            <p className="text-xs text-gray-600">
                              City of Springfield �� High Risk
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className="bg-red-100 text-red-800 text-xs">5 Red</Badge>
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">12 Amber</Badge>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-3">
                          <div className="bg-blue-100 p-2 rounded-full">
                            <Clock className="h-4 w-4 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">Highway Infrastructure Upgrade</p>
                            <p className="text-xs text-gray-600">State DOT • Medium Risk</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className="bg-red-100 text-red-800 text-xs">2 Red</Badge>
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs">8 Amber</Badge>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex items-center space-x-3">
                          <div className="bg-green-100 p-2 rounded-full">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          </div>
                          <div>
                            <p className="font-medium text-sm">Water Treatment Facility</p>
                            <p className="text-xs text-gray-600">Municipal Authority • Low Risk</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className="bg-green-100 text-green-800 text-xs">Approved</Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-5 w-5 text-orange-600" />
                      <span>Legal Review Queue</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                        <div>
                          <p className="font-medium text-sm">CTR-2024-001</p>
                          <p className="text-xs text-gray-600">Assigned: Sarah Johnson, Esq.</p>
                        </div>
                        <div className="text-right">
                          <Badge className="bg-red-100 text-red-800 text-xs mb-1">URGENT</Badge>
                          <p className="text-xs text-gray-600">2 days overdue</p>
                        </div>
                      </div>

                      <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                        <div>
                          <p className="font-medium text-sm">CTR-2024-002</p>
                          <p className="text-xs text-gray-600">Assigned: Michael Chen, Esq.</p>
                        </div>
                        <div className="text-right">
                          <Badge className="bg-yellow-100 text-yellow-800 text-xs mb-1">
                            PENDING
                          </Badge>
                          <p className="text-xs text-gray-600">Due today</p>
                        </div>
                      </div>

                      <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                        <div>
                          <p className="font-medium text-sm">CTR-2024-003</p>
                          <p className="text-xs text-gray-600">Assigned: Lisa Rodriguez, Esq.</p>
                        </div>
                        <div className="text-right">
                          <Badge className="bg-blue-100 text-blue-800 text-xs mb-1">
                            IN REVIEW
                          </Badge>
                          <p className="text-xs text-gray-600">Due Dec 15</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Clause Library & Workflow Status */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FileText className="h-5 w-5 text-purple-600" />
                      <span>Clause Library Status</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Standard Clauses</span>
                        <Badge variant="outline" className="bg-green-50 text-green-700">
                          45 Active
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Risk Management</span>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700">
                          12 Clauses
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Financial Terms</span>
                        <Badge variant="outline" className="bg-purple-50 text-purple-700">
                          8 Clauses
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Latest Update</span>
                        <Badge variant="outline" className="bg-orange-50 text-orange-700">
                          2 days ago
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-teal-600" />
                      <span>Contract Performance</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Avg Review Time</span>
                        <Badge variant="outline" className="bg-teal-50 text-teal-700">
                          2.3 days
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">AI Accuracy Rate</span>
                        <Badge variant="outline" className="bg-green-50 text-green-700">
                          94%
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Exception Rate</span>
                        <Badge variant="outline" className="bg-yellow-50 text-yellow-700">
                          18%
                        </Badge>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Success Rate</span>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700">
                          87%
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <Card className="border-2 border-emerald-200 bg-emerald-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Plus className="h-5 w-5 text-emerald-600" />
                    <span>Quick Actions</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Link to="/contracts">
                      <Button
                        variant="outline"
                        className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-emerald-100"
                      >
                        <Eye className="h-5 w-5 text-emerald-600" />
                        <span className="text-xs">View All</span>
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-red-100"
                    >
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <span className="text-xs">High Risk</span>
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-blue-100"
                    >
                      <Clock className="h-5 w-5 text-blue-600" />
                      <span className="text-xs">Pending</span>
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-purple-100"
                    >
                      <FileText className="h-5 w-5 text-purple-600" />
                      <span className="text-xs">Add Clause</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 7 && (
            // Procurement Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-amber-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
                    <Clock className="h-4 w-4 text-amber-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-amber-600">$2,127</div>
                    <p className="text-xs text-muted-foreground">8 expense reports</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-purple-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Pending Purchase Orders</CardTitle>
                    <ShoppingCart className="h-4 w-4 text-purple-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-purple-600">$4,300</div>
                    <p className="text-xs text-muted-foreground">3 purchase orders</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Monthly Burn Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-blue-600">$18.2K</div>
                    <p className="text-xs text-muted-foreground">
                      <span className="text-red-600">+12%</span> above target
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Budget Utilization</CardTitle>
                    <Target className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-green-600">78%</div>
                    <p className="text-xs text-muted-foreground">Q4 budget utilized</p>
                  </CardContent>
                </Card>
              </div>

              {/* Vendor Performance and Budget Breakdown */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Building2 className="h-5 w-5 text-amber-600" />
                      <span>Top Vendors by Spend</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-6 h-6 rounded-full bg-yellow-500 flex items-center justify-center text-white text-xs font-bold">
                            1
                          </div>
                          <div>
                            <p className="font-medium text-sm">Microsoft Corporation</p>
                            <p className="text-xs text-gray-600">12 orders • Net 30</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-amber-600">$45,000</p>
                          <div className="flex items-center space-x-1">
                            <span className="text-xs">4.8</span>
                            <span className="text-yellow-500">★</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-6 h-6 rounded-full bg-gray-400 flex items-center justify-center text-white text-xs font-bold">
                            2
                          </div>
                          <div>
                            <p className="font-medium text-sm">Dell Technologies</p>
                            <p className="text-xs text-gray-600">8 orders • Net 45</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-amber-600">$32,000</p>
                          <div className="flex items-center space-x-1">
                            <span className="text-xs">4.6</span>
                            <span className="text-yellow-500">★</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-6 h-6 rounded-full bg-amber-600 flex items-center justify-center text-white text-xs font-bold">
                            3
                          </div>
                          <div>
                            <p className="font-medium text-sm">Amazon Business</p>
                            <p className="text-xs text-gray-600">24 orders • Net 15</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-amber-600">$18,500</p>
                          <div className="flex items-center space-x-1">
                            <span className="text-xs">4.4</span>
                            <span className="text-yellow-500">★</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                      <span>Budget Breakdown</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Travel & Transportation</span>
                          <span className="text-sm">$8,200 / $12,000</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: '68%' }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-600">68% utilized</p>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Software & Licenses</span>
                          <span className="text-sm">$15,400 / $18,000</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-orange-600 h-2 rounded-full"
                            style={{ width: '86%' }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-600">86% utilized</p>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Office Supplies</span>
                          <span className="text-sm">$3,200 / $5,000</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: '64%' }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-600">64% utilized</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Activity and Policy Alerts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Clock className="h-5 w-5 text-purple-600" />
                      <span>Recent Procurement Activity</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                        <div className="bg-green-100 p-2 rounded-full">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">
                            Expense approved: Travel reimbursement
                          </p>
                          <p className="text-xs text-gray-600">
                            Sarah Johnson • $127.50 • 2 hours ago
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                        <div className="bg-purple-100 p-2 rounded-full">
                          <ShoppingCart className="h-4 w-4 text-purple-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">PO created: Office supplies</p>
                          <p className="text-xs text-gray-600">
                            Amazon Business • $450.00 • 4 hours ago
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                        <div className="bg-yellow-100 p-2 rounded-full">
                          <Clock className="h-4 w-4 text-yellow-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">Pending approval: Software licenses</p>
                          <p className="text-xs text-gray-600">
                            David Park • $2,500.00 • 1 day ago
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
                        <div className="bg-blue-100 p-2 rounded-full">
                          <FileText className="h-4 w-4 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium">Invoice received: Dell Technologies</p>
                          <p className="text-xs text-gray-600">
                            PO-2024-001 • $3,200.00 • 2 days ago
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2 border-red-200 bg-red-50">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <span>Policy Alerts & Actions Needed</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-white border border-red-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <AlertCircle className="h-5 w-5 text-red-600" />
                          <div>
                            <p className="text-sm font-medium text-red-900">Expense over limit</p>
                            <p className="text-xs text-red-700">
                              EXP-2024-004: $380 meal exceeds $200 policy
                            </p>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" className="text-red-600 border-red-300">
                          Review
                        </Button>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-white border border-orange-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className="h-5 w-5 text-orange-600" />
                          <div>
                            <p className="text-sm font-medium text-orange-900">Missing receipt</p>
                            <p className="text-xs text-orange-700">
                              EXP-2024-005: Travel expense without receipt
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-orange-600 border-orange-300"
                        >
                          Follow Up
                        </Button>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-white border border-yellow-200 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Clock className="h-5 w-5 text-yellow-600" />
                          <div>
                            <p className="text-sm font-medium text-yellow-900">Overdue invoice</p>
                            <p className="text-xs text-yellow-700">
                              INV-2024-002: Microsoft payment overdue
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-yellow-600 border-yellow-300"
                        >
                          Process
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <Card className="border-2 border-amber-200 bg-amber-50">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-amber-600" />
                    <span>Quick Actions</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Link to="/procurement">
                      <Button
                        variant="outline"
                        className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-green-100"
                      >
                        <Receipt className="h-5 w-5 text-green-600" />
                        <span className="text-xs">Submit Expense</span>
                      </Button>
                    </Link>
                    <Link to="/procurement">
                      <Button
                        variant="outline"
                        className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-purple-100"
                      >
                        <ShoppingCart className="h-5 w-5 text-purple-600" />
                        <span className="text-xs">Create PO</span>
                      </Button>
                    </Link>
                    <Link to="/procurement">
                      <Button
                        variant="outline"
                        className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-blue-100"
                      >
                        <Eye className="h-5 w-5 text-blue-600" />
                        <span className="text-xs">View Reports</span>
                      </Button>
                    </Link>
                    <Link to="/procurement">
                      <Button
                        variant="outline"
                        className="w-full h-16 flex flex-col items-center justify-center space-y-1 hover:bg-amber-100"
                      >
                        <Building2 className="h-5 w-5 text-amber-600" />
                        <span className="text-xs">Manage Vendors</span>
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentDashboard === 5 && (
            // Projects Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-cyan-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
                    <Calendar className="h-4 w-4 text-cyan-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">24</div>
                    <p className="text-xs text-muted-foreground">+3 from last month</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">On Schedule</CardTitle>
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">18</div>
                    <p className="text-xs text-muted-foreground">75% completion rate</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-yellow-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">At Risk</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">4</div>
                    <p className="text-xs text-muted-foreground">Require attention</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Revenue YTD</CardTitle>
                    <DollarSign className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">$12.4M</div>
                    <p className="text-xs text-muted-foreground">+15% from target</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-cyan-600" />
                      <span>Project Portfolio Status</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span className="text-sm">On Track</span>
                        </div>
                        <div className="text-sm font-semibold">18 projects</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span className="text-sm">At Risk</span>
                        </div>
                        <div className="text-sm font-semibold">4 projects</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span className="text-sm">Delayed</span>
                        </div>
                        <div className="text-sm font-semibold">2 projects</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Users className="h-5 w-5 text-cyan-600" />
                      <span>Resource Utilization</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Team Utilization</span>
                          <span className="font-semibold">87%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-cyan-600 h-2 rounded-full"
                            style={{ width: '87%' }}
                          ></div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Billable Hours</span>
                          <span className="font-semibold">92%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: '92%' }}
                          ></div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Available Capacity</span>
                          <span className="font-semibold">13%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: '13%' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="text-center">
                <Link to="/projects">
                  <Button className="bg-cyan-600 hover:bg-cyan-700">
                    <Calendar className="h-4 w-4 mr-2" />
                    View Full Project Management
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {currentDashboard === 6 && (
            // Finance Dashboard
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-2 hover:border-rose-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Net Revenue YTD</CardTitle>
                    <DollarSign className="h-4 w-4 text-rose-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">$4.2M</div>
                    <p className="text-xs text-muted-foreground">+12.5% vs Plan</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-green-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Operating Income</CardTitle>
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">$680K</div>
                    <p className="text-xs text-muted-foreground">Above Plan</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-blue-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Cash Position</CardTitle>
                    <Receipt className="h-4 w-4 text-blue-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">$1.8M</div>
                    <p className="text-xs text-muted-foreground">13-week forecast</p>
                  </CardContent>
                </Card>

                <Card className="border-2 hover:border-orange-300 transition-colors">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">DRO (Days)</CardTitle>
                    <Clock className="h-4 w-4 text-orange-600" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">45</div>
                    <p className="text-xs text-muted-foreground">3 days vs target</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-rose-600" />
                      <span>Revenue Trend</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-rose-500 rounded-full"></div>
                          <span className="text-sm">Q1 2024</span>
                        </div>
                        <div className="text-sm font-semibold">$1.1M</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-pink-500 rounded-full"></div>
                          <span className="text-sm">Q2 2024</span>
                        </div>
                        <div className="text-sm font-semibold">$1.3M</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span className="text-sm">Q3 2024</span>
                        </div>
                        <div className="text-sm font-semibold">$1.8M</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Target className="h-5 w-5 text-rose-600" />
                      <span>Financial KPIs</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Effective Multiplier</span>
                          <span className="font-semibold">2.4x</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-rose-600 h-2 rounded-full"
                            style={{ width: '80%' }}
                          ></div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Billability</span>
                          <span className="font-semibold">87%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: '87%' }}
                          ></div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>EBITA Margin</span>
                          <span className="font-semibold">16.2%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: '65%' }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="text-center">
                <Link to="/finance">
                  <Button className="bg-rose-600 hover:bg-rose-700">
                    <Calculator className="h-4 w-4 mr-2" />
                    View Full Finance Dashboard
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
