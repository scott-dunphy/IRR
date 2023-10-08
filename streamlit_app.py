import numpy as np
import numpy_financial as npf
import streamlit as st
import pandas as pd

class ApartmentInvestment:
    def __init__(self, unit_count, purchase_price, market_rent_per_unit, rent_growth_per_year, 
                 year_1_expense_ratio, expense_growth_per_year, capex_per_unit, exit_cap_rate,
                 loan_to_value, interest_rate, term, flag_io):
        self.unit_count = unit_count
        self.purchase_price = purchase_price
        self.market_rent_per_unit = market_rent_per_unit
        self.rent_growth_per_year = rent_growth_per_year
        self.year_1_expense_ratio = year_1_expense_ratio
        self.expense_growth_per_year = expense_growth_per_year
        self.capex_per_unit = capex_per_unit
        self.exit_cap_rate = exit_cap_rate
        self.loan_to_value = loan_to_value
        self.interest_rate = interest_rate
        self.term = term
        self.flag_io = flag_io
    
    def calculate_irr(self):
        # Define variables and arrays to store calculations
        revenue = np.zeros(12)
        expenses = np.zeros(12)
        capex = np.zeros(12)
        net_operating_income = np.zeros(12)
        net_cash_flow = np.zeros(11)
        final_cash_flows = np.zeros(11)
    
        # Step 1: Year 1 Revenue
        revenue[1] = self.market_rent_per_unit * self.unit_count * 12
        # Step 2: Year 1 Expenses
        expenses[1] = revenue[1] * self.year_1_expense_ratio
        # Step 3: Grow Revenue and Expenses
        for year in range(2, 12):
            revenue[year] = revenue[year - 1] * (1 + self.rent_growth_per_year)
            expenses[year] = expenses[year - 1] * (1 + self.expense_growth_per_year)
        # Step 4: Net Operating Income
        net_operating_income = revenue - expenses
        # Step 5 and 6: CAPEX and growth
        capex[1] = self.capex_per_unit * self.unit_count
        for year in range(2, 12):
            capex[year] = capex[year - 1] * (1 + self.expense_growth_per_year)
        # Step 7: Net Cash Flow for Year 0 to Year 10
        net_cash_flow[0] = -self.purchase_price
        net_cash_flow[1:10] = net_operating_income[1:10] - capex[1:10]
        # Step 8: Add Reversion Value to Year 10 Cash Flow (calculated from Year 11 NOI)
        reversion_value = net_operating_income[11] / self.exit_cap_rate
        net_cash_flow[10] = net_operating_income[10] - capex[10] + reversion_value

        # Calculate Debt Service
        beginning_balance, _, _, debt_service, ending_balance = self.calculate_debt_service()

        # Adjust Net Cash Flow for Debt Service from Year 1 to Year 10
        ncf_after_debt = net_cash_flow.copy()

        ncf_after_debt[1:11] -= debt_service[1:11]
    
        # Add beginning debt balance from Year 0 as positive cash inflow
        final_cash_flows[0] = ncf_after_debt[0] + beginning_balance[0]
    
        # Adjust Net Cash Flow for remaining years
        final_cash_flows[1:10] = ncf_after_debt[1:10]
    
        # Add ending debt balance from Year 10 as negative cash outflow
        final_cash_flows[10] = ncf_after_debt[10] - ending_balance[10]
    
        # Calculate Leveraged IRR based on final cash flows
        levered_irr = npf.irr(final_cash_flows)
    
        # Step 9: Calculate IRR
        irr = npf.irr(net_cash_flow)
        
        # Additional calculations
        total_contributions = np.sum(net_cash_flow[net_cash_flow < 0])  # Sum of all negative cash flows (cash outflows)
        total_distributions = np.sum(net_cash_flow[net_cash_flow > 0])  # Sum of all positive cash flows (cash inflows)
        total_profit = total_distributions + total_contributions  # Total profit (or loss if negative)
        investment_multiple = total_distributions / abs(total_contributions)  # Total distributions divided by total contributions
        
        return irr, total_contributions, total_distributions, total_profit, investment_multiple, levered_irr, debt_service

    def calculate_debt_service(self):
            # Step 1: Calculate loan balance
            loan_balance_initial = self.purchase_price * self.loan_to_value
            
            # Initialize lists to store calculations
            beginning_loan_balance = np.zeros(11)
            interest_expense = np.zeros(11)
            principal_payments = np.zeros(11)
            debt_service = np.zeros(11)
            ending_loan_balance = np.zeros(11)
            
            # Step 3: Set Year 0 beginning and ending loan balance
            beginning_loan_balance[0] = loan_balance_initial
            ending_loan_balance[0] = loan_balance_initial
            
            # Calculate debt service for each year
            for year in range(1, 11):
                # Step 4: Set beginning loan balance for the year
                beginning_loan_balance[year] = ending_loan_balance[year - 1]
                
                # Step 5: Calculate debt service
                if self.flag_io == 1:
                    debt_service[year] = beginning_loan_balance[year] * self.interest_rate
                else:
                    # Amortizing payment calculation using the PMT formula
                    debt_service[year] = npf.pmt(self.interest_rate, self.term, -loan_balance_initial, 0)
                
                # Step 6: Calculate interest expense
                interest_expense[year] = beginning_loan_balance[year] * self.interest_rate
                
                # Step 7: Calculate principal payments
                principal_payments[year] = debt_service[year] - interest_expense[year]
                
                # Step 8: Calculate ending loan balance
                ending_loan_balance[year] = beginning_loan_balance[year] - principal_payments[year]
            
            return beginning_loan_balance, interest_expense, principal_payments, debt_service, ending_loan_balance


