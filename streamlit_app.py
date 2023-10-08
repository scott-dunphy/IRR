import numpy as np
import numpy_financial as npf
import streamlit as st

class ApartmentInvestment:
    def __init__(self, unit_count, purchase_price, market_rent_per_unit, rent_growth_per_year, 
                 year_1_expense_ratio, expense_growth_per_year, capex_per_unit, exit_cap_rate):
        self.unit_count = unit_count
        self.purchase_price = purchase_price
        self.market_rent_per_unit = market_rent_per_unit
        self.rent_growth_per_year = rent_growth_per_year
        self.year_1_expense_ratio = year_1_expense_ratio
        self.expense_growth_per_year = expense_growth_per_year
        self.capex_per_unit = capex_per_unit
        self.exit_cap_rate = exit_cap_rate
    
    def calculate_irr(self):
        # Define variables and arrays to store calculations
        revenue = np.zeros(12)
        expenses = np.zeros(12)
        capex = np.zeros(12)
        net_operating_income = np.zeros(12)
        net_cash_flow = np.zeros(11)

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
        # Step 9: Calculate IRR
        irr = npf.irr(net_cash_flow)
        return irr

st.title('Apartment Investment IRR Calculator')

# Sidebar with sliders for each input parameter
st.sidebar.header('Input Parameters')
unit_count = st.sidebar.number_input('Unit Count', min_value=1, max_value=1000, value=100, step=1)
purchase_price = st.sidebar.slider('Purchase Price', min_value=10000000, max_value=100000000, value=25000000, step=1000000)
market_rent_per_unit = st.sidebar.slider('Market Rent per Unit', min_value=500, max_value=5000, value=2500, step=50)
rent_growth_per_year = st.sidebar.slider('Rent Growth per Year (%)', min_value=0.0, max_value=10.0, value=3.0, step=0.25) / 100
year_1_expense_ratio = st.sidebar.slider('Year 1 Expense Ratio (%)', min_value=0.0, max_value=100.0, value=50.0, step=1) / 100
expense_growth_per_year = st.sidebar.slider('Expense Growth per Year (%)', min_value=0.0, max_value=10.0, value=2.0, step=0.25) / 100
capex_per_unit = st.sidebar.slider('CAPEX per Unit', min_value=100, max_value=10000, value=250, step=100)
exit_cap_rate = st.sidebar.slider('Exit Cap Rate (%)', min_value=1.0, max_value=10.0, value=5.0, step=0.25) / 100

# Create instance of ApartmentInvestment class with input parameters
investment = ApartmentInvestment(unit_count, purchase_price, market_rent_per_unit, rent_growth_per_year,
                                year_1_expense_ratio, expense_growth_per_year, capex_per_unit, exit_cap_rate)

# Calculate IRR and display result
investment_irr = investment.calculate_irr()
st.header(f'The calculated IRR is: {investment_irr * 100:.2f}%')
