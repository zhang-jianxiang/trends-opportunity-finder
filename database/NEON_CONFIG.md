# Neon Database Configuration

## Project Info
- Project Name: google-trends-data
- Project ID: plain-hat-08744468
- Branch: production (br-summer-meadow-ax1tivvb)
- Database: neondb
- Region: AWS US East 2 (Ohio)
- Console: https://console.neon.tech/app/projects/plain-hat-08744468

## Connection String

```
DATABASE_URL=postgresql://neondb_owner:npg_vygZC0eU5zSP@ep-withered-haze-axektkl2-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Note: Removed channel_binding=require parameter for psycogpc2 compatibility.
Neon free tier serverless compute auto-sleeps when idle.

## SQL Editor
https://console.neon.tech/app/projects/plain-hat-08744468/branches/br-summer-meadow-ax1tivvb/sql-editor?database=neondb

## Tables
- keywords (10 rows)
- regions (12 rows)
- trends_data (0 rows, waiting for collection)
- trend_analysis (0 rows, waiting for analysis)
- opportunities (0 rows, waiting for detection)
- collection_logs (0 rows, waiting for execution)
