import os
from collections import OrderedDict
from typing import List, Union, Optional
import pandas as pd


class StudentLoanCalculator:
    """"""

    def __init__(self, loan_amount_eur: Union[float, int], last_study_year: int, education_level: str,
                 monthly_payment_amount_eur: Optional[Union[float, int]], repayment_rules: dict, interest_rates: dict,
                 payment_scheme: List, preliminary_phase_term: int = 2, fixed_interest_term: int = 5):
        """"""
        self.loan_amount_eur = loan_amount_eur
        self.last_study_year = last_study_year
        self.education_level = education_level
        self.monthly_payment_amount_eur = monthly_payment_amount_eur
        self.repayment_rules = repayment_rules
        self.interest_rates = interest_rates
        self.payment_scheme = payment_scheme
        self.preliminary_phase_term = preliminary_phase_term
        self.start_loan_period = self.last_study_year + 1
        self.start_repayment_period = self.start_loan_period + self.preliminary_phase_term
        self.fixed_interest_term = fixed_interest_term
        self.total_sum_interest = 0

    def fill_payment_rule(self):
        """"""
        if not self.payment_scheme:
            if self.last_study_year >= 2015 and self.education_level == 'WO':
                self.payment_scheme = [2012, 2018]
            else:
                self.payment_scheme = [2012]

    def fill_repayment_rules(self):
        """"""
        if not self.repayment_rules:
            self.repayment_rules = {
                2012: {'term': 15},
                2018: {'term': 35},
            }

    def fill_interest_rates(self):
        """"""
        if not self.interest_rates:
            self.interest_rates = OrderedDict([
                (2006, {2012: 2.74, 2018: 2.74}),
                (2007, {2012: 3.70, 2018: 3.70}),
                (2008, {2012: 4.17, 2018: 4.17}),
                (2009, {2012: 3.58, 2018: 3.58}),
                (2010, {2012: 2.39, 2018: 2.39}),
                (2011, {2012: 1.50, 2018: 1.50}),
                (2012, {2012: 1.39, 2018: 1.39}),
                (2013, {2012: 0.60, 2018: 0.60}),
                (2014, {2012: 0.81, 2018: 0.81}),
                (2015, {2012: 0.12, 2018: 0.12}),
                (2016, {2012: 0.01, 2018: 0.01}),
                (2017, {2012: 0.00, 2018: 0.00}),
                (2018, {2012: 0.00, 2018: 0.00}),
                (2019, {2012: 0.00, 2018: 0.00}),
                (2020, {2012: 0.00, 2018: 0.00}),
                (2021, {2012: 0.00, 2018: 0.00}),
                (2022, {2012: 0.00, 2018: 0.00}),
                (2023, {2012: 1.78, 2018: 0.46}),
                (2024, {2012: 1.78, 2018: 2.0}),
                (2025, {2012: 1.78, 2018: 2.5}),
                (2026, {2012: 1.78, 2018: 3.0}),
                (2027, {2012: 1.78, 2018: 3.5}),
                (2028, {2012: 1.78, 2018: 4.0}),
                (2029, {2012: 1.78, 2018: 4.5}),
            ])

    def fill_monthly_payment_amount_eur(self):
        """"""
        pass

    def calculate_loan_term(self, payment_scheme) -> range:
        """Calculates the year range for the loan term."""
        return range(self.start_loan_period, self.last_study_year + self.repayment_rules[payment_scheme]['term'])

    def calculate_yearly_interest_rate(self, year) -> dict:
        """Computes the yearly interest rate in percentage based on the year."""
        return self.interest_rates.get(
            year, self.interest_rates.get(
                list(self.interest_rates.keys())[-1]  # take last year's interest rate
            )
        )

    def run(self):
        """main function."""

        interest_rate_year = self.start_loan_period

        for payment_scheme in self.payment_scheme:
            for idx, year in enumerate(self.calculate_loan_term(payment_scheme=payment_scheme)):

                if (year - self.start_loan_period) % 5 == 0:
                    # sets the interest rate for a five-year period
                    interest_rate_year = year

                yearly_interest_rates = self.calculate_yearly_interest_rate(
                    interest_rate_year)  # @todo dit kan denk ik een lijst zijn nu
                yearly_interest_rate = (yearly_interest_rates[payment_scheme] / 100)

                if self.start_repayment_period > year:
                    # you don't start paying back until 2 years after loan_start_period
                    monthly_payment_amount_eur = 0
                else:
                    monthly_payment_amount_eur = self.monthly_payment_amount_eur * (1 + (yearly_interest_rate * 20))

                monthly_interest_rate = (yearly_interest_rate / 12)
                yearly_interest_eur = 0
                for month in range(12):
                    monthly_interest_eur = self.loan_amount_eur * monthly_interest_rate
                    self.loan_amount_eur += monthly_interest_eur - monthly_payment_amount_eur
                    yearly_interest_eur += monthly_interest_eur

                self.total_sum_interest += yearly_interest_eur

                print(f"{idx}, {year}: original loan amount: {self.loan_amount_eur}, "
                      f"original monthly payment: {self.monthly_payment_amount_eur}, "
                      f"new monthly payment: {monthly_payment_amount_eur}, "
                      f"yearly payment: {monthly_payment_amount_eur * 12}, "
                      f"yearly interest: {yearly_interest_eur} at rate {yearly_interest_rates[payment_scheme]} %, "
                      )

                if self.loan_amount_eur <= 0.0:
                    print("loan paid off")
                    break

            print(f"\ntotal sum interest paid: {self.total_sum_interest}")


