"""
BigQuery Setup for Q3 and Q4 2024 Portfolio Data
Loads both quarterly datasets for AI Agent analysis
"""

from google.cloud import bigquery
import os

# Configuration
PROJECT_ID = "your-gcp-project-id"  # Replace with your project ID
DATASET_ID = "credit_risk_ifrs9"

def create_bigquery_dataset(client, dataset_id):
    """Create BigQuery dataset if it doesn't exist"""
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset.description = "IFRS 9 Credit Risk Analytics - Quarterly Data"
        
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"✅ Created dataset {dataset_id}")


def load_quarterly_data(client, dataset_id, csv_file, table_id):
    """Load CSV data into BigQuery table"""
    
    table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=[
            bigquery.SchemaField("loan_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("reporting_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("product_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("origination_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("original_amount", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("outstanding_balance", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("credit_score_origination", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("credit_score_current", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("days_past_due", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("interest_rate", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("industry_sector", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("geography", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("pd_12m", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("pd_lifetime", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("lgd", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("ifrs9_stage", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("ecl_amount", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("ecl_rate", "FLOAT64", mode="REQUIRED"),
        ]
    )
    
    with open(csv_file, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    
    job.result()  # Wait for completion
    
    table = client.get_table(table_ref)
    print(f"✅ Loaded {table.num_rows:,} rows into {table_id}")


def verify_data(client, dataset_id):
    """Verify both tables are loaded correctly"""
    
    print("\n" + "="*70)
    print("VERIFICATION - Checking Loaded Data")
    print("="*70)
    
    for quarter, table_id in [("Q3 2024", "loan_portfolio_q3_2024"), 
                               ("Q4 2024", "loan_portfolio_q4_2024")]:
        
        query = f"""
        SELECT 
            reporting_date,
            COUNT(*) as total_loans,
            SUM(outstanding_balance) as total_exposure,
            SUM(ecl_amount) as total_ecl,
            SUM(CASE WHEN ifrs9_stage = 1 THEN 1 ELSE 0 END) as stage1_count,
            SUM(CASE WHEN ifrs9_stage = 2 THEN 1 ELSE 0 END) as stage2_count,
            SUM(CASE WHEN ifrs9_stage = 3 THEN 1 ELSE 0 END) as stage3_count
        FROM `{PROJECT_ID}.{dataset_id}.{table_id}`
        GROUP BY reporting_date
        """
        
        results = client.query(query).result()
        
        print(f"\n{quarter}:")
        for row in results:
            print(f"  Date: {row.reporting_date}")
            print(f"  Total Loans: {row.total_loans:,}")
            print(f"  Total Exposure: ${row.total_exposure:,.2f}")
            print(f"  Total ECL: ${row.total_ecl:,.2f}")
            print(f"  Stage 1: {row.stage1_count:,} | Stage 2: {row.stage2_count:,} | Stage 3: {row.stage3_count:,}")


def create_comparison_view(client, dataset_id):
    """Create a view that compares Q3 vs Q4"""
    
    view_id = f"{PROJECT_ID}.{dataset_id}.quarterly_comparison"
    
    view_query = f"""
    WITH q3 AS (
        SELECT 
            'Q3 2024' as quarter,
            COUNT(*) as total_loans,
            SUM(outstanding_balance) as total_exposure,
            SUM(ecl_amount) as total_ecl,
            SUM(CASE WHEN ifrs9_stage = 1 THEN 1 ELSE 0 END) as stage1,
            SUM(CASE WHEN ifrs9_stage = 2 THEN 1 ELSE 0 END) as stage2,
            SUM(CASE WHEN ifrs9_stage = 3 THEN 1 ELSE 0 END) as stage3
        FROM `{PROJECT_ID}.{dataset_id}.loan_portfolio_q3_2024`
    ),
    q4 AS (
        SELECT 
            'Q4 2024' as quarter,
            COUNT(*) as total_loans,
            SUM(outstanding_balance) as total_exposure,
            SUM(ecl_amount) as total_ecl,
            SUM(CASE WHEN ifrs9_stage = 1 THEN 1 ELSE 0 END) as stage1,
            SUM(CASE WHEN ifrs9_stage = 2 THEN 1 ELSE 0 END) as stage2,
            SUM(CASE WHEN ifrs9_stage = 3 THEN 1 ELSE 0 END) as stage3
        FROM `{PROJECT_ID}.{dataset_id}.loan_portfolio_q4_2024`
    )
    SELECT * FROM q3
    UNION ALL
    SELECT * FROM q4
    """
    
    view = bigquery.Table(view_id)
    view.view_query = view_query
    
    try:
        client.delete_table(view_id, not_found_ok=True)
    except:
        pass
    
    view = client.create_table(view)
    print(f"\n✅ Created comparison view: {view_id}")


def main():
    """Main setup function"""
    
    print("="*70)
    print("IFRS 9 QUARTERLY DATA - BIGQUERY SETUP")
    print("="*70)
    
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=PROJECT_ID)
        print(f"\n✅ Connected to project: {PROJECT_ID}\n")
        
        # Create dataset
        create_bigquery_dataset(client, DATASET_ID)
        
        # Load Q3 2024 data
        print("\n📊 Loading Q3 2024 data...")
        q3_file = "loan_portfolio_q3_2024.csv"
        if os.path.exists(q3_file):
            load_quarterly_data(client, DATASET_ID, q3_file, "loan_portfolio_q3_2024")
        else:
            print(f"❌ File not found: {q3_file}")
            print("   Please run generate_quarterly_data.py first")
            return
        
        # Load Q4 2024 data
        print("\n📊 Loading Q4 2024 data...")
        q4_file = "loan_portfolio_q4_2024.csv"
        if os.path.exists(q4_file):
            load_quarterly_data(client, DATASET_ID, q4_file, "loan_portfolio_q4_2024")
        else:
            print(f"❌ File not found: {q4_file}")
            return
        
        # Load Macro Variables
        print("\n📊 Loading Macroeconomic Variables...")
        macro_file = "macroeconomic_variables.csv"
        if os.path.exists(macro_file):
            macro_table_ref = f"{PROJECT_ID}.{DATASET_ID}.macroeconomic_variables"
            
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            
            with open(macro_file, "rb") as source_file:
                job = client.load_table_from_file(source_file, macro_table_ref, job_config=job_config)
            job.result()
            
            table = client.get_table(macro_table_ref)
            print(f"✅ Loaded {table.num_rows:,} rows into macroeconomic_variables")
        else:
            print(f"⚠️  Macro file not found (optional): {macro_file}")
        
        # Verify data
        verify_data(client, DATASET_ID)
        
        # Create comparison view
        create_comparison_view(client, DATASET_ID)
        
        print("\n" + "="*70)
        print("✅ SETUP COMPLETE!")
        print("="*70)
        print("\nTables created:")
        print(f"  • {PROJECT_ID}.{DATASET_ID}.loan_portfolio_q3_2024")
        print(f"  • {PROJECT_ID}.{DATASET_ID}.loan_portfolio_q4_2024")
        print(f"  • {PROJECT_ID}.{DATASET_ID}.macroeconomic_variables")
        print(f"  • {PROJECT_ID}.{DATASET_ID}.quarterly_comparison (view)")
        
        print("\nNext steps:")
        print("1. Go to BigQuery Console: https://console.cloud.google.com/bigquery")
        print("2. Run sample queries from the comparison view")
        print("3. Use the AI Agent notebook to ask questions!")
        print("4. AI Agent can now correlate macro factors with portfolio changes!")
        
        print("\nExample query with macro data:")
        print(f"""
SELECT 
    p.quarter,
    p.total_ecl,
    m.unemployment_rate,
    m.gdp_growth_rate
FROM `{PROJECT_ID}.{DATASET_ID}.quarterly_comparison` p
JOIN `{PROJECT_ID}.{DATASET_ID}.macroeconomic_variables` m
    ON p.quarter = m.quarter
        """)
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you've updated PROJECT_ID in this script")
        print("2. Check that BigQuery API is enabled")
        print("3. Verify GOOGLE_APPLICATION_CREDENTIALS is set")
        print("4. Confirm you have BigQuery Admin permissions")


if __name__ == "__main__":
    main()
