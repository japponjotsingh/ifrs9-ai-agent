# IFRS 9 AI Agent

Autonomous credit risk analysis using Google's Gemini AI and BigQuery.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GCP](https://img.shields.io/badge/GCP-BigQuery-orange.svg)](https://cloud.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

An AI-powered system that analyzes credit portfolios through natural language questions. Ask "Why did ECL increase from Q3 to Q4?" and get detailed analysis with macroeconomic correlation in minutes instead of days.

### What It Does

Instead of manually writing SQL queries, you ask questions in plain English:

**Question:** "Why did Expected Credit Loss increase from Q3 to Q4?"

**AI Agent Response:**
```
ECL increased by $1.15M (+18%) from Q3 to Q4 2024.

Drivers:
• Unemployment rose from 3.8% to 4.3% (+0.5 points)
• GDP growth slowed from 2.8% to 1.9% (-0.9 points)  
• 260 loans migrated from Stage 1 to Stage 2
• 38 new defaults (Stage 3 increased 46%)

Most affected:
• Credit Cards: 14.26% ECL rate
• Personal Loans: 8.55% ECL rate

Recommendations:
1. Tighten underwriting for unsecured products
2. Increase provisions by ~$600K
3. Enhanced Stage 2 monitoring
```

The agent writes SQL, queries BigQuery, analyzes results, and generates insights automatically.

---

## Key Features

**Autonomous Operation**
- Takes natural language questions
- Writes SQL queries automatically
- Executes on BigQuery
- Generates executive insights

**Self-Correcting**
- Detects SQL errors
- Fixes mistakes automatically
- Retries up to 3 times

**Macroeconomic Integration**
- Correlates portfolio changes with economic factors
- Explains causation, not just correlation
- Tracks unemployment, GDP, interest rates, inflation

**Production Ready**
- Rate limit handling
- Error recovery
- Proper authentication
- Clean logging

---

## Architecture

```
Question (Natural Language)
    ↓
Google Gemini AI
    ↓
SQL Query Generation
    ↓
BigQuery Execution
    ↓
Results Analysis
    ↓
Executive Insights + Recommendations
```

**Tech Stack:**
- **AI:** Google Gemini 2.0 Flash via Vertex AI
- **Data Warehouse:** Google BigQuery
- **Language:** Python 3.8+
- **Platform:** Google Cloud Platform

---

## Quick Start

### Prerequisites

- Python 3.8+
- Google Cloud Platform account
- BigQuery API enabled
- Vertex AI API enabled

### 1. Generate Data

```bash
# Generate Q3 and Q4 portfolio data
python generate_quarterly_data.py

# Generate macroeconomic variables
python create_macro_variables.py
```

This creates:
- Q3 2024: 5,000 loans, $259.5M exposure, $6.3M ECL
- Q4 2024: 5,000 loans, $253.0M exposure, $7.5M ECL (+18%)
- Macro data: Unemployment, GDP, rates (Q3 vs Q4)

### 2. Load to BigQuery

```bash
# Update PROJECT_ID in setup script
python setup_bigquery_quarterly.py
```

Creates 3 tables:
- `loan_portfolio_q3_2024`
- `loan_portfolio_q4_2024`
- `macroeconomic_variables`

### 3. Configure AI Agent

**Get Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Create API key for your project
3. Copy the key

**Create Service Account:**
1. Go to GCP Console → IAM & Admin → Service Accounts
2. Create account with BigQuery Admin + Vertex AI User roles
3. Download JSON key

**Update `ai_agent_notebook.py`:**
```python
GEMINI_API_KEY = "your-api-key-here"
# Upload JSON key to your environment
```

### 4. Run AI Agent

```python
from ai_agent_notebook import autonomous_agent

# Ask questions
autonomous_agent("Compare ECL between Q3 and Q4")
autonomous_agent("How did unemployment affect defaults?")
autonomous_agent("Which product has highest risk?")
```

---

## Example Questions

**Portfolio Analysis:**
- "Compare total ECL between Q3 and Q4"
- "How many loans migrated from Stage 1 to Stage 2?"
- "Which product type has the highest ECL?"
- "Show me the top 10 riskiest loans"

**Macro Correlation:**
- "How did rising unemployment affect Stage 3 defaults?"
- "Correlate GDP growth with ECL changes"
- "What impact did interest rate increases have?"

**Strategic:**
- "What should management do about Stage 2 concentration?"
- "Given macro deterioration, what are the top risks?"
- "Recommend provisioning adjustments"

---

## Project Results

### Portfolio Evolution

| Metric | Q3 2024 | Q4 2024 | Change |
|--------|---------|---------|--------|
| Total ECL | $6.3M | $7.5M | +$1.1M (+18%) |
| Stage 1 | 2,611 | 2,393 | -218 |
| Stage 2 | 2,306 | 2,486 | +180 |
| Stage 3 | 83 | 121 | +38 (+46%) |