def main():
    loan_amount_eur = 62169.17
    last_study_year = 2020
    start_loan_period = last_study_year + 1
    education_level = 'WO'  # or 'MBO'
    monthly_payment_amount_eur = 160.25  # 160.25 or 148.02   # @todo: calculcate that on the government website or build it in this app ourselves
    repayment_rules = {
        2012: {'term': 15},
        2018: {'term': 35},
    }

    interest_rates = OrderedDict([
        (2006, {2012: 2.74, 2018: 2.74}),
        (2007, {2012: 3.70, 2018: 3.70}),
        (2008, {2012: 4.17, 2018: 4.17}),
        (2009, {2012: 3.58, 2018: 3.58}),
        (2010, {2012: 2.39, 2018: 2.39}),
        (2011, {2012: 1.50, 2018: 1.50}),
        (2012, {2012: 1.39, 2018: 1.39}),
        (2013, {2012: 0.60, 2018: 0.60}),
        (2014, {2012: 0.81, 2018: 0.81}),
        (2015, {2012: 0.12, 2018: 0.12}),
        (2016, {2012: 0.01, 2018: 0.01}),
        (2017, {2012: 0.00, 2018: 0.00}),
        (2018, {2012: 0.00, 2018: 0.00}),
        (2019, {2012: 0.00, 2018: 0.00}),
        (2020, {2012: 0.00, 2018: 0.00}),
        (2021, {2012: 0.00, 2018: 0.00}),
        (2022, {2012: 0.00, 2018: 0.00}),
        (2023, {2012: 1.78, 2018: 0.46}),
        # (2024, {2012: 1.78, 2018: 4}),
        # (2025, {2012: 1.78, 2018: 2.5}),
        # (2026, {2012: 1.78, 2018: 3.0}),
        # (2027, {2012: 1.78, 2018: 3.5}),
        # (2028, {2012: 1.78, 2018: 4.0}),
        # (2029, {2012: 1.78, 2018: 4.5}),
    ])

    student_loan_calculator = StudentLoanCalculator(loan_amount_eur=loan_amount_eur, last_study_year=last_study_year,
                                                    education_level=education_level,
                                                    monthly_payment_amount_eur=monthly_payment_amount_eur,
                                                    repayment_rules=repayment_rules, interest_rates=interest_rates,
                                                    payment_scheme=[2018])

    if last_study_year < 2006:
        print("ValueError: no data.")
    else:
        student_loan_calculator.run()


def monthly_payment(principle, time, rate):
    """Calculates monthly payment consisting of monthly principle amount and monthly interest amount."""
    if rate == 0.0:
        payment = principle / time
    else:
        payment = principle * (rate / (1 - (1 + rate) ** -time))

    return payment


if __name__ == '__main__':

    p = 62169.17  # amount in euros
    t = 35 * 12  # time in months (years*months)
    ir_rate = 0.46  # monthly interest rate

    # ir_rates = [ir_rate, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0]
    ir_rates = [ir_rate] * 7
    ir_rates = [(i / 100) / 12 for i in ir_rates]

    beginning_balance = p
    monthly_amortization = []
    for idx, ir in enumerate(ir_rates):
        payment = monthly_payment(principle=beginning_balance, time=t, rate=ir)

        for month in range(1, t + 1):
            """
            Step 1: H = P x J, this is your current monthly interest
            Step 2: C = M - H, this is your monthly payment minus your monthly interest, so it is the amount of principal you pay for that month
            Step 3: Q = P - C, this is the new balance of your principal of your loan.
            Step 4: Set P equal to Q and go back to Step 1: You loop around until the value Q (and hence P) goes to zero.
            """
            interest = beginning_balance * ir
            principle_amount = payment - interest
            ending_balance = beginning_balance - principle_amount

            data = {
                'interest_period': idx,
                'month': month,
                'monthly_payment': payment,
                'beginning_balance': beginning_balance,
                'monthly_principle': principle_amount,
                'interest': interest,
                'ending_balance': ending_balance
            }
            monthly_amortization.append(data)

            beginning_balance = ending_balance

            if month % 60 == 0:
                # five years have passed, new interest rates incoming
                t -= 60
                break

    amortization_df = pd.DataFrame(monthly_amortization)
    amortization_df.to_excel('./Medium/Loan/amortization.xlsx', index=False)
    amortization_df.to_csv('./Medium/Loan/amortization.csv', index=False)

    # @todo: make a nice graph

# Regels na 2012 € 357,47
# Regels na 2018 € 160,25


# reminder in oktober nieuwe rentes invoeren
