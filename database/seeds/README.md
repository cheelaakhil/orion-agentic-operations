# Synthetic Dataset Seeds

This directory contains scripts to generate ORION's synthetic dataset
for the NovaMart demo scenario.

## Engineered Business Incident

The dataset deliberately engineers the following incident:

1. **Support SLA Degradation** (Root Cause #1)
   - Support response times increase from ~2h to 18+ hours
   - Caused by understaffing during a growth period
   - Onset: gradual over 30 days

2. **Inventory Stockouts** (Root Cause #2)
   - 3 of 8 product categories experience stockouts
   - Caused by supply chain delays
   - Onset: sudden, approximately 2 weeks after support degradation

3. **Compounding Effect** (Measurable Outcome)
   - Repeat purchase rate drops from 34% to 21%
   - New customer conversion drops due to stockouts
   - Total revenue declines ~23% over 60 days

## Generation

```bash
python -m database.seeds.generate
```

This will populate all business tables with ~90 days of synthetic data
containing the engineered incident above.
