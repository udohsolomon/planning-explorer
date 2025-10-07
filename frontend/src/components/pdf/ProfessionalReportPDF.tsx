import React from 'react'
import {
  Document,
  Page,
  View,
  Text,
  Image,
  StyleSheet,
  Font,
  PDFViewer,
  Link,
  Svg,
  Path,
  Circle,
  Rect,
  Line,
  G,
  Defs,
  LinearGradient,
  Stop
} from '@react-pdf/renderer'
import { PlanningApplicationResponse } from '@/lib/api'

// Don't register any fonts - remove ALL fontWeight properties
// @react-pdf/renderer has issues with font registration in browser environments
// We'll use default fonts without any weight specifications

// Professional color scheme - Matching web exactly
const colors = {
  primary: '#043F2E', // Planning Insights deep green (exact brand match)
  secondary: '#065940', // Planning Insights secondary green
  accent: '#087952', // Planning Insights accent green
  text: '#1e293b', // slate-800 (matching web headers)
  lightText: '#64748b',
  border: '#e2e8f0',
  background: '#f8fafc',
  white: '#ffffff',
  success: '#043F2E', // Use Planning green for success
  warning: '#ca8a04', // yellow-600 (matching web)
  danger: '#dc2626', // red-600 (matching web)
  info: '#2563eb' // blue-600 (matching web)
}

// Create styles for the PDF
const styles = StyleSheet.create({
  page: {
    backgroundColor: colors.white,
    fontFamily: 'Helvetica',
  },
  coverPage: {
    position: 'relative',
    padding: 0,
    backgroundColor: colors.primary,
    color: colors.white,
  },
  coverImage: {
    width: '100%',
    height: '50%',
    objectFit: 'cover',
  },
  coverContent: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 40,
    backgroundColor: colors.primary,
  },
  coverTitle: {
    fontSize: 48,

    color: colors.white,
    marginBottom: 8,
    letterSpacing: -1,
  },
  coverSubtitle: {
    fontSize: 20,

    color: colors.white,
    opacity: 0.9,
  },
  coverMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 30,
    paddingTop: 20,
    borderTop: '1px solid rgba(255,255,255,0.2)',
  },
  coverMetaItem: {
    flex: 1,
  },
  coverMetaLabel: {
    fontSize: 10,
    color: colors.white,
    opacity: 0.7,
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  coverMetaValue: {
    fontSize: 14,
    color: colors.white,
    
  },
  tocPage: {
    padding: 40,
    backgroundColor: colors.background,
  },
  tocTitle: {
    fontSize: 36,
    
    color: colors.primary,
    marginBottom: 40,
    letterSpacing: 8,
    textTransform: 'uppercase',
    opacity: 0.2,
  },
  tocItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    paddingBottom: 20,
    borderBottom: `1px dotted ${colors.border}`,
  },
  tocItemTitle: {
    fontSize: 14,
    color: colors.text,
    
  },
  tocItemPage: {
    fontSize: 14,
    color: colors.lightText,
  },
  contentPage: {
    padding: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
    paddingBottom: 24,
    borderBottom: `2px solid ${colors.secondary}`,
  },
  headerTitle: {
    fontSize: 30,

    color: colors.primary,
  },
  headerIcon: {
    width: 40,
    height: 40,
  },
  section: {
    marginBottom: 32,
    wrap: true, // Allow wrapping to next page if needed
    orphans: 2, // Prevent orphaned lines
    widows: 2, // Prevent widow lines
  },
  sectionTitle: {
    fontSize: 12,

    color: colors.primary,
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  card: {
    backgroundColor: colors.white,
    border: `1px solid ${colors.border}`,
    borderRadius: 16,
    padding: 40,
    marginBottom: 15,
  },
  cardHighlight: {
    backgroundColor: colors.background,
    border: `2px solid ${colors.secondary}`,
    borderRadius: 8,
    padding: 20,
    marginBottom: 15,
  },
  keyInfoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 24,
  },
  keyInfoItem: {
    width: '48%',
    padding: 15,
    backgroundColor: colors.white,
    borderRadius: 8,
    border: `1px solid ${colors.border}`,
  },
  keyInfoLabel: {
    fontSize: 10,
    color: colors.lightText,
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  keyInfoValue: {
    fontSize: 20,

    color: colors.primary,
  },
  keyInfoSubvalue: {
    fontSize: 11,
    color: colors.lightText,
    marginTop: 2,
  },
  mapContainer: {
    width: '100%',
    height: 200,
    backgroundColor: colors.background,
    borderRadius: 8,
    marginVertical: 15,
    border: `1px solid ${colors.border}`,
    alignItems: 'center',
    justifyContent: 'center',
    break: false, // Prevent map from splitting across pages
  },
  mapPlaceholder: {
    fontSize: 12,
    color: colors.lightText,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  statusText: {
    fontSize: 11,
    
    textTransform: 'uppercase',
  },
  chartContainer: {
    marginVertical: 20,
    padding: 20,
    backgroundColor: colors.background,
    borderRadius: 8,
    break: false, // Prevent charts from splitting across pages
  },
  chartTitle: {
    fontSize: 14,
    
    color: colors.text,
    marginBottom: 15,
  },
  scoreCard: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 20,
  },
  scoreItem: {
    alignItems: 'center',
    flex: 1,
  },
  scoreCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  scoreValue: {
    fontSize: 30,

    color: colors.white,
  },
  scoreLabel: {
    fontSize: 11,
    color: colors.text,
    textAlign: 'center',
  },
  dataTable: {
    marginVertical: 15,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: colors.primary,
    padding: 10,
    borderRadius: 4,
  },
  tableHeaderText: {
    flex: 1,
    fontSize: 10,
    
    color: colors.white,
    textTransform: 'uppercase',
  },
  tableRow: {
    flexDirection: 'row',
    padding: 10,
    borderBottom: `1px solid ${colors.border}`,
  },
  tableCell: {
    flex: 1,
    fontSize: 11,
    color: colors.text,
  },
  footer: {
    position: 'absolute',
    bottom: 20,
    left: 40,
    right: 40,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 10,
    borderTop: `1px solid ${colors.border}`,
  },
  footerText: {
    fontSize: 9,
    color: colors.lightText,
  },
  pageNumber: {
    fontSize: 9,
    color: colors.lightText,
  },
  brandLogo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  logoText: {
    fontSize: 20,
    
    color: colors.secondary,
    marginLeft: 10,
  },
  qrCode: {
    width: 80,
    height: 80,
    backgroundColor: colors.background,
    padding: 10,
    borderRadius: 8,
    border: `1px solid ${colors.border}`,
  },
  iconGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginVertical: 15,
  },
  iconItem: {
    width: '22%',
    alignItems: 'center',
    padding: 10,
  },
  iconLabel: {
    fontSize: 9,
    color: colors.text,
    marginTop: 5,
    textAlign: 'center',
  },
  insightCard: {
    backgroundColor: `linear-gradient(135deg, ${colors.accent}10, ${colors.secondary}10)`,
    borderLeft: `4px solid ${colors.secondary}`,
    padding: 15,
    marginVertical: 10,
    borderRadius: 4,
  },
  insightTitle: {
    fontSize: 12,
    
    color: colors.primary,
    marginBottom: 8,
  },
  insightText: {
    fontSize: 11,
    color: colors.text,
    lineHeight: 1.5,
  },
  bulletPoint: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  bullet: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.secondary,
    marginRight: 10,
    marginTop: 4,
  },
  bulletText: {
    flex: 1,
    fontSize: 11,
    color: colors.text,
    lineHeight: 1.5,
  }
})

