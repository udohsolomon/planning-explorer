'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { MapPin, Building, Users, Target, ChevronRight, Check } from 'lucide-react'
import { useUserStore } from '@/stores/userStore'

interface OnboardingProps {
  onComplete?: () => void
}

const STEPS = [
  { id: 'profile', title: 'Complete your profile', description: 'Tell us about yourself' },
  { id: 'interests', title: 'Your interests', description: 'What are you looking for?' },
  { id: 'preferences', title: 'Preferences', description: 'Customize your experience' },
  { id: 'complete', title: 'All set!', description: 'Start exploring' }
]

const INDUSTRIES = [
  'Residential Development',
  'Commercial Development',
  'Industrial Development',
  'Infrastructure',
  'Retail',
  'Mixed Use',
  'Planning Consultancy',
  'Local Authority',
  'Architecture',
  'Engineering',
  'Legal Services',
  'Property Investment',
  'Other'
]

const INTERESTS = [
  'New Applications',
  'Planning Decisions',
  'Appeal Cases',
  'Committee Meetings',
  'Policy Changes',
  'Market Trends',
  'Competitor Analysis',
  'Site Opportunities',
  'Development Finance',
  'Planning Law Updates'
]

export function Onboarding({ onComplete }: OnboardingProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    role: '',
    industry: '',
    location: '',
    interests: [] as string[],
    aiInsights: true,
    emailNotifications: true,
    searchRadius: 5
  })

  const { user, updateProfile, updatePreferences } = useUserStore()

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }))
  }

  const handleComplete = async () => {
    // Update user profile and preferences
    if (user) {
      updateProfile({
        role: formData.role,
        industry: formData.industry,
        location: { city: formData.location },
        interests: formData.interests,
        preferences: {
          aiInsightTypes: [],
          aiInsightFrequency: 'daily',
          contentPersonalization: formData.aiInsights,
          emailNotifications: formData.emailNotifications,
          browserNotifications: true,
          alertFrequency: 'daily',
          theme: 'light',
          compactView: false,
          defaultSearchRadius: formData.searchRadius,
          defaultSearchFilters: {},
          dataSharing: false,
          analytics: true,
          marketingEmails: false
        },
        updatedAt: new Date().toISOString()
      })

      updatePreferences({
        contentPersonalization: formData.aiInsights,
        emailNotifications: formData.emailNotifications,
        defaultSearchRadius: formData.searchRadius
      })
    }

    onComplete?.()
  }

  const step = STEPS[currentStep]

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mb-8">
        {/* Progress bar */}
        <div className="flex items-center justify-between mb-4">
          {STEPS.map((s, index) => (
            <div key={s.id} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                index < currentStep ? 'bg-planning-bright text-white' :
                index === currentStep ? 'bg-planning-primary text-white' :
                'bg-gray-200 text-gray-500'
              }`}>
                {index < currentStep ? <Check className="w-4 h-4" /> : index + 1}
              </div>
              {index < STEPS.length - 1 && (
                <div className={`w-16 h-0.5 ml-2 ${
                  index < currentStep ? 'bg-planning-bright' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-planning-primary">{step.title}</h2>
          <p className="text-planning-text-light">{step.description}</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-8">
          {currentStep === 0 && (
            <div className="space-y-6">
              <Input
                label="Your role"
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                leftIcon={<Users />}
                placeholder="e.g., Senior Planner, Development Manager"
              />

              <div>
                <label className="block text-sm font-medium text-planning-text-dark mb-3">
                  Industry
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {INDUSTRIES.map((industry) => (
                    <button
                      key={industry}
                      onClick={() => setFormData(prev => ({ ...prev, industry }))}
                      className={`p-3 text-left rounded-lg border transition-colors ${
                        formData.industry === industry
                          ? 'border-planning-primary bg-planning-primary/10 text-planning-primary'
                          : 'border-planning-border hover:border-planning-primary/50'
                      }`}
                    >
                      <div className="text-sm font-medium">{industry}</div>
                    </button>
                  ))}
                </div>
              </div>

              <Input
                label="Location"
                value={formData.location}
                onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                leftIcon={<MapPin />}
                placeholder="e.g., London, Manchester, Birmingham"
                helperText="This helps us provide relevant local insights"
              />
            </div>
          )}

          {currentStep === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-planning-primary mb-3">
                  What are you most interested in?
                </h3>
                <p className="text-planning-text-light mb-6">
                  Select all that apply. We'll use this to personalize your experience.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {INTERESTS.map((interest) => (
                    <button
                      key={interest}
                      onClick={() => handleInterestToggle(interest)}
                      className={`p-4 text-left rounded-lg border transition-colors ${
                        formData.interests.includes(interest)
                          ? 'border-planning-primary bg-planning-primary/10'
                          : 'border-planning-border hover:border-planning-primary/50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{interest}</span>
                        {formData.interests.includes(interest) && (
                          <Check className="w-4 h-4 text-planning-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-planning-primary mb-6">
                  Customize your experience
                </h3>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">AI-powered insights</h4>
                      <p className="text-sm text-planning-text-light">
                        Get personalized recommendations and market intelligence
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={formData.aiInsights}
                        onChange={(e) => setFormData(prev => ({ ...prev, aiInsights: e.target.checked }))}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-planning-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-planning-primary"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">Email notifications</h4>
                      <p className="text-sm text-planning-text-light">
                        Receive alerts and updates via email
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={formData.emailNotifications}
                        onChange={(e) => setFormData(prev => ({ ...prev, emailNotifications: e.target.checked }))}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-planning-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-planning-primary"></div>
                    </label>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-4">Default search radius</h4>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="1"
                        max="50"
                        value={formData.searchRadius}
                        onChange={(e) => setFormData(prev => ({ ...prev, searchRadius: parseInt(e.target.value) }))}
                        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                      />
                      <Badge variant="outline" className="min-w-[80px]">
                        {formData.searchRadius} miles
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="text-center space-y-6">
              <div className="mx-auto w-16 h-16 bg-planning-bright/10 rounded-full flex items-center justify-center">
                <Check className="w-8 h-8 text-planning-bright" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-planning-primary mb-2">
                  Welcome to Planning Explorer!
                </h3>
                <p className="text-planning-text-light">
                  Your account is all set up. Start exploring planning opportunities with our AI-powered insights.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="text-center">
                  <Target className="w-8 h-8 mx-auto text-planning-primary mb-2" />
                  <h4 className="font-medium">Personalized</h4>
                  <p className="text-sm text-planning-text-light">AI insights tailored to you</p>
                </div>
                <div className="text-center">
                  <Building className="w-8 h-8 mx-auto text-planning-primary mb-2" />
                  <h4 className="font-medium">Comprehensive</h4>
                  <p className="text-sm text-planning-text-light">Full UK planning database</p>
                </div>
                <div className="text-center">
                  <Users className="w-8 h-8 mx-auto text-planning-primary mb-2" />
                  <h4 className="font-medium">Collaborative</h4>
                  <p className="text-sm text-planning-text-light">Share and team features</p>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-between mt-8">
            <Button
              variant="ghost"
              onClick={handleBack}
              disabled={currentStep === 0}
            >
              Back
            </Button>

            {currentStep < STEPS.length - 1 ? (
              <Button onClick={handleNext}>
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleComplete}>
                Get Started
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}