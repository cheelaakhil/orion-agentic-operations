# ORION Synthetic Dataset Storage

This directory holds dataset schemas, generated data snapshots, and synthetic scenarios used by ORION.

## Dataset Structure

The primary dataset models a multi-channel e-commerce retailer (**NovaMart**) over a 90-day period.

### Data Files (Generated / Seeded)
- `orders.csv` / `orders.parquet` — Daily transactional records with customer IDs, item SKUs, regional routing, fulfillment metrics, and gross revenue.
- `products.csv` — Product catalog with categories, SKU metadata, base cost, list prices, and active supply status.
- `customers.csv` — Customer segmentation (VIP, Regular, At-Risk, Churned), acquisition cohort dates, geographic regions, and historical LTV.
- `inventory.csv` — Daily inventory snapshots by warehouse region, stock-on-hand, reorder thresholds, and stockout occurrences.
- `support_tickets.csv` — Support ticket lifecycle logs, timestamps for ticket open, first response, resolution, SLA breach flags, CSAT ratings, and categorization.
- `marketing_campaigns.csv` — Campaign channel metadata, daily spend, impressions, CTR, conversion rates, and attributed revenue.

## Engineered Business Incident

The dataset contains a controlled operational breakdown:
1. **Support SLA deterioration** (gradual response time increase from ~2h to 18+ hours due to team understaffing).
2. **Key category stockouts** (supply chain disruption leading to lost conversions on top sellers).
3. **Compound downstream impact** (repeat purchase collapse and measurable top-line revenue decline of ~23%).
