# PDF Generation Implementation

## Overview
This directory contains the PDF generation functionality for Planning Explorer reports using React-PDF library.

## Files
- `PlanningReportPDF.tsx` - React component that defines the PDF document structure and styling
- `../lib/pdf-utils.ts` - Utility functions for PDF generation, download, and preview

## Usage

### Basic PDF Download
```typescript
import { downloadPlanningReportPDF } from '@/lib/pdf-utils'

await downloadPlanningReportPDF({
  application,
  aiInsights,
  marketInsights,
  filename: 'custom-filename.pdf' // optional
})
```

### Generate PDF Blob
```typescript
import { generatePDFBlob } from '@/lib/pdf-utils'

const blob = await generatePDFBlob({
  application,
  aiInsights,
  marketInsights
})
```

### Preview PDF
```typescript
import { previewPDF } from '@/lib/pdf-utils'

const url = await previewPDF({
  application,
  aiInsights,
  marketInsights
})
// Use URL.revokeObjectURL(url) when done
```

## Features
- Professional report layout with Planning Explorer branding
- Comprehensive sections including:
  - Application details
  - AI intelligence analysis
  - Market insights
  - Associated documents
- Proper error handling and loading states
- Auto-generated filename with date and reference
- Responsive design optimized for A4 paper size

## Dependencies
- `@react-pdf/renderer` - PDF generation library
- `react-pdf` - Additional React PDF utilities

## Error Handling
The implementation includes comprehensive error handling with user-friendly error messages and automatic error dismissal after 10 seconds.

## Performance
- Client-side PDF generation
- Optimized styles for fast rendering
- Memory cleanup after download