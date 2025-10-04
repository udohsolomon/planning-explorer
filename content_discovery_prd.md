
---

# 📄 PRD – Content & Discovery Pages

**Product Name:** Planning Explorer
**Feature Set:** Content & Discovery Pages
**Version:** v1.0 (Expansion Scope)
**Owner:** [Your Company / Product Owner]
**Date:** 2025-10-01

---

## 1. Overview

### 1.1 Purpose

To build out **discovery-oriented landing pages** that showcase planning applications by **authority**, **location**, and **sector**, as well as an **Insights Hub** with dynamic dashboards. These pages serve dual purposes:

* **SEO Growth** → Drive organic traffic by targeting long-tail queries like “Planning Applications in Milton Keynes 2025.”
* **User Discovery** → Help users explore data without needing complex searches.
* **Brand Authority** → Position Planning Explorer as the trusted source of planning intelligence.

---

## 2. Feature Breakdown

### 2.1 Authority Pages (“Planning Applications in [Council Name]”)

**Purpose:** Show authority-specific planning stats & applications.

**Core Features:**

* Hero header: *“Planning Applications in [Authority Name]”*.
* **Key Stats Panel**:

  * Total applications (last 12 months, all-time).
  * Approval rate.
  * Average decision time.
* **Filters:** Date range, status, use class.
* **Application List:** Paginated, sortable, same format as core search.
* **Charts:**

  * Monthly trend of applications.
  * Approval vs refusal pie chart.
* **SEO Enhancements:**

  * Static metadata (title/description tags).
  * Schema.org structured data for SEO.
  * Internal linking to location & sector pages.

---

### 2.2 Location Pages (“Planning Applications in [City/Town/Postcode]”)

**Purpose:** Hyper-local discovery pages for towns, cities, and postcodes.

**Core Features:**

* Hero header: *“Planning Applications in [Location]”*.
* **Map View:** Interactive Mapbox map of applications in boundary.
* **Key Stats:**

  * Total applications this year.
  * Most common sectors/use classes.
  * Average council decision time (local authority overlap).
* **Filters:** Sector, application type, status.
* **Charts:**

  * Monthly trend of new applications in that area.
  * Heatmap of activity (if boundaries available).
* **SEO Enhancements:**

  * URL structure: `/planning-applications/[location-slug]`.
  * Dynamic meta titles/descriptions.
  * Breadcrumb navigation (Home → Location → Application).

---

### 2.3 Sector / Use Class Pages

**Purpose:** Category-specific pages targeting industries and suppliers.

**Examples:**

* Residential Planning Applications.
* Renewable Energy Projects.
* Student Housing Developments.

**Core Features:**

* Hero header: *“[Sector] Planning Applications”*.
* **Sector Stats:**

  * Volume of applications (last 12 months).
  * Approval rate in this sector.
  * Top 5 authorities active in this sector.
* **Application List:** Filtered by sector/use class.
* **Charts:**

  * Trend of sector applications over time.
  * Top 10 agents/consultants in this sector.
* **SEO Enhancements:**

  * Evergreen guides with AI summaries explaining the sector.
  * Internal linking to authority + location pages.
  * Schema markup for “Dataset” or “CreativeWorkSeries.”

---

### 2.4 Trends & Insights Hub

**Purpose:** A data-driven, interactive hub for showcasing UK-wide planning activity.

**Core Features:**

* **Dashboards (Interactive):**

  * Top 10 councils by approvals (monthly).
  * Fastest councils to decide (median days).
  * Most active agents/consultants (volume + approval rate).
* **Charts & Visualizations:**

  * Built with Recharts/D3.js for interactivity.
  * Export option (Pro plan).
* **Filters:** Date range, sector, authority.
* **SEO Enhancements:**

  * Static sections with commentary (“This month’s insights”).
  * Shareable dashboards (social cards, PDF export).

---

## 3. Data & Technical Requirements

### 3.1 Data Sources

* ✅ ES DB with planning applications.
* Aggregations required:

  * By authority (counts, approvals, refusals).
  * By location (geospatial clustering).
  * By use class (categorization).
  * By agent/consultant (activity, approvals).

### 3.2 Backend

* Extend API layer to provide **aggregations & stats endpoints**:

  * `/stats/authority/{id}`
  * `/stats/location/{postcode|town}`
  * `/stats/useclass/{code}`
  * `/stats/trends`

### 3.3 Frontend

* **Framework:** Next.js + Tailwind.
* **SEO-first architecture:** pre-render pages with SSR/ISR.
* **Charts:** Recharts or D3.js.
* **Maps:** Mapbox/Leaflet.

### 3.4 Caching & Performance

* Cache heavy aggregation queries in Redis.
* Use **Incremental Static Regeneration (ISR)** to pre-build SEO pages.
* Handle **10k+ long-tail SEO pages** (all councils, towns, postcodes, sectors).

---

## 4. UX/UI Requirements

* **Clean, consistent with Planning Explorer core design.**
* Page Layout:

  * Hero → Stats Panel → Filters → Chart → Application List → Related Pages.
* **Mobile-first responsive.**
* **Engagement CTAs:**

  * “Sign up to track applications in this area/sector.”
  * “Download full report (Pro only).”

---

## 5. Monetization Opportunities

* **Free:** Basic stats visible, applications previewed (2–3 results).
* **Pro:** Unlock full lists, detailed AI summaries, Opportunity Scores.
* **Enterprise:** Access Trends Hub with exportable dashboards, API feed of sector/location/authority insights.

---

## 6. Success Metrics

* **SEO Performance:**

  * Indexed pages by Google.
  * Organic impressions & CTR.
  * Long-tail traffic growth.

* **Engagement:**

  * Time on page (avg. per authority/location/sector).
  * % of users clicking “view more” or signing up.

* **Conversion:**

  * Free → Pro conversions via SEO landing pages.

---

## 7. Roadmap

### Phase 1 (MVP – 6 weeks)

* Authority pages (static + dynamic stats).
* Location pages (town + postcode level).
* Basic SEO optimizations (meta tags, schema).

### Phase 2 (3 months)

* Sector/use class pages with AI summaries.
* Trends & Insights Hub (interactive dashboards).
* Map-based visualizations.

### Phase 3 (6 months)

* Predictive insights (approval forecast).
* Personalized digests per sector/location.
* Open API for stats export.

---

✅ These **Content & Discovery Pages** give Planning Explorer a *double advantage*:

* Strong **SEO & inbound growth engine**.
* Valuable **exploration tools** for users → feeding into Pro/Enterprise upsells.

---