st.title('Apartment Investment IRR Calculator')

# Sidebar with sliders for each input parameter
with st.sidebar.expander("Investment Inputs"):
    unit_count = st.number_input('Unit Count', min_value=1, max_value=1000, value=100, step=1)
    purchase_price = st.slider('Purchase Price', min_value=10000000, max_value=100000000, value=25000000, step=1000000)
    market_rent_per_unit = st.slider('Market Rent per Unit', min_value=500, max_value=5000, value=2500, step=50)
    rent_growth_per_year = st.slider('Rent Growth per Year (%)', min_value=0.0, max_value=10.0, value=3.0, step=0.25) / 100
    year_1_expense_ratio = st.slider('Year 1 Expense Ratio (%)', min_value=0.0, max_value=100.0, value=50.0, step=1.0) / 100
    expense_growth_per_year = st.slider('Expense Growth per Year (%)', min_value=0.0, max_value=10.0, value=2.0, step=0.25) / 100
    capex_per_unit = st.slider('CAPEX per Unit', min_value=100, max_value=1000, value=250, step=50)
    exit_cap_rate = st.slider('Exit Cap Rate (%)', min_value=1.0, max_value=10.0, value=5.0, step=0.25) / 100

with st.sidebar.expander("Debt Inputs"):
    loan_to_value = st.slider('Loan to Value Ratio (%)', min_value=0.0, max_value=80.0, value=55.0, step=5.0) / 100
    interest_rate = st.slider('Interest Rate (%)', min_value=0.0, max_value=10.0, value=6.25, step=0.25) / 100
    term = st.slider('Loan Term (Years)', min_value=1, max_value=30, value=30, step=1)
    flag_io = st.selectbox('Interest Only Period?', [0, 1])



# Create instance of ApartmentInvestment class with input parameters
investment = ApartmentInvestment(unit_count, purchase_price, market_rent_per_unit, rent_growth_per_year,
                                year_1_expense_ratio, expense_growth_per_year, capex_per_unit, exit_cap_rate,
                                loan_to_value, interest_rate, term, flag_io
                                )

# Calculate IRR and other metrics, then display results
investment_irr, total_contributions, total_distributions, total_profit, investment_multiple, levered_irr, debt_service = investment.calculate_irr()

# Create a DataFrame
data = {
    'Metric': ['IRR', 'Leveraged IRR', 'Total Contributions (Cash Outflows)', 'Total Distributions (Cash Inflows)', 'Total Profit', 'Investment Multiple'],
    'Value': [f"{investment_irr * 100:.2f}%", f"{levered_irr * 100:.2f}%", f"${total_contributions:,.2f}", f"${total_distributions:,.2f}", f"${total_profit:,.2f}", f"{investment_multiple:.2f}x"]
}
df = pd.DataFrame(data)

# Display the DataFrame in Streamlit
st.table(df)


