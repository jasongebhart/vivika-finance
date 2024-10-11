import investment_module

# Timespan and Rate
interest_rate = 0.07
years = 9
# Retirement
retirement_balance = 7721528
initial_contribution = 0
increase_contribution = 3000
# Expenses and Gains
annual_surplus = 0 #90000  # Initial annual contribution
gains = [10000, 10000, 15000, 150000, 15000, 0, 0, 0, 0]
yearly_expense = 0 # 181000  # Adjust this value as needed
college_expenses = [0, 0, 0, 0, 80000, 160000, 160000, 80000, 80000]
highschool_expenses = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# Calculate total expenses for each year
expenses = [a + b for a, b in zip(college_expenses, highschool_expenses)]
# expenses_by_year = [0, 0, 0, 0, 0, 0, 0, 0, 0]

retirement_value = investment_module.calculate_future_value(retirement_balance, 0, 0, interest_rate, years)
balance_with_expenses = investment_module.calculate_balance(retirement_balance, interest_rate, years, annual_surplus=annual_surplus, gains=gains, expenses=expenses, yearly_expense=yearly_expense)

# Print the yearly net gain
print(f"Yearly Gain: {annual_surplus}")
print(f"retirement_value")
print(f"{' Investment Principal':<25} ${int(retirement_value):,}")
print(f"{' Investment Principal':<25} ${int(balance_with_expenses):,}")