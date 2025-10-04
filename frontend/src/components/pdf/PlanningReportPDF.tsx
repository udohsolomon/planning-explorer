import { Document, Page, Text, View, StyleSheet, Image } from '@react-pdf/renderer'
import { PlanningApplicationResponse } from '@/lib/api'

// Define styles for the PDF document
const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 30,
    fontFamily: 'Helvetica',
  },

  // Header styles
  header: {
    marginBottom: 30,
    paddingBottom: 20,
    borderBottomWidth: 2,
    borderBottomColor: '#2563EB',
  },

  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 15,
  },

  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2563EB',
    marginBottom: 5,
  },

  subtitle: {
    fontSize: 12,
    color: '#6B7280',
  },

  logoSection: {
    alignItems: 'flex-end',
  },

  reportId: {
    fontSize: 10,
    color: '#9CA3AF',
  },

  // Quick summary styles
  quickSummary: {
    flexDirection: 'row',
    backgroundColor: '#F9FAFB',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },

  summaryItem: {
    flex: 1,
    marginRight: 15,
  },

  summaryLabel: {
    fontSize: 10,
    color: '#6B7280',
    marginBottom: 3,
  },

  summaryValue: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#2563EB',
  },

  statusBadge: {
    backgroundColor: '#FEF3C7',
    color: '#92400E',
    padding: '4 8',
    borderRadius: 4,
    fontSize: 10,
    fontWeight: 'bold',
    textAlign: 'center',
  },

  // Section styles
  section: {
    marginBottom: 25,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 20,
  },

  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2563EB',
    marginLeft: 10,
  },

  sectionIcon: {
    width: 20,
    height: 20,
    color: '#2563EB',
  },

  // Content styles
  contentBlock: {
    marginBottom: 15,
  },

  blockTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 8,
  },

  blockText: {
    fontSize: 11,
    color: '#4B5563',
    lineHeight: 1.5,
  },

  // Grid styles
  grid: {
    flexDirection: 'row',
    gap: 20,
  },

  gridItem: {
    flex: 1,
  },

  // List styles
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },

  bullet: {
    width: 4,
    height: 4,
    backgroundColor: '#2563EB',
    borderRadius: 2,
    marginRight: 10,
    marginTop: 6,
  },

  listText: {
    flex: 1,
    fontSize: 11,
    color: '#4B5563',
    lineHeight: 1.4,
  },

  // AI Analysis styles
  aiMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
    backgroundColor: '#F8FAFC',
    padding: 15,
    borderRadius: 8,
  },

  metric: {
    alignItems: 'center',
  },

  metricLabel: {
    fontSize: 10,
    color: '#6B7280',
    marginBottom: 5,
  },

  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1E40AF',
  },

  // Footer styles
  footer: {
    marginTop: 'auto',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    alignItems: 'center',
  },

  footerText: {
    fontSize: 10,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 3,
  },

  copyright: {
    fontSize: 8,
    color: '#9CA3AF',
    textAlign: 'center',
  },
})

interface PlanningReportPDFProps {
  application: PlanningApplicationResponse
  aiInsights?: any
  marketInsights?: any
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'approved':
      return { backgroundColor: '#DCFCE7', color: '#166534' }
    case 'rejected':
      return { backgroundColor: '#FEE2E2', color: '#DC2626' }
    case 'pending':
      return { backgroundColor: '#FEF3C7', color: '#92400E' }
    default:
      return { backgroundColor: '#F3F4F6', color: '#374151' }
  }
}

