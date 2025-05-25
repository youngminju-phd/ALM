import numpy as np
import pandas as pd

class ALM:
    """
    Asset and Liability Management (ALM) class for projecting and reporting
    on assets and liabilities over the lifetime of insurance contracts.
    """
    # Class-level defaults (can be overridden per instance)
    opening_year = 2020  # Projection start year

    # --------------------------------------------------------------------------
    # Contractual management data (insurance portfolio defaults)
    insured_number = 1        # Number of contracts
    insured_premium = 1000    # Premium amount per contract
    average_age = 50          # Average policyholder age
    contracts_maturity = 10   # Contract horizon in years

    # Charges and fees
    charges_rate = 0.0          # Proportional charge rate
    fee_pct_premium = 0.0       # Fee as % of premium
    fixed_fee = 0.0             # Fixed fee amount
    fixed_cost_inflation = 0.0  # Inflation rate for fixed costs
    redemption_rates = 0.3      # Surrender rate

    # Contract revaluation parameters
    guaranteed_minimum_rate = 0.0   # GMDB floor rate
    regu_distrib_tech_res = 0.90    # % to technical reserves
    regu_distrib_fin_prod = 0.85    # % to financial products
    contra_distrib_fin_prod = 0.90  # Contrarian distribution
    repurchase_rate = 0.0           # Policy repurchase rate
    initial_fp_percentage = 0.0     # Initial allocation to financial products
    risk_adjustment = 0            # Risk adjustment amount
    capital_reserve = 0            # Capital reserve
    ppe = 0                        # Property, plant & equipment value

    # Taxes
    tax_rate = 0.0  # Corporate tax rate

    # Bond portfolio defaults
    nominal = 100           # Face value per bond
    coupon_rate = 0.10      # Annual coupon
    bonds_initial_mv = 15   # Initial market value
    bonds_initial_vnc = 10  # Initial book value
    alloc_bonds = 0         # Allocation to bonds
    alloc_stocks = 1        # Allocation to stocks
    alloc_cash = 0          # Allocation to cash

    # Stock portfolio defaults
    stocks_initial_mv = 105  # Initial market value per share
    stocks_initial_vnc = 100 # Initial book value

    def __init__(self, *initial_data, **kwargs):
        """
        Initialize ALM instance, overriding defaults via dicts or kwargs.
        Builds a projection timeline `self.years` of length contracts_maturity.
        """
        # Override attributes from provided dicts
        for dictionary in initial_data:
            for key, val in dictionary.items():
                setattr(self, key, val)
        # Override from keyword args
        for key, val in kwargs.items():
            setattr(self, key, val)

        # Generate projection years array
        self.years = np.arange(self.opening_year,
                               self.opening_year + self.contracts_maturity)

    def set_default(self):
        """
        Reset instance attributes to class-level defaults.
        Note: ensure class defaults and method defaults stay consistent.
        """
        # Reset all simple attributes from the class
        for attr, val in ALM.__dict__.items():
            if not attr.startswith('__') and not callable(val):
                setattr(self, attr, val)

    def load_parameters_from_file(self, file_name):
        """
        Placeholder: load scalar parameters (e.g., JSON) for ALM settings.
        Implementation needed based on file format.
        """
        raise NotImplementedError("load_parameters_from_file is not implemented")

    def load_data_from_file(self, file_name, attr_name):
        """
        Load a 1×T CSV (no header) and assign first T values to attribute `attr_name`.
        T = self.contracts_maturity. Logs error if read fails.
        """
        try:
            data = pd.read_csv(file_name, header=None).values[0, :self.contracts_maturity]
            setattr(self, attr_name, data)
        except Exception as e:
            # Fix: include exception message correctly
            print(f"Problem reading {file_name} for {attr_name}: {e}")

    def afficher_data(self, attr_name):
        """
        Print the contents of the specified array attribute.
        """
        if hasattr(self, attr_name):
            print(f"{attr_name} = {getattr(self, attr_name)}")
        else:
            print(f"Attribute {attr_name} not found on ALM instance.")

    def report_discount_rate(self):
        """
        Calculate discount metrics:
          - forward rates (provided externally)
          - liquidity premium (provided externally)
          - combined forward rate
          - deflator series
        Returns a DataFrame with years as columns.
        Requires: self.forward_rates and self.liquidity_premium arrays.
        """
        # Ensure inputs exist
        if not hasattr(self, 'forward_rates') or not hasattr(self, 'liquidity_premium'):
            raise AttributeError("forward_rates and liquidity_premium must be loaded first")

        n = len(self.forward_rates)
        # Initialize deflator
        self.deflator = np.ones(n)
        # Recursively compute deflator: deflator[t] = deflator[t-1]/(1 + fwd_rate[t])
        for t in range(1, n):
            self.deflator[t] = self.deflator[t-1] / (1 + self.forward_rates[t])

        # Build report
        df = pd.DataFrame([
            self.forward_rates,
            self.liquidity_premium,
            self.forward_rates + self.liquidity_premium,
            self.deflator
        ],
        index=['forward rate 1Y', 'liquidity premium', 'forward+liquidity', 'deflator'],
        columns=self.years)
        return df

    def report_neutral_risk(self):
        """
        Using bond market values, derive a neutral risk factor that equates
        discounted bond cash flows to observed market value.
        Requires: self.deflator from report_discount_rate.
        """
        # Ensure deflator exists
        if not hasattr(self, 'deflator'):
            raise AttributeError("deflator must be computed via report_discount_rate first")

        n = len(self.deflator)
        # 1. Bond cash flows: coupons and redemption
        bonds_cf = np.zeros(n)
        bonds_cf[1:] = self.nominal * self.coupon_rate
        bonds_cf[-1] += self.nominal

        # 2. Discount cash flows
        disc_cf = np.zeros(n)
        for t in range(1, n):
            disc_cf[t] = (bonds_cf[t:] * self.deflator[t:]).sum()

        # 3. Neutral risk factor
        self.neutral_risk_factor = np.zeros(n)
        if disc_cf[1] != 0:
            self.neutral_risk_factor[1:] = self.bonds_initial_mv / disc_cf[1]

        # Validate equivalence: present value vs market
        neutral_cf = bonds_cf * self.neutral_risk_factor[1]
        pv_neutral = (neutral_cf[1:] * self.deflator[1:]).sum()
        if not np.isclose(pv_neutral, self.bonds_initial_mv):
            raise ValueError("Neutral risk check failed: PV != MV")

        # Create DataFrame report
        df = pd.DataFrame([
            bonds_cf,
            disc_cf,
            self.neutral_risk_factor,
            neutral_cf
        ],
        index=['bonds CF','discounted CF','neutral factor','neutral CF'],
        columns=self.years)
        return df

    # --------------------------------------------------------------------------
    # Placeholder methods: need implementation for full ALM workflow
    def assets_variables_projection(self):
        """
        Project asset book/market values over time (bonds, stocks, cash).
        Incomplete: implement depreciation, market value, quantities, etc.
        """
        # TODO: complete bond VNC/MV projection, stock projection, cash
        raise NotImplementedError("assets_variables_projection not implemented")

    def total_assets_booked_value(self):
        """
        Sum all asset classes by book value.
        """
        raise NotImplementedError("total_assets_booked_value not implemented")

    def total_assets_market_value(self):
        """
        Sum all asset classes by market value.
        """
        raise NotImplementedError("total_assets_market_value not implemented")

    def variation_pmvl_reference(self):
        """
        Calculate variation in portfolio market value vs reference scenario.
        """
        raise NotImplementedError("variation_pmvl_reference not implemented")

    # Liability cash flow projection placeholders
    def cash_flows_liabilities(self):
        """
        Project liability cash flows: benefits, reserves, provisions.
        To implement: inputs, benefit calc, gross/net revaluations, PPE, provisions.
        """
        raise NotImplementedError("cash_flows_liabilities not implemented")

    def calculation_BEL(self):
        """
        Calculate Best Estimate Liability (BEL) from projected liabilities.
        """
        raise NotImplementedError("calculation_BEL not implemented")

    def local_gaap_pnl(self):
        """
        Compute P&L under local GAAP: realized/unrealized gains, interest, etc.
        """
        raise NotImplementedError("local_gaap_pnl not implemented")

    def value_in_force(self):
        """
        Compute Value in Force (VIF) for in-force business.
        """
        raise NotImplementedError("value_in_force not implemented")

    def total_value_options_garantees(self):
        """
        Sum value of options & guarantees embedded in contracts.
        """
        raise NotImplementedError("total_value_options_garantees not implemented")

    # Balance sheet calibration placeholders
    def total_liabilities_vnc(self):
        """
        Sum of liabilities at book value (VNC).
        """
        raise NotImplementedError("total_liabilities_vnc not implemented")

    def total_liabilities_vm(self):
        """
        Sum of liabilities at market value (VM).
        """
        raise NotImplementedError("total_liabilities_vm not implemented")
