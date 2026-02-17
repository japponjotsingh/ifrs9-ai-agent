"""
Generate Q3 and Q4 2024 Loan Portfolio Data with Realistic Changes
This creates two quarterly snapshots showing portfolio evolution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_base_portfolio(n_loans=5000, reporting_date=datetime(2024, 9, 30)):
    """Generate base loan portfolio (Q3 2024)"""
    
    # Loan IDs
    loan_ids = [f"LN{str(i).zfill(7)}" for i in range(1, n_loans + 1)]
    
    # Product types
    product_types = ['Mortgage', 'Personal Loan', 'Auto Loan', 'Credit Card', 'SME Loan']
    products = np.random.choice(product_types, n_loans, p=[0.35, 0.25, 0.20, 0.15, 0.05])
    
    # Origination dates (between 1-5 years ago from Q3)
    days_ago = np.random.randint(365, 1825, n_loans)
    origination_dates = [reporting_date - timedelta(days=int(d)) for d in days_ago]
    
    # Original loan amounts
    original_amounts = []
    for product in products:
        if product == 'Mortgage':
            amount = np.random.lognormal(12.5, 0.5)
        elif product == 'Personal Loan':
            amount = np.random.lognormal(9.5, 0.6)
        elif product == 'Auto Loan':
            amount = np.random.lognormal(10.3, 0.4)
        elif product == 'Credit Card':
            amount = np.random.lognormal(8.5, 0.5)
        else:  # SME Loan
            amount = np.random.lognormal(11.5, 0.7)
        original_amounts.append(amount)
    
    # Current outstanding balance (EAD)
    outstanding_balances = []
    for i, orig_date in enumerate(origination_dates):
        months_elapsed = (reporting_date - orig_date).days / 30
        amort_factor = max(0.3, 1 - (months_elapsed / 60))
        outstanding_balances.append(original_amounts[i] * amort_factor * np.random.uniform(0.85, 1.0))
    
    # Credit scores at origination
    credit_scores_orig = np.random.normal(680, 80, n_loans).clip(300, 850)
    
    # Current credit scores (Q3)
    credit_scores_current = []
    for score in credit_scores_orig:
        change = np.random.normal(0, 25)
        credit_scores_current.append(max(300, min(850, score + change)))
    
    # Days past due (DPD) - Q3 baseline
    dpd_distribution = np.random.choice(
        [0, 30, 60, 90, 120, 180],
        n_loans,
        p=[0.87, 0.07, 0.03, 0.015, 0.01, 0.005]  # Healthier in Q3
    )
    
    # Interest rates
    interest_rates = []
    for product, score in zip(products, credit_scores_orig):
        if product == 'Mortgage':
            base_rate = 4.5
        elif product == 'Personal Loan':
            base_rate = 9.0
        elif product == 'Auto Loan':
            base_rate = 6.5
        elif product == 'Credit Card':
            base_rate = 18.0
        else:
            base_rate = 7.5
        
        risk_premium = (750 - score) / 100 * 0.5
        interest_rates.append(max(2.0, base_rate + risk_premium + np.random.uniform(-0.5, 0.5)))
    
    # Industry sector (for SME loans)
    sectors = ['Retail', 'Manufacturing', 'Services', 'Construction', 'Technology', 'Healthcare', 'N/A']
    industry_sectors = []
    for product in products:
        if product == 'SME Loan':
            industry_sectors.append(np.random.choice(sectors[:-1]))
        else:
            industry_sectors.append('N/A')
    
    # Geography
    regions = ['North', 'South', 'East', 'West', 'Central']
    geographies = np.random.choice(regions, n_loans, p=[0.25, 0.20, 0.20, 0.20, 0.15])
    
    # Create DataFrame
    df = pd.DataFrame({
        'loan_id': loan_ids,
        'reporting_date': reporting_date,
        'product_type': products,
        'origination_date': origination_dates,
        'original_amount': original_amounts,
        'outstanding_balance': outstanding_balances,
        'credit_score_origination': credit_scores_orig,
        'credit_score_current': credit_scores_current,
        'days_past_due': dpd_distribution,
        'interest_rate': interest_rates,
        'industry_sector': industry_sectors,
        'geography': geographies
    })
    
    # Round numeric columns
    df['original_amount'] = df['original_amount'].round(2)
    df['outstanding_balance'] = df['outstanding_balance'].round(2)
    df['credit_score_origination'] = df['credit_score_origination'].round(0).astype(int)
    df['credit_score_current'] = df['credit_score_current'].round(0).astype(int)
    df['interest_rate'] = df['interest_rate'].round(2)
    
    return df


def calculate_pd_lgd(df):
    """Calculate PD (Probability of Default) and LGD (Loss Given Default)"""
    
    def calculate_12m_pd(row):
        if row['credit_score_current'] >= 750:
            base_pd = 0.005
        elif row['credit_score_current'] >= 700:
            base_pd = 0.01
        elif row['credit_score_current'] >= 650:
            base_pd = 0.025
        elif row['credit_score_current'] >= 600:
            base_pd = 0.05
        else:
            base_pd = 0.10
        
        if row['days_past_due'] == 0:
            dpd_multiplier = 1.0
        elif row['days_past_due'] <= 30:
            dpd_multiplier = 2.0
        elif row['days_past_due'] <= 90:
            dpd_multiplier = 4.0
        else:
            dpd_multiplier = 8.0
        
        product_adj = {
            'Mortgage': 0.7,
            'Auto Loan': 0.9,
            'Personal Loan': 1.2,
            'Credit Card': 1.5,
            'SME Loan': 1.3
        }
        
        pd = base_pd * dpd_multiplier * product_adj.get(row['product_type'], 1.0)
        return min(pd, 1.0)
    
    def calculate_lifetime_pd(row):
        return min(row['pd_12m'] * 3.0, 1.0)
    
    def calculate_lgd(row):
        lgd_by_product = {
            'Mortgage': np.random.uniform(0.15, 0.30),
            'Auto Loan': np.random.uniform(0.25, 0.40),
            'Personal Loan': np.random.uniform(0.50, 0.70),
            'Credit Card': np.random.uniform(0.60, 0.80),
            'SME Loan': np.random.uniform(0.40, 0.60)
        }
        return lgd_by_product.get(row['product_type'], 0.50)
    
    df['pd_12m'] = df.apply(calculate_12m_pd, axis=1)
    df['pd_lifetime'] = df.apply(calculate_lifetime_pd, axis=1)
    df['lgd'] = df.apply(calculate_lgd, axis=1)
    
    df['pd_12m'] = df['pd_12m'].round(6)
    df['pd_lifetime'] = df['pd_lifetime'].round(6)
    df['lgd'] = df['lgd'].round(4)
    
    return df


def assign_ifrs9_stage(df):
    """Assign IFRS 9 staging (Stage 1, 2, or 3)"""
    
    def determine_stage(row):
        if row['days_past_due'] > 90:
            return 3
        
        credit_score_drop = row['credit_score_origination'] - row['credit_score_current']
        pd_increase = row['pd_12m'] > 0.03
        
        if (row['days_past_due'] >= 30 or credit_score_drop > 100 or pd_increase):
            return 2
        
        return 1
    
    df['ifrs9_stage'] = df.apply(determine_stage, axis=1)
    return df


def calculate_ecl(df):
    """Calculate Expected Credit Loss"""
    
    def calc_ecl(row):
        ead = row['outstanding_balance']
        
        if row['ifrs9_stage'] == 1:
            ecl = ead * row['pd_12m'] * row['lgd']
        else:
            ecl = ead * row['pd_lifetime'] * row['lgd']
        
        return ecl
    
    df['ecl_amount'] = df.apply(calc_ecl, axis=1).round(2)
    df['ecl_rate'] = (df['ecl_amount'] / df['outstanding_balance'] * 100).round(4)
    
    return df


def evolve_to_q4(df_q3):
    """
    Evolve Q3 portfolio to Q4 with realistic changes
    - Some loans deteriorate (credit scores drop, DPD increases)
    - Some loans improve (payments made, credit scores improve)
    - Stage migrations occur
    - Balances decrease (normal amortization)
    """
    
    df_q4 = df_q3.copy()
    df_q4['reporting_date'] = datetime(2024, 12, 31)
    
    n_loans = len(df_q4)
    
    # Simulate 3 months of changes
    
    # 1. Balance reduction (normal amortization - 3 months)
    df_q4['outstanding_balance'] = df_q4['outstanding_balance'] * np.random.uniform(0.96, 0.99, n_loans)
    
    # 2. Credit score changes (more deterioration than improvement)
    deterioration_indices = np.random.choice(df_q4.index, size=int(n_loans * 0.25), replace=False)
    improvement_indices = np.random.choice(
        [i for i in df_q4.index if i not in deterioration_indices], 
        size=int(n_loans * 0.15), 
        replace=False
    )
    
    # Deteriorate some credit scores
    for idx in deterioration_indices:
        change = np.random.uniform(-25, -5)
        df_q4.at[idx, 'credit_score_current'] = int(max(300, df_q4.at[idx, 'credit_score_current'] + change))
    
    # Improve some credit scores
    for idx in improvement_indices:
        change = np.random.uniform(5, 20)
        df_q4.at[idx, 'credit_score_current'] = int(min(850, df_q4.at[idx, 'credit_score_current'] + change))
    
    # 3. DPD changes - some deteriorate, some improve
    # Loans that were current may become delinquent
    current_loans = df_q4[df_q4['days_past_due'] == 0].index
    newly_delinquent = np.random.choice(current_loans, size=int(len(current_loans) * 0.08), replace=False)
    
    for idx in newly_delinquent:
        df_q4.at[idx, 'days_past_due'] = np.random.choice([30, 60], p=[0.7, 0.3])
    
    # Some 30 DPD become 60 or 90
    dpd_30 = df_q4[df_q4['days_past_due'] == 30].index
    worsening_30 = np.random.choice(dpd_30, size=int(len(dpd_30) * 0.4), replace=False)
    
    for idx in worsening_30:
        df_q4.at[idx, 'days_past_due'] = np.random.choice([60, 90], p=[0.6, 0.4])
    
    # Some 60 DPD become 90 or 120
    dpd_60 = df_q4[df_q4['days_past_due'] == 60].index
    worsening_60 = np.random.choice(dpd_60, size=int(len(dpd_60) * 0.5), replace=False)
    
    for idx in worsening_60:
        df_q4.at[idx, 'days_past_due'] = np.random.choice([90, 120], p=[0.7, 0.3])
    
    # Some delinquent loans cure (pay down)
    delinquent = df_q4[df_q4['days_past_due'] > 0].index
    curing = np.random.choice(delinquent, size=int(len(delinquent) * 0.15), replace=False)
    
    for idx in curing:
        current_dpd = df_q4.at[idx, 'days_past_due']
        if current_dpd == 30:
            df_q4.at[idx, 'days_past_due'] = 0
        elif current_dpd == 60:
            df_q4.at[idx, 'days_past_due'] = 30
        elif current_dpd >= 90:
            df_q4.at[idx, 'days_past_due'] = 60
    
    # Round credit scores
    df_q4['credit_score_current'] = df_q4['credit_score_current'].round(0).astype(int)
    df_q4['outstanding_balance'] = df_q4['outstanding_balance'].round(2)
    
    # Recalculate risk parameters with new data
    df_q4 = calculate_pd_lgd(df_q4)
    df_q4 = assign_ifrs9_stage(df_q4)
    df_q4 = calculate_ecl(df_q4)
    
    return df_q4


if __name__ == "__main__":
    print("="*70)
    print("GENERATING QUARTERLY LOAN PORTFOLIO DATA")
    print("="*70)
    
    # Generate Q3 2024 portfolio
    print("\n📊 Generating Q3 2024 Portfolio (September 30, 2024)...")
    df_q3 = generate_base_portfolio(n_loans=5000, reporting_date=datetime(2024, 9, 30))
    df_q3 = calculate_pd_lgd(df_q3)
    df_q3 = assign_ifrs9_stage(df_q3)
    df_q3 = calculate_ecl(df_q3)
    
    # Save Q3
    df_q3.to_csv('loan_portfolio_q3_2024.csv', index=False)
    print("✅ Q3 2024 Portfolio saved: loan_portfolio_q3_2024.csv")
    
    # Q3 Summary
    print("\n" + "="*70)
    print("Q3 2024 PORTFOLIO SUMMARY")
    print("="*70)
    print(f"Total Loans: {len(df_q3):,}")
    print(f"Total Exposure: ${df_q3['outstanding_balance'].sum():,.2f}")
    print(f"Total ECL: ${df_q3['ecl_amount'].sum():,.2f}")
    print(f"Coverage Ratio: {(df_q3['ecl_amount'].sum() / df_q3['outstanding_balance'].sum() * 100):.2f}%")
    print("\nStaging:")
    print(df_q3['ifrs9_stage'].value_counts().sort_index())
    
    # Generate Q4 2024 portfolio (evolved from Q3)
    print("\n" + "="*70)
    print("📊 Generating Q4 2024 Portfolio (December 31, 2024)...")
    print("   Simulating 3 months of portfolio evolution...")
    df_q4 = evolve_to_q4(df_q3)
    
    # Save Q4
    df_q4.to_csv('loan_portfolio_q4_2024.csv', index=False)
    print("✅ Q4 2024 Portfolio saved: loan_portfolio_q4_2024.csv")
    
    # Q4 Summary
    print("\n" + "="*70)
    print("Q4 2024 PORTFOLIO SUMMARY")
    print("="*70)
    print(f"Total Loans: {len(df_q4):,}")
    print(f"Total Exposure: ${df_q4['outstanding_balance'].sum():,.2f}")
    print(f"Total ECL: ${df_q4['ecl_amount'].sum():,.2f}")
    print(f"Coverage Ratio: {(df_q4['ecl_amount'].sum() / df_q4['outstanding_balance'].sum() * 100):.2f}%")
    print("\nStaging:")
    print(df_q4['ifrs9_stage'].value_counts().sort_index())
    
    # Calculate and display changes
    print("\n" + "="*70)
    print("QUARTER-OVER-QUARTER CHANGES (Q3 → Q4)")
    print("="*70)
    
    q3_ecl = df_q3['ecl_amount'].sum()
    q4_ecl = df_q4['ecl_amount'].sum()
    ecl_change = q4_ecl - q3_ecl
    ecl_change_pct = (ecl_change / q3_ecl) * 100
    
    print(f"\n💰 ECL Change:")
    print(f"   Q3: ${q3_ecl:,.2f}")
    print(f"   Q4: ${q4_ecl:,.2f}")
    print(f"   Change: ${ecl_change:,.2f} ({ecl_change_pct:+.2f}%)")
    
    print(f"\n📊 Stage Migration:")
    q3_stages = df_q3['ifrs9_stage'].value_counts().sort_index()
    q4_stages = df_q4['ifrs9_stage'].value_counts().sort_index()
    
    for stage in [1, 2, 3]:
        q3_count = q3_stages.get(stage, 0)
        q4_count = q4_stages.get(stage, 0)
        change = q4_count - q3_count
        change_pct = (change / q3_count * 100) if q3_count > 0 else 0
        print(f"   Stage {stage}: {q3_count:,} → {q4_count:,} ({change:+,} loans, {change_pct:+.1f}%)")
    
    # Detailed migration analysis
    print(f"\n🔄 Loan-Level Migrations:")
    
    # Track individual loan stage changes
    migration_analysis = pd.merge(
        df_q3[['loan_id', 'ifrs9_stage']],
        df_q4[['loan_id', 'ifrs9_stage']],
        on='loan_id',
        suffixes=('_q3', '_q4')
    )
    
    # Count migrations
    stage1_to_2 = len(migration_analysis[(migration_analysis['ifrs9_stage_q3'] == 1) & 
                                         (migration_analysis['ifrs9_stage_q4'] == 2)])
    stage1_to_3 = len(migration_analysis[(migration_analysis['ifrs9_stage_q3'] == 1) & 
                                         (migration_analysis['ifrs9_stage_q4'] == 3)])
    stage2_to_3 = len(migration_analysis[(migration_analysis['ifrs9_stage_q3'] == 2) & 
                                         (migration_analysis['ifrs9_stage_q4'] == 3)])
    stage2_to_1 = len(migration_analysis[(migration_analysis['ifrs9_stage_q3'] == 2) & 
                                         (migration_analysis['ifrs9_stage_q4'] == 1)])
    
    print(f"   Stage 1 → Stage 2: {stage1_to_2:,} loans (deterioration)")
    print(f"   Stage 1 → Stage 3: {stage1_to_3:,} loans (rapid deterioration)")
    print(f"   Stage 2 → Stage 3: {stage2_to_3:,} loans (defaults)")
    print(f"   Stage 2 → Stage 1: {stage2_to_1:,} loans (improvements)")
    
    print("\n" + "="*70)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Upload both CSV files to BigQuery")
    print("2. Build the AI Agent to analyze changes")
    print("3. Ask questions in natural language!")