### Macroeconomic Drivers

| Factor | Q3 | Q4 | Impact |
|--------|----|----|--------|
| Unemployment | 3.8% | 4.3% | Critical (+0.5) |
| GDP Growth | 2.8% | 1.9% | High (-0.9) |
| 10Y Yield | 4.25% | 4.65% | High (+40bps) |

### Migration Analysis

- Stage 1 → Stage 2: 260 loans (deterioration)
- Stage 2 → Stage 3: 38 loans (defaults)
- Stage 2 → Stage 1: 53 loans (improvements)

---

## Technical Details

### Data Schema

**Loan Portfolio Tables:**
- loan_id, product_type, outstanding_balance
- credit_score_current, days_past_due
- ifrs9_stage (1, 2, or 3)
- ecl_amount, ecl_rate
- pd_12m, pd_lifetime, lgd
- geography, origination_date

**Macro Variables:**
- quarter, reporting_date
- bond_yield_10y, gdp_growth_rate
- unemployment_rate, inflation_rate
- consumer_confidence, credit_spread

### AI Agent Implementation

The agent operates in 3 steps:

**Step 1: SQL Generation**
- Sends question + table schema to Gemini
- AI writes appropriate SQL query
- Handles complex JOINs and aggregations

**Step 2: Execution with Self-Correction**
- Runs SQL on BigQuery
- If error occurs, sends error message to AI
- AI fixes the SQL and retries
- Up to 3 attempts

**Step 3: Insight Generation**
- Sends results + context to Gemini
- AI analyzes patterns
- Generates executive summary
- Provides recommendations

---

## Skills Demonstrated

**Technical:**
- Large Language Models (LLMs) and Generative AI
- Cloud Data Engineering (BigQuery)
- Agentic AI Systems
- SQL Query Optimization
- Python Automation
- API Integration (REST, OAuth)
- Error Handling & Retry Logic

**Domain:**
- IFRS 9 Accounting Standards
- Expected Credit Loss Modeling
- Credit Risk Analytics
- Macroeconomic Analysis
- Portfolio Management
- SICR Detection

**Business:**
- Executive Communication
- Data-Driven Decision Making
- Process Automation (3 days → 5 minutes)
- ROI Demonstration

---

## Project Structure

```
ifrs9-ai-agent/
├── README.md                          
├── ai_agent_notebook.py               # Main AI agent
├── generate_quarterly_data.py         # Data generation
├── create_macro_variables.py          # Macro data
├── setup_bigquery_quarterly.py        # BigQuery setup
├── loan_portfolio_q3_2024.csv         # Q3 data
├── loan_portfolio_q4_2024.csv         # Q4 data
├── macroeconomic_variables.csv        # Macro factors
└── macro_context.json                 # Economic context
```

---

## Use Cases

**For Credit Risk Teams:**
- Automated quarterly analysis
- Macro correlation analysis
- Portfolio monitoring
- Executive reporting

**For Management:**
- Quick answers to "why" questions
- Data-driven decisions
- Scenario analysis
- Risk identification

**For Auditors:**
- Transparent calculations
- Documented methodology
- Consistent framework
- Audit trail

---

## Future Enhancements

**Phase 1 (Current):**
- Natural language query interface
- Automated SQL generation
- Executive insight generation
- Macro correlation

**Phase 2 (Planned):**
- Interactive visualizations
- Real-time dashboards
- Automated scheduling
- Email alerts

**Phase 3 (Future):**
- Predictive ML models
- Stress testing scenarios
- Portfolio optimization
- Early warning system

---

## Limitations

**Rate Limiting:**
- Free tier: 15 requests/minute
- Cooldown: 10-15 minutes after heavy use
- Handled automatically in code

**Data Scope:**
- Synthetic data for demonstration
- 5,000 loans per quarter
- Simplified economic model

**SQL Complexity:**
- Works best with standard queries
- May require retry for complex JOINs
- Self-corrects common errors

---

## Contributing

This is a portfolio project demonstrating AI capabilities for credit risk analysis. Feel free to fork and adapt for your use case.

---

## License

MIT License - See LICENSE file for details

---

## Contact

**Japponjot Singh**  
Email: japponjot.singh@gmail.com  
LinkedIn: https://www.linkedin.com/in/japponjot-singh/  
GitHub: https://github.com/japponjotsingh

---

## Acknowledgments

- Google Cloud Platform for infrastructure
- Vertex AI and Gemini for AI capabilities
- IFRS Foundation for accounting standards

---

**Built to demonstrate modern credit risk analytics with AI automation**

*Last Updated: February 2026*
