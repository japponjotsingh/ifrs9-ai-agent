"""
Macroeconomic Variables for Credit Risk Analysis
Q3 2024 vs Q4 2024

These variables influence default rates and portfolio performance.
Changes in macro conditions explain portfolio deterioration.
"""

import pandas as pd
from datetime import datetime
import json

# =============================================================================
# MACROECONOMIC VARIABLES
# =============================================================================

macro_variables = {
    'Q3_2024': {
        'reporting_date': '2024-09-30',
        'quarter': 'Q3 2024',
        'variables': {
            'bond_yield_10y': 4.25,          # 10-Year Treasury Yield (%)
            'gdp_growth_rate': 2.8,          # Real GDP Growth Rate (% annualized)
            'unemployment_rate': 3.8,        # Unemployment Rate (%)
            'inflation_rate': 2.4,           # CPI Inflation Rate (% YoY)
            'fed_funds_rate': 5.25,          # Federal Funds Rate (%)
            'consumer_confidence': 102.5,    # Consumer Confidence Index
            'housing_price_index': 315.2,    # Case-Shiller Home Price Index
            'credit_spread': 1.85            # Corporate BBB Spread over Treasury (%)
        },
        'economic_outlook': 'Stable - Moderate growth with controlled inflation'
    },
    'Q4_2024': {
        'reporting_date': '2024-12-31',
        'quarter': 'Q4 2024',
        'variables': {
            'bond_yield_10y': 4.65,          # +40 bps (rising rates stress borrowers)
            'gdp_growth_rate': 1.9,          # -0.9 points (economic slowdown)
            'unemployment_rate': 4.3,        # +0.5 points (job market weakening)
            'inflation_rate': 2.8,           # +0.4 points (persistent inflation)
            'fed_funds_rate': 5.50,          # +25 bps (tighter monetary policy)
            'consumer_confidence': 96.8,     # -5.7 points (consumer pessimism)
            'housing_price_index': 310.5,    # -4.7 points (housing market cooling)
            'credit_spread': 2.25            # +40 bps (credit conditions tightening)
        },
        'economic_outlook': 'Deteriorating - Slowing growth, rising unemployment, tighter credit'
    }
}

# =============================================================================
# CALCULATE QUARTER-OVER-QUARTER CHANGES
# =============================================================================

def calculate_changes():
    """Calculate Q3 to Q4 changes"""
    
    q3_vars = macro_variables['Q3_2024']['variables']
    q4_vars = macro_variables['Q4_2024']['variables']
    
    changes = {}
    for var in q3_vars.keys():
        q3_value = q3_vars[var]
        q4_value = q4_vars[var]
        change = q4_value - q3_value
        change_pct = (change / q3_value * 100) if q3_value != 0 else 0
        
        changes[var] = {
            'q3': q3_value,
            'q4': q4_value,
            'absolute_change': round(change, 2),
            'percent_change': round(change_pct, 2)
        }
    
    return changes

# =============================================================================
# RISK IMPACT ANALYSIS
# =============================================================================

def analyze_risk_impact():
    """
    Analyze how macro changes impact credit risk
    Based on economic theory and empirical research
    """
    
    changes = calculate_changes()
    
    risk_impact = {
        'bond_yield_10y': {
            'change': changes['bond_yield_10y']['absolute_change'],
            'direction': 'Negative',
            'impact': 'High',
            'explanation': 'Rising rates increase borrowing costs and debt service burden, leading to higher default risk. +40 bps indicates tighter financial conditions.',
            'expected_pd_impact': '+8-12%'  # Expected increase in PD
        },
        'gdp_growth_rate': {
            'change': changes['gdp_growth_rate']['absolute_change'],
            'direction': 'Negative',
            'impact': 'High',
            'explanation': 'Economic slowdown from 2.8% to 1.9% reduces household income and business revenues, increasing default probability.',
            'expected_pd_impact': '+10-15%'
        },
        'unemployment_rate': {
            'change': changes['unemployment_rate']['absolute_change'],
            'direction': 'Negative',
            'impact': 'Critical',
            'explanation': 'Rising unemployment (+0.5 points) is the strongest predictor of consumer loan defaults. Job losses directly impair repayment ability.',
            'expected_pd_impact': '+15-20%'
        },
        'inflation_rate': {
            'change': changes['inflation_rate']['absolute_change'],
            'direction': 'Negative',
            'impact': 'Medium',
            'explanation': 'Persistent inflation erodes purchasing power and strains household budgets, particularly for low-income borrowers.',
            'expected_pd_impact': '+5-8%'
        },
        'consumer_confidence': {
            'change': changes['consumer_confidence']['absolute_change'],
            'direction': 'Negative',
            'impact': 'Medium',
            'explanation': 'Declining confidence leads to reduced spending and increased savings, but also signals economic anxiety.',
            'expected_pd_impact': '+3-5%'
        },
        'credit_spread': {
            'change': changes['credit_spread']['absolute_change'],
            'direction': 'Negative',
            'impact': 'High',
            'explanation': 'Widening spreads (+40 bps) indicate tighter credit availability and increased market-perceived default risk.',
            'expected_pd_impact': '+7-10%'
        }
    }
    
    return risk_impact

