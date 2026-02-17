"""
IFRS 9 AI Agent - Autonomous Credit Risk Analysis
Author: Japponjot Singh
Date: February 2026

This module provides an autonomous AI agent that analyzes credit portfolios
using Google's Gemini LLM. The agent takes natural language questions,
generates SQL queries, executes them on BigQuery, and provides insights.
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import requests
import json
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# BigQuery Configuration
SERVICE_ACCOUNT_KEY = '/home/jupyter/ifrs9-analytics-4c7c8e70c91c.json'
PROJECT_ID = "ifrs9-analytics"
DATASET_ID = "credit_risk_ifrs9"

# Gemini API Configuration
GEMINI_API_KEY = "GEMINI_API_KEY", "your-key-here"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Initialize BigQuery Client
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_KEY
)

client = bigquery.Client(
    project=PROJECT_ID,
    credentials=credentials
)

print("AI Agent initialized successfully")

# ============================================================================
# MAIN AI AGENT FUNCTION
# ============================================================================

def autonomous_agent(question):
    """
    Autonomous AI Agent for credit risk analysis.
    
    Takes a natural language question, generates SQL, executes on BigQuery,
    and provides detailed insights with macroeconomic correlation.
    
    Args:
        question (str): Natural language question about the portfolio
        
    Returns:
        dict: Contains SQL query, data, and AI-generated insights
        
    Example:
        result = autonomous_agent("Why did ECL increase from Q3 to Q4?")
    """
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    # ========================================================================
    # STEP 1: GENERATE SQL QUERY
    # ========================================================================
    
    print("\n" + "="*70)
    print(f"QUESTION: {question}")
    print("="*70)
    
    sql_prompt = f"""
You are a SQL expert for BigQuery. Generate a SQL query to answer this question:

QUESTION: {question}

AVAILABLE TABLES:

1. `{PROJECT_ID}.{DATASET_ID}.loan_portfolio_q3_2024`
   Columns: loan_id, reporting_date, product_type, outstanding_balance,
            credit_score_current, days_past_due, ifrs9_stage, ecl_amount,
            ecl_rate, pd_12m, lgd, geography

2. `{PROJECT_ID}.{DATASET_ID}.loan_portfolio_q4_2024`
   Same columns as Q3

3. `{PROJECT_ID}.{DATASET_ID}.macroeconomic_variables`
   Columns: quarter, reporting_date, bond_yield_10y, gdp_growth_rate,
            unemployment_rate, inflation_rate

INSTRUCTIONS:
- Return ONLY the SQL query, no explanations
- Use INNER JOIN or LEFT JOIN (NOT CROSS JOIN)
- Include proper ON clause for joins
- Use valid BigQuery syntax

SQL Query:
"""
    
    data = {"contents": [{"parts": [{"text": sql_prompt}]}]}
    
    print("\nAI Agent: Writing SQL query...")
    response = requests.post(GEMINI_URL, headers=headers, json=data)
    
    # Handle rate limiting
    if response.status_code == 429:
        print("Rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        response = requests.post(GEMINI_URL, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None
    
    # Extract SQL
    sql_query = response.json()['candidates'][0]['content']['parts'][0]['text']
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    print(f"\nGenerated SQL:")
    print("-" * 70)
    print(sql_query)
    print("-" * 70)
    
    # ========================================================================
    # STEP 2: EXECUTE SQL (WITH SELF-CORRECTION)
    # ========================================================================
    
    print("\nExecuting query on BigQuery...")
    
    max_attempts = 3
    attempt = 1
    query_results = None
    
    while attempt <= max_attempts:
        try:
            query_results = client.query(sql_query).to_dataframe()
            print(f"Success! Retrieved {len(query_results)} rows")
            
            # Show preview
            if len(query_results) > 0:
                print("\nData Preview:")
                print(query_results.head(10).to_string())
            
            break  # Success - exit loop
            
        except Exception as e:
            error_msg = str(e)
            print(f"Attempt {attempt} failed: {error_msg[:200]}...")
            
            if attempt < max_attempts:
                print(f"\nAI Agent: Fixing the SQL query...")
                
                # Ask AI to fix
                fix_prompt = f"""
The following SQL query has an error. Please fix it.

ORIGINAL QUERY:
{sql_query}

ERROR:
{error_msg}

Return ONLY the corrected SQL query. Make sure to use INNER JOIN or LEFT JOIN
with proper ON clause.
"""
                
                data = {"contents": [{"parts": [{"text": fix_prompt}]}]}
                time.sleep(3)
                
                response = requests.post(GEMINI_URL, headers=headers, json=data)
                
                if response.status_code == 200:
                    sql_query = response.json()['candidates'][0]['content']['parts'][0]['text']
                    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
                    
                    print(f"\nCorrected SQL (Attempt {attempt + 1}):")
                    print("-" * 70)
                    print(sql_query)
                    print("-" * 70)
                    
                    attempt += 1
                else:
                    print("Could not get corrected SQL")
                    return None
            else:
                print(f"Failed after {max_attempts} attempts")
                return None
    
    if query_results is None or len(query_results) == 0:
        print("No results returned")
        return None
    
    # ========================================================================
    # STEP 3: GENERATE INSIGHTS
    # ========================================================================
    
    print("\nAI Agent: Analyzing results...")
    
    analysis_prompt = f"""
You are a senior credit risk analyst.

QUESTION: {question}

QUERY RESULTS:
{query_results.to_string()}

CONTEXT:
- Q3 2024 was baseline, Q4 2024 shows evolution
- Macroeconomic conditions deteriorated in Q4:
  * Unemployment: 3.8% → 4.3% (+0.5 points)
  * GDP Growth: 2.8% → 1.9% (-0.9 points)
  * 10Y Yield: 4.25% → 4.65% (+40 bps)

PROVIDE:
1. Direct answer with specific numbers
2. Key insights and patterns
3. Business implications
4. Recommendations if applicable
5. Explain how macro factors influenced results if relevant

Format as professional executive summary.
"""
    
    data = {"contents": [{"parts": [{"text": analysis_prompt}]}]}
    
    time.sleep(3)  # Avoid rate limit
    
    response = requests.post(GEMINI_URL, headers=headers, json=data)
    
    if response.status_code == 429:
        print("Rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        response = requests.post(GEMINI_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        analysis = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        print("\n" + "="*70)
        print("AI AGENT INSIGHTS")
        print("="*70)
        print(analysis)
        print("="*70 + "\n")
        
        return {
            'question': question,
            'sql': sql_query,
            'data': query_results,
            'insights': analysis
        }
    else:
        print(f"Analysis failed: {response.status_code}")
        print(response.json())
        return None


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("IFRS 9 AI AGENT - READY")
    print("="*70)
    print("\nExample questions:")
    print("  autonomous_agent('Compare ECL between Q3 and Q4')")
    print("  autonomous_agent('How did unemployment affect defaults?')")
    print("  autonomous_agent('Which product has highest risk?')")
    print("="*70 + "\n")