interface ProfessionalReportPDFProps {
  application: PlanningApplicationResponse
  aiInsights?: any
  marketInsights?: any
}

const getStatusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case 'approved':
      return colors.success
    case 'rejected':
      return colors.danger
    case 'pending':
      return colors.warning
    default:
      return colors.info
  }
}

const formatStatus = (status: string) => {
  if (!status) return 'N/A'
  // Convert underscore_case or camelCase to TITLE CASE
  return status
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .trim()
    .toUpperCase()
}

export function ProfessionalReportPDF({
  application,
  aiInsights,
  marketInsights
}: ProfessionalReportPDFProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  return (
    <Document>
      {/* Cover Page */}
      <Page size="A4" style={styles.coverPage}>
        <View style={{ height: '50%', backgroundColor: '#1e293b' }}>
          {/* Map placeholder or property image */}
          <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
            <Svg width="200" height="200" viewBox="0 0 24 24" fill="none">
              <Path
                d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"
                fill={colors.white}
                opacity={0.3}
              />
            </Svg>
          </View>
        </View>
        <View style={styles.coverContent}>
          <Text style={styles.coverTitle}>PROPERTY REPORT</Text>
          <Text style={styles.coverSubtitle}>
            Created on {formatDate(new Date().toISOString())}
          </Text>

          <View style={{ marginTop: 20 }}>
            <Text style={{ fontSize: 16, color: colors.white, opacity: 0.9, marginBottom: 8 }}>
              {application.address || 'N/A'}
            </Text>
            <Text style={{ fontSize: 14, color: colors.white, opacity: 0.7 }}>
              {application.postcode || 'N/A'}
            </Text>
          </View>

          <View style={styles.coverMeta}>
            <View style={styles.coverMetaItem}>
              <Text style={styles.coverMetaLabel}>Reference</Text>
              <Text style={styles.coverMetaValue}>{application.reference}</Text>
            </View>
            <View style={styles.coverMetaItem}>
              <Text style={styles.coverMetaLabel}>Authority</Text>
              <Text style={styles.coverMetaValue}>{application.localAuthority || application.area_name || application.authority || 'N/A'}</Text>
            </View>
            <View style={styles.coverMetaItem}>
              <Text style={styles.coverMetaLabel}>Status</Text>
              <Text style={styles.coverMetaValue}>{formatStatus(application.status)}</Text>
            </View>
          </View>

          <View style={{ position: 'absolute', bottom: 20, right: 40 }}>
            <View style={styles.qrCode}>
              <Svg width="60" height="60" viewBox="0 0 100 100">
                {/* Simplified QR code pattern */}
                <Rect x="10" y="10" width="20" height="20" fill={colors.primary} />
                <Rect x="40" y="10" width="20" height="20" fill={colors.primary} />
                <Rect x="70" y="10" width="20" height="20" fill={colors.primary} />
                <Rect x="10" y="40" width="20" height="20" fill={colors.primary} />
                <Rect x="70" y="40" width="20" height="20" fill={colors.primary} />
                <Rect x="10" y="70" width="20" height="20" fill={colors.primary} />
                <Rect x="40" y="70" width="20" height="20" fill={colors.primary} />
                <Rect x="70" y="70" width="20" height="20" fill={colors.primary} />
              </Svg>
            </View>
            <Text style={{ fontSize: 8, color: colors.white, opacity: 0.5, marginTop: 5 }}>
              Scan to view online
            </Text>
          </View>
        </View>
      </Page>

      {/* Table of Contents - Matching Web Exactly */}
      <Page size="A4" style={styles.tocPage}>
        <Text style={styles.tocTitle}>CONTENTS</Text>
        <View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>KEY PLANNING INFORMATION</Text>
            <Text style={styles.tocItemPage}>1</Text>
          </View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>APPLICATION DETAILS</Text>
            <Text style={styles.tocItemPage}>2</Text>
          </View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>AI INTELLIGENCE ANALYSIS</Text>
            <Text style={styles.tocItemPage}>3</Text>
          </View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>MARKET INSIGHTS</Text>
            <Text style={styles.tocItemPage}>4</Text>
          </View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>OPPORTUNITY ASSESSMENT</Text>
            <Text style={styles.tocItemPage}>5</Text>
          </View>
          <View style={styles.tocItem}>
            <Text style={styles.tocItemTitle}>DOCUMENTS & APPENDIX</Text>
            <Text style={styles.tocItemPage}>6</Text>
          </View>
        </View>
      </Page>

      {/* Executive Summary Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>EXECUTIVE SUMMARY</Text>
          <View style={styles.brandLogo}>
            <Text style={styles.logoText}>Planning Explorer</Text>
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.cardHighlight}>
            <Text style={{ fontSize: 12, color: colors.text, lineHeight: 1.6, marginBottom: 15 }}>
              This planning application analysis is based on comprehensive AI intelligence and market data, providing actionable insights for informed decision-making.
            </Text>

            {/* Key Highlights */}
            {((application.aiInsights?.opportunities && Array.isArray(application.aiInsights.opportunities) && application.aiInsights.opportunities.length > 0) ||
              (aiInsights?.opportunities && Array.isArray(aiInsights.opportunities) && aiInsights.opportunities.length > 0)) && (
              <View style={{ marginTop: 12 }}>
                <Text style={{ fontSize: 10, color: colors.lightText, marginBottom: 8, textTransform: 'uppercase' }}>Key Highlights</Text>
                {(application.aiInsights?.opportunities || aiInsights?.opportunities || []).slice(0, 3).map((highlight: string, index: number) => (
                  <View key={index} style={styles.bulletPoint}>
                    <View style={styles.bullet} />
                    <Text style={styles.bulletText}>{highlight}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        </View>

        {/* Investment Ratings */}
        <View style={styles.section}>
          <View style={{ flexDirection: 'row', gap: 15 }}>
            <View style={[styles.keyInfoItem, { flex: 1 }]}>
              <Text style={styles.keyInfoLabel}>Investment Rating</Text>
              <Text style={[styles.keyInfoValue, { color: colors.success, fontSize: 20 }]}>
                {application.aiInsights?.score >= 70 ? 'STRONG' : application.aiInsights?.score >= 50 ? 'MODERATE' : 'CAUTIOUS'}
              </Text>
            </View>
            <View style={[styles.keyInfoItem, { flex: 1 }]}>
              <Text style={styles.keyInfoLabel}>Recommendation</Text>
              <Text style={[styles.keyInfoValue, {
                color: application.aiInsights?.score >= 70 ? colors.success : application.aiInsights?.score >= 50 ? colors.warning : colors.danger,
                fontSize: 20
              }]}>
                {application.aiInsights?.score >= 70 ? 'RECOMMEND' : application.aiInsights?.score >= 50 ? 'REVIEW' : 'CAUTION'}
              </Text>
            </View>
          </View>
        </View>

        {/* Critical Factors */}
        {((application.aiInsights?.concerns && Array.isArray(application.aiInsights.concerns) && application.aiInsights.concerns.length > 0) ||
          (aiInsights?.concerns && Array.isArray(aiInsights.concerns) && aiInsights.concerns.length > 0)) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Critical Factors</Text>
            <View style={styles.card}>
              {(application.aiInsights?.concerns || aiInsights?.concerns || []).slice(0, 3).map((factor: string, index: number) => (
                <View key={index} style={{
                  backgroundColor: colors.warning + '10',
                  padding: 10,
                  borderRadius: 4,
                  marginBottom: 6,
                  flexDirection: 'row',
                  alignItems: 'flex-start'
                }}>
                  <Text style={{ fontSize: 10, color: colors.warning, marginRight: 8 }}>⚠</Text>
                  <Text style={{ fontSize: 10, color: colors.text, flex: 1 }}>{factor}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View style={styles.footer}>
          <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
          <Text style={styles.pageNumber}>Page 3</Text>
        </View>
      </Page>

      {/* Key Planning Information Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>KEY PLANNING INFORMATION</Text>
          <View style={styles.brandLogo}>
            <Text style={styles.logoText}>Planning Explorer</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Property Overview</Text>
          <View style={styles.card}>
            <Text style={{ fontSize: 14,  color: colors.primary, marginBottom: 10 }}>
              {application.address || 'N/A'}
            </Text>
            <View style={styles.keyInfoGrid}>
              <View style={styles.keyInfoItem}>
                <Text style={styles.keyInfoLabel}>Reference Number</Text>
                <Text style={styles.keyInfoValue}>{application.reference}</Text>
              </View>
              <View style={styles.keyInfoItem}>
                <Text style={styles.keyInfoLabel}>Application Type</Text>
                <Text style={styles.keyInfoValue}>{application.applicationType || application.app_type || application.application_type || 'N/A'}</Text>
              </View>
              <View style={styles.keyInfoItem}>
                <Text style={styles.keyInfoLabel}>Submission Date</Text>
                <Text style={styles.keyInfoValue}>{application.submissionDate ? formatDate(application.submissionDate) : application.start_date ? formatDate(application.start_date) : application.submission_date ? formatDate(application.submission_date) : 'N/A'}</Text>
              </View>
              <View style={styles.keyInfoItem}>
                <Text style={styles.keyInfoLabel}>Current Status</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(application.status) + '20' }]}>
                  <Text style={[styles.statusText, { color: getStatusColor(application.status) }]}>
                    {application.status}
                  </Text>
                </View>
              </View>
            </View>
          </View>
        </View>

        {/* AI Score Cards */}
        {(aiInsights || application.aiInsights) && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Intelligence Metrics</Text>
            <View style={styles.scoreCard}>
              <View style={styles.scoreItem}>
                <View style={[styles.scoreCircle, { backgroundColor: colors.accent }]}>
                  <Text style={styles.scoreValue}>{aiInsights?.score || application.aiInsights?.score || 0}</Text>
                </View>
                <Text style={styles.scoreLabel}>Opportunity{'\n'}Score</Text>
              </View>
              <View style={styles.scoreItem}>
                <View style={[styles.scoreCircle, { backgroundColor: colors.success }]}>
                  <Text style={styles.scoreValue}>{Math.round(aiInsights?.confidence || application.aiInsights?.confidence || 0)}%</Text>
                </View>
                <Text style={styles.scoreLabel}>Approval{'\n'}Probability</Text>
              </View>
              <View style={styles.scoreItem}>
                <View style={[styles.scoreCircle, { backgroundColor: colors.warning }]}>
                  <Text style={styles.scoreValue}>{Math.round((aiInsights?.confidence || application.aiInsights?.confidence || 85))}%</Text>
                </View>
                <Text style={styles.scoreLabel}>Confidence{'\n'}Level</Text>
              </View>
            </View>
          </View>
        )}

        {/* Location Map - Enhanced for PDF */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Property Location</Text>
          <View style={styles.mapContainer}>
            <Svg width="100%" height="200" viewBox="0 0 400 200">
              {/* Map background with grid pattern */}
              <Rect x="0" y="0" width="400" height="200" fill={colors.background} />

              {/* Grid lines for map feel */}
              <Line x1="100" y1="0" x2="100" y2="200" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />
              <Line x1="200" y1="0" x2="200" y2="200" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />
              <Line x1="300" y1="0" x2="300" y2="200" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />
              <Line x1="0" y1="50" x2="400" y2="50" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />
              <Line x1="0" y1="100" x2="400" y2="100" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />
              <Line x1="0" y1="150" x2="400" y2="150" stroke={colors.border} strokeWidth="0.5" opacity="0.3" />

              {/* Simplified road/area pattern */}
              <Path d="M50 100 L100 85 L150 95 L200 100 L250 105 L300 90 L350 100"
                stroke={colors.lightText} strokeWidth="2" fill="none" opacity="0.4" />
              <Path d="M200 20 L200 180"
                stroke={colors.lightText} strokeWidth="2" fill="none" opacity="0.4" />

              {/* Property marker - same as Leaflet style */}
              <G transform="translate(200, 100)">
                {/* Marker pin shape */}
                <Path
                  d="M0,-15 Q-8,-15 -8,-8 Q-8,0 0,8 Q8,0 8,-8 Q8,-15 0,-15 Z"
                  fill={colors.primary}
                  stroke={colors.white}
                  strokeWidth="1"
                />
                <Circle cx="0" cy="-8" r="3" fill={colors.white} />
              </G>

              {/* Label below marker */}
              <Text x="200" y="125" fontSize="9" fill={colors.primary} textAnchor="middle">
                {application.address ? application.address.substring(0, 40) + (application.address.length > 40 ? '...' : '') : 'Property Location'}
              </Text>
            </Svg>
          </View>

          {/* Location details */}
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 10, paddingHorizontal: 5 }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 2 }}>Ward</Text>
              <Text style={{ fontSize: 10, color: colors.text }}>{application.ward_name || application.ward || 'N/A'}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 2 }}>Postcode</Text>
              <Text style={{ fontSize: 10, color: colors.text }}>{application.postcode || 'N/A'}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 2 }}>Authority</Text>
              <Text style={{ fontSize: 10, color: colors.text }}>{application.localAuthority || application.area_name || application.authority || 'N/A'}</Text>
            </View>
          </View>

          {/* Coordinates if available */}
          {application.location && (application.location.lat || application.location.lon) && (
            <View style={{ marginTop: 8, paddingHorizontal: 5 }}>
              <Text style={{ fontSize: 8, color: colors.lightText }}>
                Coordinates: {application.location.lat?.toFixed(6) || 'N/A'}, {application.location.lon?.toFixed(6) || 'N/A'}
              </Text>
            </View>
          )}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
          <Text style={styles.pageNumber}>Page 4</Text>
        </View>
      </Page>

      {/* Application Details Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>APPLICATION DETAILS</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Development Description</Text>
          <View style={styles.cardHighlight}>
            <Text style={{ fontSize: 12, color: colors.text, lineHeight: 1.6 }}>
              {application.description || 'No description available'}
            </Text>
          </View>
        </View>

        {/* Key Dates Table */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Timeline</Text>
          <View style={styles.dataTable}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableHeaderText}>Event</Text>
              <Text style={styles.tableHeaderText}>Date</Text>
              <Text style={styles.tableHeaderText}>Status</Text>
            </View>
            <View style={styles.tableRow}>
              <Text style={styles.tableCell}>Application Submitted</Text>
              <Text style={styles.tableCell}>{application.submissionDate ? formatDate(application.submissionDate) : application.start_date ? formatDate(application.start_date) : application.submission_date ? formatDate(application.submission_date) : 'N/A'}</Text>
              <Text style={[styles.tableCell, { color: colors.success }]}>Completed</Text>
            </View>
            <View style={styles.tableRow}>
              <Text style={styles.tableCell}>Validation</Text>
              <Text style={styles.tableCell}>-</Text>
              <Text style={[styles.tableCell, { color: colors.success }]}>Passed</Text>
            </View>
            <View style={styles.tableRow}>
              <Text style={styles.tableCell}>Consultation Period</Text>
              <Text style={styles.tableCell}>-</Text>
              <Text style={[styles.tableCell, { color: colors.warning }]}>In Progress</Text>
            </View>
            {application.decisionDate && (
              <View style={styles.tableRow}>
                <Text style={styles.tableCell}>Decision Made</Text>
                <Text style={styles.tableCell}>{formatDate(application.decisionDate)}</Text>
                <Text style={[styles.tableCell, { color: colors.success }]}>Final</Text>
              </View>
            )}
          </View>

          {/* Applicant and Agent Information */}
          <View style={{ marginTop: 12, gap: 8 }}>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <Text style={{ fontSize: 10, color: colors.textLight, width: 100 }}>Applicant Name:</Text>
              <Text style={{ fontSize: 10, color: colors.text, flex: 1, fontWeight: 600 }}>
                {application.applicant_name || 'N/A'}
              </Text>
            </View>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <Text style={{ fontSize: 10, color: colors.textLight, width: 100 }}>Agent Name:</Text>
              <Text style={{ fontSize: 10, color: colors.text, flex: 1, fontWeight: 600 }}>
                {application.agent_name || 'N/A'}
              </Text>
            </View>
          </View>
        </View>

        {/* Planning Details Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Planning Details</Text>
          <View style={styles.card}>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 12 }}>
              <View style={{ width: '48%' }}>
                <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Ward</Text>
                <Text style={{ fontSize: 10, color: colors.text, fontWeight: 600 }}>
                  {application.ward_name || application.ward || 'N/A'}
                </Text>
              </View>
              <View style={{ width: '48%' }}>
                <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Decision Date</Text>
                <Text style={{ fontSize: 10, color: colors.text, fontWeight: 600 }}>
                  {application.decided_date ? formatDate(application.decided_date) : application.decisionDate ? formatDate(application.decisionDate) : 'N/A'}
                </Text>
              </View>
              <View style={{ width: '48%' }}>
                <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Number of Documents</Text>
                <Text style={{ fontSize: 10, color: colors.text, fontWeight: 600 }}>
                  {application.n_documents || 'N/A'}
                </Text>
              </View>
              <View style={{ width: '48%' }}>
                <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Statutory Days</Text>
                <Text style={{ fontSize: 10, color: colors.text, fontWeight: 600 }}>
                  {application.n_statutory_days || 'N/A'}
                </Text>
              </View>
              {application.url && (
                <View style={{ width: '48%' }}>
                  <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Website</Text>
                  <Link src={application.url} style={{ fontSize: 9, color: colors.info, textDecoration: 'underline' }}>
                    View Application
                  </Link>
                </View>
              )}
              {application.docs_url && (
                <View style={{ width: '48%' }}>
                  <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Documents URL</Text>
                  <Link src={application.docs_url} style={{ fontSize: 9, color: colors.info, textDecoration: 'underline' }}>
                    View Documents
                  </Link>
                </View>
              )}
            </View>
          </View>
        </View>

        {/* Property Features Grid */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Property Features</Text>
          <View style={styles.iconGrid}>
            <View style={styles.iconItem}>
              <View style={{ width: 40, height: 40, backgroundColor: colors.background, borderRadius: 20, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={{ fontSize: 20 }}>🏠</Text>
              </View>
              <Text style={styles.iconLabel}>Residential</Text>
            </View>
            <View style={styles.iconItem}>
              <View style={{ width: 40, height: 40, backgroundColor: colors.background, borderRadius: 20, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={{ fontSize: 20 }}>📏</Text>
              </View>
              <Text style={styles.iconLabel}>Extension</Text>
            </View>
            <View style={styles.iconItem}>
              <View style={{ width: 40, height: 40, backgroundColor: colors.background, borderRadius: 20, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={{ fontSize: 20 }}>🚗</Text>
              </View>
              <Text style={styles.iconLabel}>Parking</Text>
            </View>
            <View style={styles.iconItem}>
              <View style={{ width: 40, height: 40, backgroundColor: colors.background, borderRadius: 20, alignItems: 'center', justifyContent: 'center' }}>
                <Text style={{ fontSize: 20 }}>🌳</Text>
              </View>
              <Text style={styles.iconLabel}>Garden</Text>
            </View>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
          <Text style={styles.pageNumber}>Page 5</Text>
        </View>
      </Page>

      {/* AI Intelligence Analysis Page */}
      {(aiInsights || application.aiInsights) && (
        <Page size="A4" style={styles.contentPage}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>AI INTELLIGENCE ANALYSIS</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Predictive Analysis</Text>
            <View style={styles.insightCard}>
              <Text style={styles.insightTitle}>AI Prediction</Text>
              <Text style={styles.insightText}>
                {application.aiInsights?.predictedOutcome || 'Based on historical data and current trends, this application shows strong potential for approval with minor conditions.'}
              </Text>
            </View>
          </View>

          {/* Opportunities */}
          {((application.aiInsights?.opportunities && Array.isArray(application.aiInsights.opportunities) && application.aiInsights.opportunities.length > 0) ||
            (aiInsights?.opportunities && Array.isArray(aiInsights.opportunities) && aiInsights.opportunities.length > 0)) && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Identified Opportunities</Text>
              <View style={styles.card}>
                {(application.aiInsights?.opportunities || aiInsights?.opportunities || []).map((opp: string, index: number) => (
                  <View key={index} style={styles.bulletPoint}>
                    <View style={styles.bullet} />
                    <Text style={styles.bulletText}>{opp || 'N/A'}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* Risk Assessment Chart */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Risk Assessment</Text>
            <View style={styles.chartContainer}>
              <Svg width="100%" height="150" viewBox="0 0 300 150">
                {/* Risk level bars */}
                <Rect x="50" y="30" width="200" height="20" fill={colors.border} rx="10" />
                <Rect x="50" y="30" width={`${(application.aiInsights?.score || 75) * 2}`} height="20" fill={colors.secondary} rx="10" />

                <Text x="50" y="20" fontSize="10" fill={colors.text}>Overall Risk Score</Text>
                <Text x="250" y="20" fontSize="12" fill={colors.primary}>
                  {application.aiInsights?.riskLevel || 'Medium'}
                </Text>

                {/* Individual risk factors */}
                <Text x="50" y="80" fontSize="9" fill={colors.lightText}>Market Risk</Text>
                <Rect x="120" y="70" width="130" height="10" fill={colors.border} rx="5" />
                <Rect x="120" y="70" width="80" height="10" fill={colors.success} rx="5" />

                <Text x="50" y="100" fontSize="9" fill={colors.lightText}>Planning Risk</Text>
                <Rect x="120" y="90" width="130" height="10" fill={colors.border} rx="5" />
                <Rect x="120" y="90" width="60" height="10" fill={colors.warning} rx="5" />

                <Text x="50" y="120" fontSize="9" fill={colors.lightText}>Financial Risk</Text>
                <Rect x="120" y="110" width="130" height="10" fill={colors.border} rx="5" />
                <Rect x="120" y="110" width="100" height="10" fill={colors.success} rx="5" />
              </Svg>
            </View>
          </View>

          {/* Concerns */}
          {((application.aiInsights?.concerns && Array.isArray(application.aiInsights.concerns) && application.aiInsights.concerns.length > 0) ||
            (aiInsights?.concerns && Array.isArray(aiInsights.concerns) && aiInsights.concerns.length > 0)) && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Areas of Attention</Text>
              <View style={[styles.card, { borderLeft: `3px solid ${colors.warning}` }]}>
                {(application.aiInsights?.concerns || aiInsights?.concerns || []).map((concern: string, index: number) => (
                  <View key={index} style={styles.bulletPoint}>
                    <View style={[styles.bullet, { backgroundColor: colors.warning }]} />
                    <Text style={styles.bulletText}>{concern || 'N/A'}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          <View style={styles.footer}>
            <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
            <Text style={styles.pageNumber}>Page 6</Text>
          </View>
        </Page>
      )}

      {/* Market Insights Page */}
      {marketInsights && Object.keys(marketInsights).length > 0 && (
        <Page size="A4" style={styles.contentPage}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>MARKET INSIGHTS</Text>
          </View>

          {/* Market Statistics Grid */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Market Performance Analysis</Text>
            <View style={styles.chartContainer}>
              <Text style={styles.chartTitle}>Planning Application Volume Trends (Last 12 Months)</Text>
              <Svg width="100%" height="200" viewBox="0 0 400 200">
                {/* Horizontal grid lines - matching web style */}
                {[0, 25, 50, 75, 100].map((val, i) => (
                  <Line key={i} x1="60" y1={160 - val * 1.2} x2="350" y2={160 - val * 1.2}
                    stroke={colors.border} strokeWidth="0.5" strokeDasharray="3,3" />
                ))}

                {/* Y-axis - lighter color matching web */}
                <Line x1="60" y1="40" x2="60" y2="160" stroke={colors.border} strokeWidth="1" />
                {/* X-axis - lighter color matching web */}
                <Line x1="60" y1="160" x2="350" y2="160" stroke={colors.border} strokeWidth="1" />

                {/* Bar chart with solid colors (no gradients for better print) */}
                {[85, 62, 94, 71, 83, 78, 100, 58, 89, 76, 64, 69].map((height, index) => (
                  <G key={index}>
                    <Rect
                      x={70 + index * 22}
                      y={160 - height * 1.2}
                      width="18"
                      height={height * 1.2}
                      fill={index === 6 ? colors.danger : colors.primary}
                      opacity={index === 6 ? 1 : 0.9}
                      rx="4"
                    />
                    {/* Data labels removed for cleaner look matching web */}
                    {/* Month labels */}
                    <Text
                      x={79 + index * 22}
                      y="175"
                      fontSize="9"
                      fill={colors.lightText}
                      textAnchor="middle"
                    >
                      {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][index]}
                    </Text>
                  </G>
                ))}

                {/* Y-axis labels */}
                {[0, 25, 50, 75, 100].map((val, i) => (
                  <Text key={i} x="50" y={165 - val * 1.2} fontSize="9" fill={colors.text} textAnchor="end">{val}</Text>
                ))}

                {/* Chart title and legend */}
                <Text x="60" y="25" fontSize="10" fill={colors.primary} >Applications Submitted</Text>
                <Circle cx="270" cy="25" r="4" fill={colors.secondary} />
                <Text x="280" y="28" fontSize="8" fill={colors.text}>Approved</Text>
                <Circle cx="320" cy="25" r="4" fill={colors.danger} />
                <Text x="330" y="28" fontSize="8" fill={colors.text}>Peak Month</Text>
              </Svg>
            </View>
          </View>

          {/* Market Statistics Cards */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Key Market Statistics</Text>
            <View style={{ flexDirection: 'row', gap: 15 }}>
              <View style={[styles.keyInfoItem, { flex: 1 }]}>
                <Text style={styles.keyInfoLabel}>Average Approval Rate</Text>
                <Text style={[styles.keyInfoValue, { color: colors.success, fontSize: 24 }]}>78%</Text>
                <Text style={styles.keyInfoSubvalue}>↑ 5% from last year</Text>
              </View>
              <View style={[styles.keyInfoItem, { flex: 1 }]}>
                <Text style={styles.keyInfoLabel}>Average Decision Time</Text>
                <Text style={[styles.keyInfoValue, { color: colors.warning, fontSize: 24 }]}>56 days</Text>
                <Text style={styles.keyInfoSubvalue}>↓ 8 days improvement</Text>
              </View>
              <View style={[styles.keyInfoItem, { flex: 1 }]}>
                <Text style={styles.keyInfoLabel}>Total Applications (YTD)</Text>
                <Text style={[styles.keyInfoValue, { color: colors.info, fontSize: 24 }]}>2,847</Text>
                <Text style={styles.keyInfoSubvalue}>+12% vs last year</Text>
              </View>
            </View>
          </View>

          {/* Comparable Applications Analysis */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Comparable Applications in Area</Text>

            {/* Success Rate Donut Chart */}
            <View style={styles.chartContainer}>
              <Text style={styles.chartTitle}>Local Authority Performance</Text>
              <Svg width="100%" height="180" viewBox="0 0 300 180">
                {/* Donut chart segments */}
                <G transform="translate(80, 90)">
                  {/* Approved segment (78%) */}
                  <Path
                    d="M 0,-50 A 50,50 0 1,1 -15.45,47.02 L -9.27,28.21 A 30,30 0 1,0 0,-30 Z"
                    fill={colors.success}
                  />
                  {/* Rejected segment (12%) */}
                  <Path
                    d="M -15.45,47.02 A 50,50 0 0,1 -47.02,-15.45 L -28.21,-9.27 A 30,30 0 0,0 -9.27,28.21 Z"
                    fill={colors.danger}
                  />
                  {/* Pending segment (10%) */}
                  <Path
                    d="M -47.02,-15.45 A 50,50 0 0,1 0,-50 L 0,-30 A 30,30 0 0,0 -28.21,-9.27 Z"
                    fill={colors.warning}
                  />

                  {/* Center text */}
                  <Text x="0" y="-5" fontSize="20"  fill={colors.primary} textAnchor="middle">78%</Text>
                  <Text x="0" y="10" fontSize="10" fill={colors.text} textAnchor="middle">Approval Rate</Text>
                </G>

                {/* Legend */}
                <G transform="translate(180, 50)">
                  <Circle cx="0" cy="0" r="6" fill={colors.success} />
                  <Text x="15" y="4" fontSize="10" fill={colors.text}>Approved (78%)</Text>

                  <Circle cx="0" cy="25" r="6" fill={colors.danger} />
                  <Text x="15" y="29" fontSize="10" fill={colors.text}>Rejected (12%)</Text>

                  <Circle cx="0" cy="50" r="6" fill={colors.warning} />
                  <Text x="15" y="54" fontSize="10" fill={colors.text}>Pending (10%)</Text>
                </G>
              </Svg>
            </View>

            {/* Comparable Applications Table */}
            <View style={styles.dataTable}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableHeaderText}>Reference</Text>
                <Text style={styles.tableHeaderText}>Description</Text>
                <Text style={styles.tableHeaderText}>Status</Text>
                <Text style={styles.tableHeaderText}>Decision Date</Text>
              </View>

              <View style={styles.tableRow}>
                <Text style={styles.tableCell}>APP/2024/1247</Text>
                <Text style={styles.tableCell}>Two storey extension</Text>
                <Text style={[styles.tableCell, { color: colors.success,  }]}>Approved</Text>
                <Text style={styles.tableCell}>15-Mar-2024</Text>
              </View>

              <View style={styles.tableRow}>
                <Text style={styles.tableCell}>APP/2024/0983</Text>
                <Text style={styles.tableCell}>Single storey rear extension</Text>
                <Text style={[styles.tableCell, { color: colors.success,  }]}>Approved</Text>
                <Text style={styles.tableCell}>08-Feb-2024</Text>
              </View>

              <View style={styles.tableRow}>
                <Text style={styles.tableCell}>APP/2024/1156</Text>
                <Text style={styles.tableCell}>Loft conversion with dormer</Text>
                <Text style={[styles.tableCell, { color: colors.warning,  }]}>Pending</Text>
                <Text style={styles.tableCell}>-</Text>
              </View>

              <View style={styles.tableRow}>
                <Text style={styles.tableCell}>APP/2023/2891</Text>
                <Text style={styles.tableCell}>Garden outbuilding</Text>
                <Text style={[styles.tableCell, { color: colors.danger,  }]}>Rejected</Text>
                <Text style={styles.tableCell}>12-Jan-2024</Text>
              </View>
            </View>

            {/* Decision Timeline Chart - Aligned with web version */}
            <View style={{ marginTop: 20 }}>
              <Text style={styles.chartTitle}>Average Decision Timeline by Application Type</Text>
              <Svg width="100%" height="140" viewBox="0 0 350 140">
                {/* Grid lines - subtle vertical guides */}
                {[0, 25, 50, 75, 90].map((tick, i) => {
                  const x = 90 + (tick / 90) * 230
                  return (
                    <Line
                      key={`grid-${i}`}
                      x1={x}
                      y1="10"
                      x2={x}
                      y2="115"
                      stroke={colors.border}
                      strokeWidth="0.5"
                      strokeDasharray="3,3"
                      opacity="0.4"
                    />
                  )
                })}

                {/* X-axis */}
                <Line x1="90" y1="115" x2="320" y2="115" stroke={colors.border} strokeWidth="1" />

                {/* X-axis labels */}
                {[0, 25, 50, 75, 90].map((tick, i) => {
                  const x = 90 + (tick / 90) * 230
                  return (
                    <Text
                      key={`tick-${i}`}
                      x={x}
                      y="128"
                      fontSize="9"
                      fill={colors.lightText}
                      textAnchor="middle"
                    >
                      {tick}
                    </Text>
                  )
                })}

                {/* X-axis label */}
                <Text x="205" y="140" fontSize="9" fill={colors.lightText} textAnchor="middle">
                  Average Days
                </Text>

                {/* Bars */}
                {['Householder', 'Full Planning', 'Listed Building', 'Prior Approval'].map((type, index) => {
                  const days = [42, 78, 65, 28][index]
                  const maxDays = 90
                  const barWidth = (days / maxDays) * 230
                  const yPos = index * 23 + 15

                  return (
                    <G key={index}>
                      {/* Bar with gradient opacity for visual hierarchy */}
                      <Rect
                        x="90"
                        y={yPos}
                        width={barWidth}
                        height="16"
                        fill={colors.primary}
                        opacity={0.85 + (index * 0.05)}
                        rx="0"
                        ry="4"
                      />
                      {/* Type label */}
                      <Text x="85" y={yPos + 11} fontSize="10" fill={colors.text} textAnchor="end">{type}</Text>
                      {/* Days label */}
                      <Text x={95 + barWidth} y={yPos + 11} fontSize="9" fill={colors.primary}>
                        {days} days
                      </Text>
                    </G>
                  )
                })}
              </Svg>

              {/* Info note matching web */}
              <Text style={{ fontSize: 8, color: colors.lightText, marginTop: 6 }}>
                Average processing times based on historical data. Actual timelines may vary by authority.
              </Text>
            </View>
          </View>

          {/* Authority Performance */}
          {marketInsights?.authority_performance && Object.keys(marketInsights.authority_performance).length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Authority Performance Metrics</Text>
              <View style={{ flexDirection: 'row', gap: 10 }}>
                <View style={[styles.keyInfoItem, { flex: 1 }]}>
                  <Text style={styles.keyInfoLabel}>Approval Rate</Text>
                  <Text style={[styles.keyInfoValue, { color: colors.success }]}>
                    {typeof marketInsights.authority_performance.approval_rate === 'number'
                      ? `${Math.round(marketInsights.authority_performance.approval_rate * 100)}%`
                      : marketInsights.authority_performance.approval_rate || '78%'}
                  </Text>
                </View>
                <View style={[styles.keyInfoItem, { flex: 1 }]}>
                  <Text style={styles.keyInfoLabel}>Avg Decision Time</Text>
                  <Text style={[styles.keyInfoValue, { color: colors.warning }]}>
                    {typeof marketInsights.authority_performance.avg_decision_time === 'number'
                      ? `${marketInsights.authority_performance.avg_decision_time} days`
                      : marketInsights.authority_performance.avg_decision_time || '45 days'}
                  </Text>
                </View>
                <View style={[styles.keyInfoItem, { flex: 1 }]}>
                  <Text style={styles.keyInfoLabel}>Total Applications</Text>
                  <Text style={[styles.keyInfoValue, { color: colors.info }]}>
                    {marketInsights.authority_performance.total_applications?.toLocaleString() || '2,847'}
                  </Text>
                </View>
              </View>
            </View>
          )}

          <View style={styles.footer}>
            <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
            <Text style={styles.pageNumber}>Page 7</Text>
          </View>
        </Page>
      )}

      {/* Documents & Appendix Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>DOCUMENTS & APPENDIX</Text>
        </View>

        {application.documents && application.documents.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Associated Documents</Text>
            <View style={styles.dataTable}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableHeaderText}>Document Name</Text>
                <Text style={styles.tableHeaderText}>Type</Text>
                <Text style={styles.tableHeaderText}>Status</Text>
              </View>
              {application.documents.map((doc: any, index: number) => (
                <View key={index} style={styles.tableRow}>
                  <Text style={styles.tableCell}>{doc.name}</Text>
                  <Text style={styles.tableCell}>{doc.type}</Text>
                  <Text style={[styles.tableCell, { color: colors.success }]}>Available</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Report Information</Text>
          <View style={styles.card}>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 15 }}>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: 'row', marginBottom: 8 }}>
                  <Text style={{ fontSize: 10, color: colors.lightText, width: 120 }}>Report Generated:</Text>
                  <Text style={{ fontSize: 10, color: colors.text,  }}>{formatDate(new Date().toISOString())}</Text>
                </View>
                <View style={{ flexDirection: 'row', marginBottom: 8 }}>
                  <Text style={{ fontSize: 10, color: colors.lightText, width: 120 }}>Report ID:</Text>
                  <Text style={{ fontSize: 10, color: colors.text,  }}>{application.reference || 'N/A'}</Text>
                </View>
                <View style={{ flexDirection: 'row', marginBottom: 8 }}>
                  <Text style={{ fontSize: 10, color: colors.lightText, width: 120 }}>Data Sources:</Text>
                  <Text style={{ fontSize: 10, color: colors.text }}>UK Planning Portal, AI Analysis Engine</Text>
                </View>
                <View style={{ flexDirection: 'row' }}>
                  <Text style={{ fontSize: 10, color: colors.lightText, width: 120 }}>Validity:</Text>
                  <Text style={{ fontSize: 10, color: colors.text }}>30 days from generation date</Text>
                </View>
              </View>

              {/* QR Code */}
              <View style={{ alignItems: 'center', marginLeft: 20 }}>
                <View style={[styles.qrCode, { width: 60, height: 60 }]}>
                  <Svg width="60" height="60" viewBox="0 0 100 100">
                    {/* Enhanced QR code pattern */}
                    <Rect x="10" y="10" width="15" height="15" fill={colors.primary} />
                    <Rect x="30" y="10" width="5" height="5" fill={colors.primary} />
                    <Rect x="40" y="10" width="5" height="5" fill={colors.primary} />
                    <Rect x="50" y="10" width="10" height="10" fill={colors.primary} />
                    <Rect x="70" y="10" width="15" height="15" fill={colors.primary} />

                    <Rect x="10" y="30" width="5" height="5" fill={colors.primary} />
                    <Rect x="20" y="30" width="5" height="5" fill={colors.primary} />
                    <Rect x="35" y="30" width="15" height="5" fill={colors.primary} />
                    <Rect x="55" y="30" width="5" height="5" fill={colors.primary} />
                    <Rect x="70" y="30" width="5" height="5" fill={colors.primary} />
                    <Rect x="80" y="30" width="5" height="5" fill={colors.primary} />

                    <Rect x="10" y="40" width="10" height="10" fill={colors.primary} />
                    <Rect x="25" y="45" width="15" height="5" fill={colors.primary} />
                    <Rect x="45" y="40" width="10" height="10" fill={colors.primary} />
                    <Rect x="70" y="40" width="5" height="5" fill={colors.primary} />
                    <Rect x="80" y="45" width="5" height="5" fill={colors.primary} />

                    <Rect x="10" y="55" width="5" height="5" fill={colors.primary} />
                    <Rect x="25" y="55" width="5" height="5" fill={colors.primary} />
                    <Rect x="35" y="60" width="10" height="5" fill={colors.primary} />
                    <Rect x="50" y="55" width="5" height="10" fill={colors.primary} />
                    <Rect x="70" y="60" width="15" height="5" fill={colors.primary} />

                    <Rect x="10" y="70" width="15" height="15" fill={colors.primary} />
                    <Rect x="30" y="75" width="10" height="5" fill={colors.primary} />
                    <Rect x="45" y="70" width="5" height="5" fill={colors.primary} />
                    <Rect x="55" y="80" width="10" height="5" fill={colors.primary} />
                    <Rect x="70" y="70" width="15" height="15" fill={colors.primary} />
                  </Svg>
                </View>
                <Text style={{ fontSize: 7, color: colors.lightText, marginTop: 5, textAlign: 'center' }}>Scan for{' \n'}digital version</Text>
              </View>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Disclaimer</Text>
          <View style={[styles.card, { backgroundColor: colors.background }]}>
            <Text style={{ fontSize: 9, color: colors.lightText, lineHeight: 1.4 }}>
              This report is generated by Planning Explorer's AI Intelligence System and is provided for informational purposes only.
              While we strive for accuracy, the information should be independently verified before making any decisions.
              Planning Explorer accepts no liability for any errors or omissions in this report.
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact Information</Text>
          <View style={styles.card}>
            <Text style={{ fontSize: 12,  color: colors.primary, marginBottom: 10 }}>
              Planning Explorer
            </Text>
            <Text style={{ fontSize: 10, color: colors.text, marginBottom: 4 }}>
              Email: reports@planningexplorer.com
            </Text>
            <Text style={{ fontSize: 10, color: colors.text, marginBottom: 4 }}>
              Phone: 0800 123 4567
            </Text>
            <Text style={{ fontSize: 10, color: colors.text }}>
              Web: www.planningexplorer.com
            </Text>
          </View>
        </View>

        {/* Planning Explorer Branding Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About Planning Explorer</Text>
          <View style={[styles.card, { backgroundColor: `${colors.secondary}10`, borderLeft: `4px solid ${colors.secondary}` }]}>
            <Text style={{ fontSize: 12,  color: colors.primary, marginBottom: 8 }}>Your AI-Powered Planning Intelligence Partner</Text>
            <Text style={{ fontSize: 10, color: colors.text, lineHeight: 1.5, marginBottom: 10 }}>Planning Explorer revolutionises property intelligence by transforming weeks of manual research into minutes of AI-powered insights. We provide comprehensive UK planning data that's accessible, actionable, and intelligent for every property professional.</Text>

            <View style={{ flexDirection: 'row', gap: 30, marginTop: 10 }}>
              <View>
                <Text style={{ fontSize: 14,  color: colors.secondary, marginBottom: 2 }}>336K+</Text>
                <Text style={{ fontSize: 9, color: colors.text }}>Applications Tracked</Text>
              </View>
              <View>
                <Text style={{ fontSize: 14,  color: colors.secondary, marginBottom: 2 }}>321K+</Text>
                <Text style={{ fontSize: 9, color: colors.text }}>Councils Covered</Text>
              </View>
              <View>
                <Text style={{ fontSize: 14,  color: colors.secondary, marginBottom: 2 }}>85%+</Text>
                <Text style={{ fontSize: 9, color: colors.text }}>Prediction Accuracy</Text>
              </View>
              <View>
                <Text style={{ fontSize: 14,  color: colors.secondary, marginBottom: 2 }}>98%</Text>
                <Text style={{ fontSize: 9, color: colors.text }}>Customer Satisfaction</Text>
              </View>
            </View>
          </View>
        </View>

        <View style={[styles.footer, { borderTop: `3px solid ${colors.secondary}`, paddingTop: 15 }]}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '100%' }}>
            <Text style={styles.footerText}>© 2024 Planning Explorer. All rights reserved.</Text>
            <Text style={styles.footerText}>AI-Generated Report | Confidence Level: {application.aiInsights?.confidence || 95}%</Text>
            <Text style={styles.pageNumber}>Page 8</Text>
          </View>
        </View>
      </Page>

      {/* Comparable Applications Analysis Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>COMPARABLE APPLICATIONS ANALYSIS</Text>
          <View style={styles.brandLogo}>
            <Text style={styles.logoText}>Planning Explorer</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Similar Applications in the Area</Text>
          <Text style={{ fontSize: 10, color: colors.lightText, marginBottom: 15 }}>
            Analysis of similar planning applications within a 1-mile radius, providing context for decision-making patterns.
          </Text>

          <View style={styles.dataTable}>
            <View style={styles.tableHeader}>
              <Text style={[styles.tableHeaderText, { flex: 1.2 }]}>Reference</Text>
              <Text style={[styles.tableHeaderText, { flex: 2 }]}>Description</Text>
              <Text style={[styles.tableHeaderText, { flex: 1 }]}>Value</Text>
              <Text style={[styles.tableHeaderText, { flex: 1 }]}>Status</Text>
              <Text style={[styles.tableHeaderText, { flex: 1.2 }]}>Decision Date</Text>
            </View>

            <View style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>APP/2024/2156</Text>
              <Text style={[styles.tableCell, { flex: 2 }]}>25 Bank Street - Commercial Tower</Text>
              <Text style={[styles.tableCell, { flex: 1 }]}>£324M</Text>
              <Text style={[styles.tableCell, { flex: 1, color: colors.success }]}>Approved</Text>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>12-Aug-2024</Text>
            </View>

            <View style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>APP/2023/4789</Text>
              <Text style={[styles.tableCell, { flex: 2 }]}>Wood Wharf Phase 2</Text>
              <Text style={[styles.tableCell, { flex: 1 }]}>£567M</Text>
              <Text style={[styles.tableCell, { flex: 1, color: colors.success }]}>Approved</Text>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>23-Nov-2023</Text>
            </View>

            <View style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>APP/2024/1033</Text>
              <Text style={[styles.tableCell, { flex: 2 }]}>Landmark Pinnacle Extension</Text>
              <Text style={[styles.tableCell, { flex: 1 }]}>£189M</Text>
              <Text style={[styles.tableCell, { flex: 1, color: colors.warning }]}>Pending</Text>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>-</Text>
            </View>

            <View style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>APP/2023/8901</Text>
              <Text style={[styles.tableCell, { flex: 2 }]}>South Quay Plaza</Text>
              <Text style={[styles.tableCell, { flex: 1 }]}>£425M</Text>
              <Text style={[styles.tableCell, { flex: 1, color: colors.success }]}>Approved</Text>
              <Text style={[styles.tableCell, { flex: 1.2 }]}>07-Mar-2024</Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Key Insights from Comparable Applications</Text>
          <View style={styles.card}>
            <View style={{ flexDirection: 'row', gap: 10, marginBottom: 10 }}>
              <View style={{ width: 4, backgroundColor: colors.success, borderRadius: 2 }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 11,  color: colors.text, marginBottom: 4 }}>Approval Rate</Text>
                <Text style={{ fontSize: 9, color: colors.lightText, lineHeight: 1.4 }}>
                  75% of similar residential applications in this area have been approved within the last 12 months.
                </Text>
              </View>
            </View>

            <View style={{ flexDirection: 'row', gap: 10, marginBottom: 10 }}>
              <View style={{ width: 4, backgroundColor: colors.secondary, borderRadius: 2 }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 11,  color: colors.text, marginBottom: 4 }}>Average Timeline</Text>
                <Text style={{ fontSize: 9, color: colors.lightText, lineHeight: 1.4 }}>
                  Typical decision period for comparable applications is 12-14 weeks from validation.
                </Text>
              </View>
            </View>

            <View style={{ flexDirection: 'row', gap: 10 }}>
              <View style={{ width: 4, backgroundColor: colors.primary, borderRadius: 2 }} />
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 11,  color: colors.text, marginBottom: 4 }}>Common Requirements</Text>
                <Text style={{ fontSize: 9, color: colors.lightText, lineHeight: 1.4 }}>
                  Most approved applications included robust community engagement strategies and addressed local planning policy requirements.
                </Text>
              </View>
            </View>
          </View>
        </View>

        <View style={styles.footer}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '100%' }}>
            <Text style={styles.footerText}>© 2024 Planning Explorer. All rights reserved.</Text>
            <Text style={styles.footerText}>AI-Generated Report | Confidence Level: {application.aiInsights?.confidence || 95}%</Text>
            <Text style={styles.pageNumber}>Page 9</Text>
          </View>
        </View>
      </Page>

      {/* Market Recommendations Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>MARKET RECOMMENDATIONS</Text>
          <View style={styles.brandLogo}>
            <Text style={styles.logoText}>Planning Explorer</Text>
          </View>
        </View>

        <View style={styles.section}>
          {/* Strategic Timing Card - Matching Web Exactly */}
          <View style={[styles.card, { backgroundColor: colors.background, marginBottom: 15 }]}>
            <Text style={{ fontSize: 12,  color: colors.text, marginBottom: 8 }}>Strategic Timing</Text>
            <Text style={{ fontSize: 11, color: colors.text, lineHeight: 1.6 }}>
              Submit before Q2 2025 to benefit from current favorable policy environment and avoid potential regulatory changes.
            </Text>
          </View>

          {/* Community Engagement Card - Matching Web Exactly */}
          <View style={[styles.card, { backgroundColor: colors.background, marginBottom: 15 }]}>
            <Text style={{ fontSize: 12,  color: colors.text, marginBottom: 8 }}>Community Engagement</Text>
            <Text style={{ fontSize: 11, color: colors.text, lineHeight: 1.6 }}>
              Proactive consultation with local groups has shown 73% higher approval rates for similar scale developments.
            </Text>
          </View>

          {/* Risk Mitigation Card - Matching Web Exactly */}
          <View style={[styles.card, { backgroundColor: colors.background, marginBottom: 15 }]}>
            <Text style={{ fontSize: 12,  color: colors.text, marginBottom: 8 }}>Risk Mitigation</Text>
            <Text style={{ fontSize: 11, color: colors.text, lineHeight: 1.6 }}>
              Consider pre-application advice and environmental impact assessment to address potential concerns early.
            </Text>
          </View>
        </View>

        <View style={styles.footer}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', width: '100%' }}>
            <Text style={styles.footerText}>© 2024 Planning Explorer. All rights reserved.</Text>
            <Text style={styles.footerText}>AI-Generated Report | Confidence Level: {application.aiInsights?.confidence || 95}%</Text>
            <Text style={styles.pageNumber}>Page 10</Text>
          </View>
        </View>
      </Page>

      {/* Project Timeline & Milestones Page */}
      <Page size="A4" style={styles.contentPage}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>PROJECT TIMELINE & MILESTONES</Text>
        </View>

        <View style={styles.section}>
          <Text style={{ fontSize: 10, color: colors.lightText, marginBottom: 20 }}>
            Track the progress of this planning application through key development milestones and expected completion dates.
          </Text>

          {/* Vertical Timeline - Matching Web Layout */}

          {/* Milestone 1: Application Submitted - Completed */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
            {/* Icon Circle with Checkmark SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.success,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M5 13l4 4L19 7" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>Application Submitted</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>15-Mar-2024 • Documentation and initial submission completed</Text>
              <View style={{
                backgroundColor: `${colors.success}20`,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.success }}>✓ Completed</Text>
              </View>
            </View>
          </View>

          {/* Milestone 2: Validation & Initial Review - Completed */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
            {/* Icon Circle with Checkmark SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.success,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M5 13l4 4L19 7" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>Validation & Initial Review</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>22-Mar-2024 • Technical validation and compliance check (7 days)</Text>
              <View style={{
                backgroundColor: `${colors.success}20`,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.success }}>✓ Completed</Text>
              </View>
            </View>
          </View>

          {/* Milestone 3: Public Consultation Period - Completed */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
            {/* Icon Circle with Checkmark SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.success,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M5 13l4 4L19 7" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>Public Consultation Period</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>05-Apr-2024 • Community engagement and feedback collection (21 days)</Text>
              <View style={{
                backgroundColor: `${colors.success}20`,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.success }}>✓ Completed</Text>
              </View>
            </View>
          </View>

          {/* Milestone 4: Committee Review & Decision - Approved */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
            {/* Icon Circle with Checkmark SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.success,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M5 13l4 4L19 7" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>Committee Review & Decision</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>18-Jun-2024 • Final assessment and approval decision (89 days total)</Text>
              <View style={{
                backgroundColor: `${colors.success}20`,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.success }}>✓ Approved</Text>
              </View>
            </View>
          </View>

          {/* Milestone 5: S106 Agreement Completion - In Progress */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 20 }}>
            {/* Icon Circle with Spinner SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.info,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>S106 Agreement Completion</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Expected: 15-Oct-2024 • Legal agreements and community obligations</Text>
              <View style={{
                backgroundColor: `${colors.info}20`,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.info }}>⏳ In Progress</Text>
              </View>
            </View>
          </View>

          {/* Milestone 6: Planning Permission Issued - Pending */}
          <View style={{ flexDirection: 'row', alignItems: 'flex-start', gap: 12 }}>
            {/* Icon Circle with Clock SVG */}
            <View style={{
              width: 48,
              height: 48,
              borderRadius: 24,
              backgroundColor: colors.border,
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <Svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={colors.white} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <Path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </Svg>
            </View>
            {/* Content */}
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 10,  color: colors.text, marginBottom: 6 }}>Planning Permission Issued</Text>
              <Text style={{ fontSize: 9, color: colors.lightText, marginBottom: 4 }}>Expected: 30-Oct-2024 • Final permission documentation and commencement</Text>
              <View style={{
                backgroundColor: colors.background,
                paddingHorizontal: 6,
                paddingVertical: 3,
                borderRadius: 4,
                alignSelf: 'flex-start'
              }}>
                <Text style={{ fontSize: 8, color: colors.lightText }}>◦ Pending</Text>
              </View>
            </View>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Planning Explorer - AI Property Intelligence</Text>
          <Text style={styles.pageNumber}>Page 11</Text>
        </View>
      </Page>
    </Document>
  )
}