# =============================================================================
# EXPORT TO CSV FOR BIGQUERY
# =============================================================================

def create_macro_table():
    """Create a table format for BigQuery"""
    
    rows = []
    
    for quarter_key in ['Q3_2024', 'Q4_2024']:
        quarter_data = macro_variables[quarter_key]
        
        row = {
            'reporting_date': quarter_data['reporting_date'],
            'quarter': quarter_data['quarter'],
            'economic_outlook': quarter_data['economic_outlook']
        }
        
        # Add all variables
        row.update(quarter_data['variables'])
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df

# =============================================================================
# EXPORT TO JSON FOR AI AGENT
# =============================================================================

def create_macro_context():
    """Create narrative context for AI Agent"""
    
    changes = calculate_changes()
    risk_impact = analyze_risk_impact()
    
    context = {
        'summary': 'Macroeconomic conditions deteriorated significantly from Q3 to Q4 2024',
        'key_drivers': [
            {
                'variable': 'Unemployment Rate',
                'change': f"+{changes['unemployment_rate']['absolute_change']} points to {macro_variables['Q4_2024']['variables']['unemployment_rate']}%",
                'impact': 'Critical - Primary driver of consumer default risk'
            },
            {
                'variable': 'GDP Growth',
                'change': f"{changes['gdp_growth_rate']['absolute_change']} points to {macro_variables['Q4_2024']['variables']['gdp_growth_rate']}%",
                'impact': 'High - Economic slowdown reduces repayment capacity'
            },
            {
                'variable': '10-Year Yield',
                'change': f"+{changes['bond_yield_10y']['absolute_change']} bps to {macro_variables['Q4_2024']['variables']['bond_yield_10y']}%",
                'impact': 'High - Rising rates increase debt service costs'
            }
        ],
        'portfolio_implications': [
            'Expected PD increase: 15-25% based on macro deterioration',
            'Consumer products (Personal Loans, Credit Cards) most vulnerable',
            'SME Loans at risk due to economic slowdown',
            'Mortgages somewhat insulated but facing rate pressure'
        ],
        'q3_to_q4_changes': changes,
        'risk_impact_analysis': risk_impact
    }
    
    return context

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    
    print("="*70)
    print("MACROECONOMIC VARIABLES - Q3 vs Q4 2024")
    print("="*70)
    
    # Display Q3 conditions
    print("\n📊 Q3 2024 (September 30):")
    print(f"   Economic Outlook: {macro_variables['Q3_2024']['economic_outlook']}")
    for var, value in macro_variables['Q3_2024']['variables'].items():
        print(f"   {var}: {value}")
    
    # Display Q4 conditions
    print("\n📊 Q4 2024 (December 31):")
    print(f"   Economic Outlook: {macro_variables['Q4_2024']['economic_outlook']}")
    for var, value in macro_variables['Q4_2024']['variables'].items():
        print(f"   {var}: {value}")
    
    # Calculate changes
    print("\n" + "="*70)
    print("QUARTER-OVER-QUARTER CHANGES")
    print("="*70)
    
    changes = calculate_changes()
    
    for var, data in changes.items():
        direction = "↑" if data['absolute_change'] > 0 else "↓"
        print(f"\n{var}:")
        print(f"   Q3: {data['q3']} → Q4: {data['q4']}")
        print(f"   Change: {direction} {abs(data['absolute_change'])} ({data['percent_change']:+.1f}%)")
    
    # Risk impact
    print("\n" + "="*70)
    print("CREDIT RISK IMPACT ANALYSIS")
    print("="*70)
    
    risk_impact = analyze_risk_impact()
    
    for var, impact_data in risk_impact.items():
        if impact_data['impact'] in ['Critical', 'High']:
            print(f"\n⚠️  {var.upper()}")
            print(f"   Change: {impact_data['change']}")
            print(f"   Impact: {impact_data['impact']}")
            print(f"   Expected PD Impact: {impact_data['expected_pd_impact']}")
            print(f"   {impact_data['explanation']}")
    
    # Export to CSV
    df_macro = create_macro_table()
    df_macro.to_csv('macroeconomic_variables.csv', index=False)
    print("\n✅ Exported: macroeconomic_variables.csv")
    
    # Export context for AI
    macro_context = create_macro_context()
    with open('macro_context.json', 'w') as f:
        json.dump(macro_context, f, indent=2)
    print("✅ Exported: macro_context.json")
    
    # Display AI Agent prompt
    print("\n" + "="*70)
    print("AI AGENT CONTEXT")
    print("="*70)
    print("\nKey Message for AI:")
    print(macro_context['summary'])
    print("\nPortfolio Implications:")
    for implication in macro_context['portfolio_implications']:
        print(f"  • {implication}")
    
    print("\n" + "="*70)
    print("✅ MACRO VARIABLES READY FOR AI ANALYSIS!")
    print("="*70)
    print("\nThe AI Agent can now:")
    print("  • Correlate macro changes with portfolio deterioration")
    print("  • Explain WHY ECL increased (unemployment, GDP, rates)")
    print("  • Provide economic context for risk changes")
    print("  • Make forward-looking recommendations")