const PlanningReportPDF: React.FC<PlanningReportPDFProps> = ({
  application,
  aiInsights,
  marketInsights,
}) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.title}>Planning Application Report</Text>
            <Text style={styles.subtitle}>
              Generated on {formatDate(new Date().toISOString())}
            </Text>
          </View>
          <View style={styles.logoSection}>
            <Text style={[styles.subtitle, { fontSize: 14, fontWeight: 'bold' }]}>
              Planning Explorer
            </Text>
            <Text style={styles.reportId}>
              Report ID: {application.reference || 'N/A'}
            </Text>
          </View>
        </View>

        {/* Quick Summary */}
        <View style={styles.quickSummary}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Reference</Text>
            <Text style={styles.summaryValue}>{application.reference}</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Status</Text>
            <View style={[styles.statusBadge, getStatusColor(application.status)]}>
              <Text>{application.status}</Text>
            </View>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Submission Date</Text>
            <Text style={styles.summaryValue}>
              {application.submissionDate ? formatDate(application.submissionDate) : 'N/A'}
            </Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Local Authority</Text>
            <Text style={styles.summaryValue}>{application.localAuthority || application.area_name || application.authority || 'N/A'}</Text>
          </View>
        </View>
      </View>

      {/* Application Details Section */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Application Details</Text>
        </View>

        <View style={styles.contentBlock}>
          <Text style={styles.blockTitle}>Description</Text>
          <Text style={styles.blockText}>{application.description || 'No description available'}</Text>
        </View>

        <View style={styles.grid}>
          <View style={styles.gridItem}>
            <Text style={styles.blockTitle}>Property Information</Text>
            <Text style={styles.blockText}>Address: {application.address || 'N/A'}</Text>
            <Text style={styles.blockText}>Postcode: {application.postcode || 'N/A'}</Text>
            <Text style={styles.blockText}>Ward: {application.ward || 'N/A'}</Text>
          </View>
          <View style={styles.gridItem}>
            <Text style={styles.blockTitle}>Application Type</Text>
            <Text style={styles.blockText}>Type: {application.applicationType || application.app_type || 'N/A'}</Text>
            <Text style={styles.blockText}>
              Decision Date: {application.decisionDate ? formatDate(application.decisionDate) : 'Pending'}
            </Text>
          </View>
        </View>
      </View>

      {/* AI Analysis Section */}
      {aiInsights && (
        <View style={styles.section} break>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>AI Intelligence Analysis</Text>
          </View>

          <View style={styles.aiMetrics}>
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>Opportunity Score</Text>
              <Text style={styles.metricValue}>{aiInsights.score || 0}/100</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>Approval Probability</Text>
              <Text style={styles.metricValue}>{aiInsights.confidence || 0}%</Text>
            </View>
            <View style={styles.metric}>
              <Text style={styles.metricLabel}>Risk Level</Text>
              <Text style={[styles.metricValue, { textTransform: 'capitalize' }]}>
                {aiInsights.riskLevel || 'Medium'}
              </Text>
            </View>
          </View>

          {aiInsights.predictedOutcome && (
            <View style={styles.contentBlock}>
              <Text style={styles.blockTitle}>AI Prediction</Text>
              <Text style={styles.blockText}>{aiInsights.predictedOutcome}</Text>
            </View>
          )}

          {aiInsights.opportunities && Array.isArray(aiInsights.opportunities) && aiInsights.opportunities.length > 0 && (
            <View style={styles.contentBlock}>
              <Text style={styles.blockTitle}>Identified Opportunities</Text>
              {aiInsights.opportunities.map((opp: string, index: number) => (
                <View key={index} style={styles.listItem}>
                  <View style={styles.bullet} />
                  <Text style={styles.listText}>{opp}</Text>
                </View>
              ))}
            </View>
          )}

          {aiInsights.concerns && Array.isArray(aiInsights.concerns) && aiInsights.concerns.length > 0 && (
            <View style={styles.contentBlock}>
              <Text style={styles.blockTitle}>Potential Concerns</Text>
              {aiInsights.concerns.map((concern: string, index: number) => (
                <View key={index} style={styles.listItem}>
                  <View style={styles.bullet} />
                  <Text style={styles.listText}>{concern}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Market Insights Section */}
      {marketInsights && (
        <View style={styles.section} break>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Market Intelligence</Text>
          </View>

          <View style={styles.grid}>
            {marketInsights.location_insights && (
              <View style={styles.gridItem}>
                <Text style={styles.blockTitle}>Location Insights</Text>
                {Object.entries(marketInsights.location_insights)
                  .slice(0, 5)
                  .map(([key, value]: [string, any]) => (
                    <Text key={key} style={styles.blockText}>
                      {key.replace(/_/g, ' ')}: {value}
                    </Text>
                  ))}
              </View>
            )}

            {marketInsights.authority_performance && (
              <View style={styles.gridItem}>
                <Text style={styles.blockTitle}>Authority Performance</Text>
                {Object.entries(marketInsights.authority_performance)
                  .slice(0, 5)
                  .map(([key, value]: [string, any]) => (
                    <Text key={key} style={styles.blockText}>
                      {key.replace(/_/g, ' ')}: {value}
                    </Text>
                  ))}
              </View>
            )}
          </View>

          {marketInsights.recommendations && Array.isArray(marketInsights.recommendations) && marketInsights.recommendations.length > 0 && (
            <View style={styles.contentBlock}>
              <Text style={styles.blockTitle}>Market Recommendations</Text>
              {marketInsights.recommendations.slice(0, 5).map((rec: string, index: number) => (
                <View key={index} style={styles.listItem}>
                  <View style={styles.bullet} />
                  <Text style={styles.listText}>{rec}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Documents Section */}
      {application.documents && Array.isArray(application.documents) && application.documents.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Associated Documents</Text>
          </View>

          {application.documents.map((doc, index) => (
            <View key={doc.id || index} style={styles.listItem}>
              <View style={styles.bullet} />
              <View style={{ flex: 1 }}>
                <Text style={[styles.listText, { fontWeight: 'bold' }]}>{doc.name || 'Unnamed Document'}</Text>
                <Text style={styles.listText}>Type: {doc.type || 'Unknown'}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          This report was generated by Planning Explorer AI Intelligence System
        </Text>
        <Text style={styles.footerText}>
          Report generated on {formatDate(new Date().toISOString())} | Application ID: {application.reference || 'N/A'}
        </Text>
        <Text style={styles.copyright}>
          © 2024 Planning Explorer. All rights reserved.
        </Text>
      </View>
    </Page>
  </Document>
)

export default PlanningReportPDF