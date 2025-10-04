'use client'

import { useState } from 'react'
import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Download } from 'lucide-react'
import { PDFDownloadLink, PDFViewer } from '@react-pdf/renderer'
import { ProfessionalReportPDF } from '@/components/pdf/ProfessionalReportPDF'

// Sample data for preview
const sampleApplication = {
  application_id: "SAMPLE/2024/001",
  reference: "SAMPLE/2024/001",
  uid: "SAMPLE/2024/001",
  name: "Sample Application",
  authority: "Westminster City Council",
  area_name: "Westminster",
  address: "123 Sample Street, London, SW1A 1AA",
  postcode: "SW1A 1AA",
  location: {
    lat: 51.5074,
    lon: -0.1278
  },
  status: "approved",
  app_type: "Full",
  app_state: "Permitted",
  description: "Proposed residential development comprising 50 new apartments with associated amenities, landscaping, and parking facilities. The development includes ground floor commercial units and communal gardens.",
  submission_date: "2024-01-15T00:00:00",
  start_date: "2024-01-15T00:00:00",
  decided_date: "2024-03-20T00:00:00",
  decision_date: "2024-03-20T00:00:00",
  development_type: "residential",
  opportunity_score: 85,
  approval_probability: 0.78,
  applicant_name: "Sample Developments Ltd",
  application_type: "Full Planning Permission",
  case_officer: "John Smith",
  n_documents: 12,
  aiInsights: {
    opportunity_analysis: {
      score: 85,
      confidence: 0.92,
      breakdown: {
        location_score: 90,
        market_demand: 85,
        approval_likelihood: 78,
        timeline_favorability: 88,
        competition_level: 75
      },
      rationale: "High-quality residential development in prime location with strong market demand and favorable planning history.",
      risk_factors: [
        "Potential affordable housing requirements",
        "Heritage considerations in conservation area",
        "Traffic impact assessment needed"
      ],
      recommendations: [
        "Engage with local community early",
        "Consider pre-application consultation",
        "Prepare comprehensive transport assessment"
      ]
    },
    summary_analysis: {
      summary: "Well-designed residential scheme with strong commercial viability and good compliance with local planning policy.",
      key_points: [
        "50 high-quality apartments",
        "Ground floor commercial units",
        "Sustainable design features",
        "Community benefits package"
      ],
      sentiment: "positive",
      complexity_score: 7
    },
    market_context: {
      average_approval_rate: 0.72,
      similar_applications: 15,
      market_trends: "positive",
      demand_indicators: {
        housing_demand: "high",
        commercial_demand: "moderate"
      }
    }
  }
}

export default function SampleReport() {
  const [viewMode, setViewMode] = useState<'preview' | 'download'>('preview')

  return (
    <div className="min-h-screen bg-gray-50">
      <Container className="py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Professional Report Sample
          </h1>
          <p className="text-gray-600">
            Preview of the bank-grade professional planning report template
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Report Preview</h2>
              <p className="text-sm text-gray-600 mt-1">
                This is a sample report using mock data to demonstrate the professional template
              </p>
            </div>
            <PDFDownloadLink
              document={<ProfessionalReportPDF application={sampleApplication} />}
              fileName={`Planning_Report_Sample.pdf`}
            >
              {({ loading }) => (
                <Button disabled={loading}>
                  <Download className="w-4 h-4 mr-2" />
                  {loading ? 'Generating PDF...' : 'Download Sample PDF'}
                </Button>
              )}
            </PDFDownloadLink>
          </div>

          <div className="border rounded-lg overflow-hidden" style={{ height: '800px' }}>
            <PDFViewer width="100%" height="100%">
              <ProfessionalReportPDF application={sampleApplication} />
            </PDFViewer>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            About This Report
          </h3>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Bank-grade professional formatting with branded design</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Comprehensive AI-powered opportunity analysis and risk assessment</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Market intelligence with data visualizations and insights</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Multi-page layout with executive summary, detailed analysis, and appendices</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Professional charts, graphs, and infographics</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Downloadable PDF format for sharing with stakeholders</span>
            </li>
          </ul>
        </div>
      </Container>
    </div>
  )
}
