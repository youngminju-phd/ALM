"""
Asset and Liability Management (ALM) Engine

This module provides a comprehensive ALM framework for insurance companies and financial
institutions. The ALM class implements sophisticated asset and liability modeling,
cash flow projections, and risk analysis capabilities.

Key Features:
- Complete asset and liability modeling with realistic industry parameters
- Advanced discount rate calculations using bootstrapping methodology
- Comprehensive neutral risk analysis with validation frameworks
- Multi-asset portfolio management (bonds, stocks, cash)
- Liability cash flow modeling with mortality and surrender rates
- Professional reporting suite with four comprehensive report types
- 10-year projection capabilities with scenario analysis

The framework supports:
- Insurance portfolio management with configurable parameters
- Market data integration (forward rates, liquidity premiums, mortality tables)
- Risk-adjusted calculations with volatility analysis
- Regulatory compliance (Best Estimate Liabilities, risk margins)
- Advanced analytics (Value in Force, Options & Guarantees valuation)

Author: ALM Development Team
Version: 2.0
License: MIT
"""

import numpy as np
import pandas as pd


class ALM:
    """
    Comprehensive Asset and Liability Management engine for insurance and financial institutions.
    
    This class provides a complete framework for ALM analysis including asset projection,
    liability modeling, cash flow analysis, and risk assessment. The implementation follows
    industry best practices and regulatory standards for insurance ALM.
    
    Key Capabilities:
    - Asset Management: Multi-asset portfolio projections with bonds, stocks, and cash
    - Liability Management: Comprehensive liability cash flow modeling with actuarial factors
    - Risk Analysis: Advanced discount rate calculations, neutral risk analysis, stress testing
    - Reporting: Professional reporting suite with validation frameworks
    - Scenario Analysis: Multi-maturity interest rate scenarios (1Y-30Y)
    
    The class is designed with realistic industry defaults suitable for insurance companies
    while maintaining flexibility for customization across different business lines.
    
    Attributes:
        opening_year (int): Projection start year (default: 2015)
        insured_number (int): Number of insurance contracts in portfolio
        insured_premium (float): Annual premium amount per contract
        average_age (int): Average age of policyholders
        contracts_maturity (int): Contract projection horizon in years
        
        charges_rate (float): Proportional charge rate (management fees)
        fee_pct_premium (float): Fee as percentage of premium
        fixed_fee (float): Fixed annual fee amount
        tax_rate (float): Corporate tax rate
        
        alloc_bonds (float): Portfolio allocation to bonds (0-1)
        alloc_stocks (float): Portfolio allocation to stocks (0-1)
        alloc_cash (float): Portfolio allocation to cash (0-1)
    """
    
    # =========================================================================
    # CLASS-LEVEL DEFAULTS (Industry-Standard Parameters)
    # =========================================================================
    
    # Projection Configuration
    opening_year = 2015  # Projection start year (aligned with 10-year historical data)

    # -------------------------------------------------------------------------
    # Insurance Portfolio Configuration (Realistic Industry Defaults)
    # -------------------------------------------------------------------------
    insured_number = 10000        # Number of contracts (typical mid-size portfolio)
    insured_premium = 50000       # Premium amount per contract ($50k annual premium)
    average_age = 45              # Average policyholder age (prime insurance demographic)
    contracts_maturity = 20       # Contract horizon in years (long-term insurance)

    # -------------------------------------------------------------------------
    # Fee Structure and Charges (Industry-Standard Rates)
    # -------------------------------------------------------------------------
    charges_rate = 0.015          # Proportional charge rate (1.5% - competitive rate)
    fee_pct_premium = 0.025       # Fee as % of premium (2.5% - standard acquisition cost)
    fixed_fee = 500.0             # Fixed fee amount per contract (annual administration)
    fixed_cost_inflation = 0.025  # Inflation rate for fixed costs (2.5% - long-term average)
    redemption_rates = 0.05       # Surrender rate (5% - typical lapse rate)

    # -------------------------------------------------------------------------
    # Contract Revaluation and Distribution Parameters
    # -------------------------------------------------------------------------
    guaranteed_minimum_rate = 0.025   # GMDB floor rate (2.5% minimum guarantee)
    regu_distrib_tech_res = 0.85      # % to technical reserves (85% - regulatory requirement)
    regu_distrib_fin_prod = 0.75      # % to financial products (75% - profit sharing)
    contra_distrib_fin_prod = 0.80    # Contrarian distribution (80% - smoothing mechanism)
    repurchase_rate = 0.03            # Policy repurchase rate (3% - buyback provision)
    initial_fp_percentage = 0.60      # Initial allocation to financial products (60%)
    risk_adjustment = 50000           # Risk adjustment amount (regulatory risk margin)
    capital_reserve = 500000          # Capital reserve (solvency buffer)
    ppe = 100000                      # Property, plant & equipment value

    # -------------------------------------------------------------------------
    # Tax Configuration
    # -------------------------------------------------------------------------
    tax_rate = 0.22  # Corporate tax rate (22% - typical developed market rate)

    # -------------------------------------------------------------------------
    # Bond Portfolio Configuration (Conservative Fixed Income)
    # -------------------------------------------------------------------------
    nominal = 1000000         # Face value per bond ($1M standard denomination)
    coupon_rate = 0.035       # Annual coupon (3.5% - investment grade corporate)
    bonds_initial_mv = 950000 # Initial market value (trading at discount)
    bonds_initial_vnc = 980000# Initial book value (amortized cost)
    alloc_bonds = 0.60        # Allocation to bonds (60% - conservative insurance allocation)
    alloc_stocks = 0.30       # Allocation to stocks (30% - growth component)
    alloc_cash = 0.10         # Allocation to cash (10% - liquidity buffer)

    # -------------------------------------------------------------------------
    # Stock Portfolio Configuration (Equity Component)
    # -------------------------------------------------------------------------
    stocks_initial_mv = 1200000  # Initial market value per share (growth-oriented)
    stocks_initial_vnc = 1100000 # Initial book value (historical cost basis)

    def __init__(self, *initial_data, **kwargs):
        """
        Initialize ALM instance with configurable parameters.
        
        Creates a new ALM instance with the ability to override default parameters
        through dictionaries or keyword arguments. Automatically generates the
        projection timeline based on the contract maturity.
        
        Args:
            *initial_data: Variable number of dictionaries containing parameter overrides
            **kwargs: Keyword arguments for parameter overrides
            
        Example:
            # Use defaults
            alm = ALM()
            
            # Override specific parameters
            alm = ALM(insured_number=15000, tax_rate=0.25)
            
            # Override with dictionary
            params = {'alloc_bonds': 0.70, 'alloc_stocks': 0.25, 'alloc_cash': 0.05}
            alm = ALM(params)
        """
        # Apply parameter overrides from dictionaries
        for dictionary in initial_data:
            for key, val in dictionary.items():
                setattr(self, key, val)
                
        # Apply parameter overrides from keyword arguments
        for key, val in kwargs.items():
            setattr(self, key, val)

        # Generate projection timeline array
        self.years = np.arange(self.opening_year,
                               self.opening_year + self.contracts_maturity)

    def set_default(self):
        """
        Reset all instance attributes to their class-level default values.
        
        This method provides a convenient way to restore the ALM instance to
        its original configuration with industry-standard parameters. Useful
        for scenario analysis or parameter sensitivity testing.
        
        Note:
            This method resets ALL configurable parameters. Any loaded data
            (forward rates, mortality tables, etc.) will be preserved.
        """
        # Reset all non-method, non-private attributes from the class
        for attr, val in ALM.__dict__.items():
            if not attr.startswith('__') and not callable(val):
                setattr(self, attr, val)

    def load_parameters_from_file(self, file_name):
        """
        Load scalar parameters from external file (JSON/CSV format).
        
        This method provides a framework for loading ALM parameters from
        external configuration files. Implementation depends on the specific
        file format and organizational requirements.
        
        Args:
            file_name (str): Path to parameter configuration file
            
        Raises:
            NotImplementedError: Method requires implementation based on file format
            
        Note:
            This is a placeholder for future implementation. Consider JSON format
            for structured parameter configuration or CSV for tabular parameters.
        """
        raise NotImplementedError("load_parameters_from_file requires implementation based on file format")

    def load_data_from_file(self, file_path, data_type):
        """
        Load market data from CSV files with automatic parsing and validation.
        
        Supports loading of comprehensive market data including forward rates,
        liquidity premiums, mortality tables, and repurchase rates. Provides
        automatic date parsing, numeric conversion, and data validation.
        
        Args:
            file_path (str): Path to CSV data file
            data_type (str): Type of data to load. Supported types:
                - 'forward_rates': Interest rate curves with volatility
                - 'liquidity_premium': Liquidity risk premiums
                - 'mortality_table': Age-based mortality rates
                - 'repurchase_rates': Policy surrender/lapse rates
                
        Returns:
            bool: True if data loaded successfully, False otherwise
            
        Example:
            >>> alm = ALM()
            >>> success = alm.load_data_from_file('input/fwd_rates.csv', 'forward_rates')
            >>> if success:
            ...     print("Forward rates loaded successfully")
            
        Note:
            - Forward rates file should have Date column and maturity columns (1Y, 2Y, etc.)
            - Mortality table should have Age column and Qx/Px columns
            - All files should use standard CSV format with headers
        """
        try:
            if data_type == 'mortality_table':
                # Load mortality table with age-based indexing
                df = pd.read_csv(file_path)
                df.set_index('Age', inplace=True)
                
                # Convert mortality rates to numeric format
                for col in ['Qx', 'Px']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                self.mortality_table = df
                
            else:
                # Load time-series data with date parsing
                df = pd.read_csv(file_path, parse_dates=['Date'])
                df.set_index('Date', inplace=True)
                
                # Convert all numeric columns to float
                numeric_columns = df.select_dtypes(include=['object']).columns
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                # Assign to appropriate attribute
                if data_type == 'forward_rates':
                    self.forward_rates = df
                elif data_type == 'liquidity_premium':
                    self.liquidity_premium = df
                elif data_type == 'repurchase_rates':
                    self.repurchase_rates = df
                else:
                    raise ValueError(f"Unknown data type: {data_type}")
                    
            return True
            
        except Exception as e:
            print(f"Error loading {data_type} data: {str(e)}")
            return False

    def afficher_data(self, attr_name):
        """
        Display the contents of a specified data attribute for debugging.
        
        Provides a convenient way to inspect loaded data or calculated results
        during development and debugging. Useful for validating data integrity
        and understanding calculation intermediate steps.
        
        Args:
            attr_name (str): Name of the attribute to display
            
        Example:
            >>> alm = ALM()
            >>> alm.load_data_from_file('input/fwd_rates.csv', 'forward_rates')
        Print the contents of the specified array attribute.
        """
        if hasattr(self, attr_name):
            print(f"{attr_name} = {getattr(self, attr_name)}")
        else:
            print(f"Attribute {attr_name} not found on ALM instance.")

    def report_discount_rate(self, selected_maturity='5Y'):
        """
        Calculate discount rates and deflators using selected maturity.
        
        Methodology:
        - Forward rates are used to calculate spot rates and deflators
        - Deflator[t] = 1 / (1 + spot_rate[t])^t
        - Spot rates are derived from forward rates using bootstrapping
        - Risk-adjusted rates include volatility premium
        """
        try:
            n = len(self.years)
            
            # Extract forward rates and volatility for selected maturity
            forward_rates = np.zeros(n)
            volatility = np.zeros(n)
            
            for i, year in enumerate(self.years):
                # Convert year to date (January 1st of that year)
                current_date = pd.Timestamp(year=int(year), month=1, day=1)
                # Find the closest date in forward_rates index
                closest_idx = self.forward_rates.index.get_indexer([current_date], method='nearest')[0]
                
                # Get forward rate for selected maturity
                if selected_maturity in self.forward_rates.columns:
                    forward_rates[i] = float(self.forward_rates.iloc[closest_idx][selected_maturity])
                else:
                    forward_rates[i] = float(self.forward_rates.iloc[closest_idx, 0])
                
                # Get volatility
                vol_col = f"{selected_maturity}_Vol"
                if vol_col in self.forward_rates.columns:
                    volatility[i] = float(self.forward_rates.iloc[closest_idx][vol_col])
                else:
                    volatility[i] = 0.01  # Default 1% volatility
            
            # Calculate spot rates from forward rates (bootstrapping method)
            spot_rates = np.zeros(n)
            spot_rates[0] = forward_rates[0]  # First year spot = forward
            
            for t in range(1, n):
                # Spot rate calculation: (1 + spot[t])^(t+1) = (1 + spot[t-1])^t * (1 + forward[t])
                if t == 1:
                    spot_rates[t] = forward_rates[t]
                else:
                    # Bootstrapping: solve for spot rate
                    compound_prev = (1 + spot_rates[t-1]) ** t
                    compound_current = compound_prev * (1 + forward_rates[t])
                    spot_rates[t] = compound_current ** (1/(t+1)) - 1
            
            # Calculate deflators (discount factors)
            self.deflator = np.zeros(n)
            self.deflator[0] = 1.0  # Base year deflator
            
            for t in range(1, n):
                # Deflator = 1 / (1 + spot_rate)^t
                self.deflator[t] = 1 / ((1 + spot_rates[t]) ** t)
            
            # Calculate discount rates (yield to maturity for each period)
            discount_rates = np.zeros(n)
            discount_rates[0] = 0.0  # Base year
            
            for t in range(1, n):
                # Discount rate = (1/deflator)^(1/t) - 1
                discount_rates[t] = (1 / self.deflator[t]) ** (1/t) - 1
            
            # Calculate risk-adjusted rates (forward rate + volatility premium)
            risk_premium_factor = 1.5  # Risk premium multiplier
            risk_adjusted_rates = forward_rates + (volatility * risk_premium_factor)
            
            # Create comprehensive result DataFrame
            result_df = pd.DataFrame({
                'Forward Rate': forward_rates,
                'Spot Rate': spot_rates,
                'Deflator': self.deflator,
                'Discount Rate': discount_rates,
                'Volatility': volatility,
                'Risk Adjusted Rate': risk_adjusted_rates,
                'Risk Premium': volatility * risk_premium_factor
            }, index=[str(year) for year in self.years])
            
            # Store calculated values for other methods
            self.forward_rates_selected = forward_rates
            self.spot_rates = spot_rates
            self.discount_rates = discount_rates
            self.volatility_selected = volatility
            
            return result_df
            
        except Exception as e:
            print(f"Error in report_discount_rate: {e}")
            import traceback
            traceback.print_exc()
            # Return empty DataFrame with proper structure
            return pd.DataFrame({
                'Forward Rate': [],
                'Spot Rate': [],
                'Deflator': [],
                'Discount Rate': [],
                'Volatility': [],
                'Risk Adjusted Rate': [],
                'Risk Premium': []
            })

    def report_neutral_risk(self):
        """
        Using bond market values, derive a neutral risk factor that equates
        discounted bond cash flows to observed market value.
        
        The neutral risk factor is calculated such that:
        Market Value = Sum of (Neutral Cash Flows * Deflators)
        
        Requires: self.deflator from report_discount_rate.
        """
        # Ensure deflator exists
        if not hasattr(self, 'deflator'):
            raise AttributeError("deflator must be computed via report_discount_rate first")

        n = len(self.deflator)
        
        # 1. Bond cash flows: annual coupons + principal at maturity
        bonds_cf = np.zeros(n)
        # Annual coupon payments (starting from year 1)
        bonds_cf[1:] = self.nominal * self.coupon_rate
        # Principal repayment at maturity (last year)
        bonds_cf[-1] += self.nominal

        # 2. Calculate present value of each cash flow (discounted to time 0)
        disc_cf = np.zeros(n)
        for t in range(1, n):
            # Present value of cash flow at time t
            disc_cf[t] = bonds_cf[t] * self.deflator[t]

        # 3. Calculate total present value of bond cash flows
        total_pv_bonds = np.sum(disc_cf[1:])
        
        # 4. Calculate neutral risk factor
        # The factor that makes PV of neutral cash flows equal to market value
        self.neutral_risk_factor = np.zeros(n)
        if total_pv_bonds > 0:
            # Single neutral factor applied to all cash flows
            neutral_factor = self.bonds_initial_mv / total_pv_bonds
            self.neutral_risk_factor[1:] = neutral_factor
        else:
            # If no cash flows, set factor to 1
            self.neutral_risk_factor[1:] = 1.0

        # 5. Calculate neutral cash flows (risk-adjusted)
        neutral_cf = bonds_cf.copy()
        for t in range(1, n):
            neutral_cf[t] = bonds_cf[t] * self.neutral_risk_factor[t]

        # 6. Validation: Check that PV of neutral cash flows equals market value
        pv_neutral = np.sum(neutral_cf[1:] * self.deflator[1:])
        
        # Allow small numerical differences (within 0.1%)
        tolerance = abs(self.bonds_initial_mv * 0.001)
        if not np.isclose(pv_neutral, self.bonds_initial_mv, atol=tolerance):
            print(f"Warning: Neutral risk validation - PV: {pv_neutral:.2f}, MV: {self.bonds_initial_mv:.2f}")

        # 7. Create comprehensive DataFrame report
        df = pd.DataFrame({
            'Bond CF': bonds_cf,
            'PV of CF': disc_cf,
            'Neutral Factor': self.neutral_risk_factor,
            'Neutral CF': neutral_cf,
            'Cumulative PV': np.cumsum(disc_cf)
        },
        index=[str(year) for year in self.years])
        
        # Add summary information as attributes for reference
        self.total_pv_bonds = total_pv_bonds
        self.pv_neutral_check = pv_neutral
        self.neutral_factor_value = neutral_factor if total_pv_bonds > 0 else 1.0
        
        return df

    # --------------------------------------------------------------------------
    # Asset Management Methods
    def assets_variables_projection(self):
        """
        Project asset book/market values over time (bonds, stocks, cash).
        
        Returns:
            dict: Asset projections with book values, market values, and quantities
        """
        try:
            n = len(self.years)
            
            # Initialize asset projection arrays
            self.bonds_vnc = np.zeros(n)  # Book value
            self.bonds_mv = np.zeros(n)   # Market value
            self.bonds_quantity = np.zeros(n)
            
            self.stocks_vnc = np.zeros(n)
            self.stocks_mv = np.zeros(n)
            self.stocks_quantity = np.zeros(n)
            
            self.cash_balance = np.zeros(n)
            
            # Initial values (year 0)
            total_initial_assets = self.bonds_initial_vnc + self.stocks_initial_vnc
            
            # Bond projections
            self.bonds_vnc[0] = self.bonds_initial_vnc
            self.bonds_mv[0] = self.bonds_initial_mv
            self.bonds_quantity[0] = self.bonds_initial_vnc / self.nominal  # Number of bonds
            
            # Stock projections
            self.stocks_vnc[0] = self.stocks_initial_vnc
            self.stocks_mv[0] = self.stocks_initial_mv
            self.stocks_quantity[0] = 1.0  # Normalized to 1 unit
            
            # Cash projections (initial allocation)
            self.cash_balance[0] = total_initial_assets * self.alloc_cash / (self.alloc_bonds + self.alloc_stocks)
            
            # Project forward
            for t in range(1, n):
                # Bond projections
                # Book value: amortization towards par value
                amortization_rate = 1 / self.contracts_maturity
                self.bonds_vnc[t] = self.bonds_vnc[t-1] + (self.nominal - self.bonds_vnc[t-1]) * amortization_rate
                
                # Market value: affected by interest rate changes
                if hasattr(self, 'forward_rates_selected'):
                    rate_change = self.forward_rates_selected[t] - self.forward_rates_selected[0]
                    # Duration approximation for bond price sensitivity
                    duration = max(1, self.contracts_maturity - t)
                    price_change = -duration * rate_change
                    self.bonds_mv[t] = self.bonds_mv[0] * (1 + price_change)
                else:
                    self.bonds_mv[t] = self.bonds_mv[t-1] * 1.02  # Default 2% growth
                
                self.bonds_quantity[t] = self.bonds_quantity[0]  # Quantity remains constant
                
                # Stock projections
                # Book value: cost basis remains constant
                self.stocks_vnc[t] = self.stocks_vnc[0]
                
                # Market value: stochastic growth with volatility
                if hasattr(self, 'volatility_selected'):
                    expected_return = 0.08  # 8% expected stock return
                    volatility_impact = self.volatility_selected[t] * np.random.normal(0, 1)
                    growth_rate = expected_return + volatility_impact
                else:
                    growth_rate = 0.08  # Default 8% growth
                
                self.stocks_mv[t] = self.stocks_mv[t-1] * (1 + growth_rate)
                self.stocks_quantity[t] = self.stocks_quantity[0]
                
                # Cash projections
                # Cash earns short-term interest rate
                cash_rate = self.forward_rates_selected[t] * 0.5 if hasattr(self, 'forward_rates_selected') else 0.02
                self.cash_balance[t] = self.cash_balance[t-1] * (1 + cash_rate)
            
            # Store projections
            self.asset_projections = {
                'bonds_vnc': self.bonds_vnc,
                'bonds_mv': self.bonds_mv,
                'bonds_quantity': self.bonds_quantity,
                'stocks_vnc': self.stocks_vnc,
                'stocks_mv': self.stocks_mv,
                'stocks_quantity': self.stocks_quantity,
                'cash_balance': self.cash_balance
            }
            
            return self.asset_projections
            
        except Exception as e:
            print(f"Error in assets_variables_projection: {e}")
            return {}

    def total_assets_booked_value(self):
        """
        Sum all asset classes by book value.
        
        Returns:
            np.array: Total book value of assets over time
        """
        if not hasattr(self, 'asset_projections'):
            self.assets_variables_projection()
        
        total_vnc = (self.bonds_vnc + self.stocks_vnc + self.cash_balance)
        return total_vnc

    def total_assets_market_value(self):
        """
        Sum all asset classes by market value.
        
        Returns:
            np.array: Total market value of assets over time
        """
        if not hasattr(self, 'asset_projections'):
            self.assets_variables_projection()
        
        total_mv = (self.bonds_mv + self.stocks_mv + self.cash_balance)
        return total_mv

    def variation_pmvl_reference(self):
        """
        Calculate variation in portfolio market value vs reference scenario.
        
        Returns:
            dict: Variations and sensitivities
        """
        try:
            if not hasattr(self, 'asset_projections'):
                self.assets_variables_projection()
            
            # Reference scenario (base case)
            reference_mv = self.total_assets_market_value()
            
            # Calculate variations
            variations = {}
            
            # Interest rate sensitivity (duration-based)
            if hasattr(self, 'forward_rates_selected'):
                rate_shock = 0.01  # 100 bps shock
                bond_duration = np.mean([max(1, self.contracts_maturity - t) for t in range(len(self.years))])
                bond_pv01 = self.bonds_mv * bond_duration * rate_shock
                
                variations['interest_rate_up'] = reference_mv - bond_pv01
                variations['interest_rate_down'] = reference_mv + bond_pv01
            
            # Equity shock scenarios
            equity_shock_up = 0.20    # 20% up
            equity_shock_down = -0.20  # 20% down
            
            variations['equity_up'] = reference_mv + (self.stocks_mv * equity_shock_up)
            variations['equity_down'] = reference_mv + (self.stocks_mv * equity_shock_down)
            
            # Combined stress scenario
            variations['stress_scenario'] = (reference_mv - bond_pv01 + 
                                           (self.stocks_mv * equity_shock_down))
            
            return variations
            
        except Exception as e:
            print(f"Error in variation_pmvl_reference: {e}")
            return {}

    # Liability Management Methods
    def cash_flows_liabilities(self):
        """
        Project liability cash flows: benefits, reserves, provisions.
        
        Returns:
            dict: Liability cash flow projections
        """
        try:
            n = len(self.years)
            
            # Initialize liability arrays
            self.benefit_payments = np.zeros(n)
            self.technical_reserves = np.zeros(n)
            self.surrender_benefits = np.zeros(n)
            self.expenses = np.zeros(n)
            self.premium_income = np.zeros(n)
            
            # Load mortality data if available
            if hasattr(self, 'mortality_table'):
                mortality_rates = self.mortality_table['Qx'].values
            else:
                # Default mortality rates (increasing with age)
                base_mortality = 0.001
                mortality_rates = np.array([base_mortality * (1.1 ** i) for i in range(100)])
            
            # Initial values
            contracts_in_force = self.insured_number
            average_age_current = self.average_age
            
            for t in range(n):
                current_age = average_age_current + t
                
                # Mortality rate for current age
                if current_age < len(mortality_rates):
                    mortality_rate = mortality_rates[int(current_age)]
                else:
                    mortality_rate = 0.05  # High mortality for very old ages
                
                # Premium income (decreases due to mortality and surrenders)
                if t == 0:
                    self.premium_income[t] = contracts_in_force * self.insured_premium
                else:
                    # Reduce by mortality and surrenders
                    contracts_in_force *= (1 - mortality_rate - self.redemption_rates)
                    self.premium_income[t] = contracts_in_force * self.insured_premium
                
                # Death benefits
                death_claims = contracts_in_force * mortality_rate
                self.benefit_payments[t] = death_claims * self.insured_premium * 10  # 10x premium as death benefit
                
                # Surrender benefits
                surrender_claims = contracts_in_force * self.redemption_rates
                surrender_value = self.insured_premium * 8  # 8x premium as surrender value
                self.surrender_benefits[t] = surrender_claims * surrender_value
                
                # Technical reserves (accumulating premiums less claims)
                if t == 0:
                    self.technical_reserves[t] = self.premium_income[t] * 0.8  # 80% of premiums
                else:
                    reserve_interest = self.technical_reserves[t-1] * self.guaranteed_minimum_rate
                    new_reserves = self.premium_income[t] * 0.8
                    claim_outflow = self.benefit_payments[t] + self.surrender_benefits[t]
                    self.technical_reserves[t] = (self.technical_reserves[t-1] + 
                                                reserve_interest + new_reserves - claim_outflow)
                
                # Expenses (fixed + variable)
                fixed_expense = self.fixed_fee * (1 + self.fixed_cost_inflation) ** t
                variable_expense = self.premium_income[t] * self.charges_rate
                self.expenses[t] = fixed_expense + variable_expense
            
            # Store liability projections
            self.liability_projections = {
                'benefit_payments': self.benefit_payments,
                'technical_reserves': self.technical_reserves,
                'surrender_benefits': self.surrender_benefits,
                'expenses': self.expenses,
                'premium_income': self.premium_income
            }
            
            return self.liability_projections
            
        except Exception as e:
            print(f"Error in cash_flows_liabilities: {e}")
            return {}

    def calculation_BEL(self):
        """
        Calculate Best Estimate Liability (BEL) from projected liabilities.
        
        Returns:
            dict: BEL calculations and components
        """
        try:
            if not hasattr(self, 'liability_projections'):
                self.cash_flows_liabilities()
            
            if not hasattr(self, 'deflator'):
                self.report_discount_rate()
            
            n = len(self.years)
            
            # Calculate present value of each liability component
            pv_benefits = np.sum(self.benefit_payments * self.deflator)
            pv_surrenders = np.sum(self.surrender_benefits * self.deflator)
            pv_expenses = np.sum(self.expenses * self.deflator)
            pv_premiums = np.sum(self.premium_income * self.deflator)
            
            # BEL = PV of outflows - PV of inflows
            bel_gross = pv_benefits + pv_surrenders + pv_expenses
            bel_net = bel_gross - pv_premiums
            
            # Risk margin (simplified approach)
            cost_of_capital = 0.06  # 6% cost of capital
            risk_margin = bel_gross * cost_of_capital
            
            # Technical provisions = BEL + Risk Margin
            technical_provisions = bel_net + risk_margin
            
            self.bel_results = {
                'bel_gross': bel_gross,
                'bel_net': bel_net,
                'pv_benefits': pv_benefits,
                'pv_surrenders': pv_surrenders,
                'pv_expenses': pv_expenses,
                'pv_premiums': pv_premiums,
                'risk_margin': risk_margin,
                'technical_provisions': technical_provisions
            }
            
            return self.bel_results
            
        except Exception as e:
            print(f"Error in calculation_BEL: {e}")
            return {}

    def local_gaap_pnl(self):
        """
        Compute P&L under local GAAP: realized/unrealized gains, interest, etc.
        
        Returns:
            dict: P&L components over time
        """
        try:
            if not hasattr(self, 'asset_projections'):
                self.assets_variables_projection()
            
            if not hasattr(self, 'liability_projections'):
                self.cash_flows_liabilities()
            
            n = len(self.years)
            
            # Initialize P&L components
            self.premium_revenue = self.premium_income.copy()
            self.investment_income = np.zeros(n)
            self.claim_expenses = self.benefit_payments + self.surrender_benefits
            self.operating_expenses = self.expenses.copy()
            self.realized_gains = np.zeros(n)
            self.unrealized_gains = np.zeros(n)
            
            for t in range(1, n):
                # Investment income
                bond_income = self.bonds_vnc[t-1] * self.coupon_rate
                stock_dividends = self.stocks_mv[t-1] * 0.03  # 3% dividend yield
                cash_interest = self.cash_balance[t-1] * 0.02  # 2% cash rate
                self.investment_income[t] = bond_income + stock_dividends + cash_interest
                
                # Realized gains (assume 10% of unrealized gains are realized annually)
                bond_unrealized = self.bonds_mv[t] - self.bonds_vnc[t]
                stock_unrealized = self.stocks_mv[t] - self.stocks_vnc[t]
                total_unrealized = bond_unrealized + stock_unrealized
                
                self.realized_gains[t] = total_unrealized * 0.1  # 10% realization rate
                self.unrealized_gains[t] = total_unrealized * 0.9  # Remaining unrealized
            
            # Calculate net income
            gross_income = self.premium_revenue + self.investment_income + self.realized_gains
            total_expenses = self.claim_expenses + self.operating_expenses
            pre_tax_income = gross_income - total_expenses
            tax_expense = np.maximum(0, pre_tax_income * self.tax_rate)
            net_income = pre_tax_income - tax_expense
            
            self.pnl_results = {
                'premium_revenue': self.premium_revenue,
                'investment_income': self.investment_income,
                'realized_gains': self.realized_gains,
                'unrealized_gains': self.unrealized_gains,
                'claim_expenses': self.claim_expenses,
                'operating_expenses': self.operating_expenses,
                'gross_income': gross_income,
                'total_expenses': total_expenses,
                'pre_tax_income': pre_tax_income,
                'tax_expense': tax_expense,
                'net_income': net_income
            }
            
            return self.pnl_results
            
        except Exception as e:
            print(f"Error in local_gaap_pnl: {e}")
            return {}

    def value_in_force(self):
        """
        Compute Value in Force (VIF) for in-force business.
        
        Returns:
            dict: VIF calculations and components
        """
        try:
            if not hasattr(self, 'pnl_results'):
                self.local_gaap_pnl()
            
            if not hasattr(self, 'deflator'):
                self.report_discount_rate()
            
            # VIF = Present value of future profits from in-force business
            future_profits = self.pnl_results['net_income']
            
            # Apply risk discount rate (higher than risk-free rate)
            risk_discount_rate = 0.12  # 12% risk discount rate
            risk_deflator = np.array([(1 / (1 + risk_discount_rate) ** t) for t in range(len(self.years))])
            
            # Calculate VIF components
            pv_future_profits = np.sum(future_profits * risk_deflator)
            
            # Adjust for new business strain and acquisition costs
            new_business_strain = self.insured_number * self.insured_premium * 0.1  # 10% strain
            acquisition_costs = self.insured_number * self.fee_pct_premium * self.insured_premium
            
            # Net VIF
            vif_gross = pv_future_profits
            vif_net = vif_gross - new_business_strain - acquisition_costs
            
            # VIF margin analysis
            vif_margin = vif_net / (self.insured_number * self.insured_premium) if self.insured_number > 0 else 0
            
            self.vif_results = {
                'vif_gross': vif_gross,
                'vif_net': vif_net,
                'pv_future_profits': pv_future_profits,
                'new_business_strain': new_business_strain,
                'acquisition_costs': acquisition_costs,
                'vif_margin': vif_margin,
                'risk_discount_rate': risk_discount_rate
            }
            
            return self.vif_results
            
        except Exception as e:
            print(f"Error in value_in_force: {e}")
            return {}

    def total_value_options_garantees(self):
        """
        Sum value of options & guarantees embedded in contracts.
        
        Returns:
            dict: Options and guarantees valuation
        """
        try:
            if not hasattr(self, 'deflator'):
                self.report_discount_rate()
            
            n = len(self.years)
            
            # Guaranteed minimum death benefit (GMDB)
            gmdb_value = np.zeros(n)
            
            # Guaranteed minimum withdrawal benefit (GMWB) 
            gmwb_value = np.zeros(n)
            
            # Guaranteed minimum accumulation benefit (GMAB)
            gmab_value = np.zeros(n)
            
            for t in range(n):
                # GMDB: Value of guarantee that death benefit won't fall below minimum
                guaranteed_death_benefit = self.insured_premium * 10  # 10x premium guarantee
                if hasattr(self, 'asset_projections'):
                    account_value = self.total_assets_market_value()[t] / self.insured_number
                    gmdb_payoff = max(0, guaranteed_death_benefit - account_value)
                else:
                    gmdb_payoff = guaranteed_death_benefit * 0.1  # Assume 10% of guarantee value
                
                gmdb_value[t] = gmdb_payoff
                
                # GMWB: Value of guaranteed withdrawal rates
                guaranteed_withdrawal_rate = 0.05  # 5% annual withdrawal guarantee
                if t > 0:
                    gmwb_value[t] = self.insured_premium * guaranteed_withdrawal_rate
                
                # GMAB: Value of guaranteed accumulation
                guaranteed_accumulation_rate = self.guaranteed_minimum_rate
                if hasattr(self, 'asset_projections') and t > 0:
                    guaranteed_value = self.insured_premium * (1 + guaranteed_accumulation_rate) ** t
                    actual_value = account_value if 'account_value' in locals() else guaranteed_value
                    gmab_payoff = max(0, guaranteed_value - actual_value)
                    gmab_value[t] = gmab_payoff
            
            # Calculate present values
            pv_gmdb = np.sum(gmdb_value * self.deflator)
            pv_gmwb = np.sum(gmwb_value * self.deflator)
            pv_gmab = np.sum(gmab_value * self.deflator)
            
            total_options_guarantees = pv_gmdb + pv_gmwb + pv_gmab
            
            self.options_guarantees_results = {
                'gmdb_value': gmdb_value,
                'gmwb_value': gmwb_value,
                'gmab_value': gmab_value,
                'pv_gmdb': pv_gmdb,
                'pv_gmwb': pv_gmwb,
                'pv_gmab': pv_gmab,
                'total_value': total_options_guarantees
            }
            
            return self.options_guarantees_results
            
        except Exception as e:
            print(f"Error in total_value_options_garantees: {e}")
            return {}

    # Balance Sheet Methods
    def total_liabilities_vnc(self):
        """
        Sum of liabilities at book value (VNC).
        
        Returns:
            np.array: Total book value of liabilities over time
        """
        try:
            if not hasattr(self, 'liability_projections'):
                self.cash_flows_liabilities()
            
            # Total liabilities = Technical reserves + Other provisions
            total_liabilities = self.technical_reserves + self.risk_adjustment
            return total_liabilities
            
        except Exception as e:
            print(f"Error in total_liabilities_vnc: {e}")
            return np.zeros(len(self.years))

    def total_liabilities_vm(self):
        """
        Sum of liabilities at market value (VM).
        
        Returns:
            np.array: Total market value of liabilities over time
        """
        try:
            if not hasattr(self, 'bel_results'):
                self.calculation_BEL()
            
            # Market value = BEL + Risk margin + Options & guarantees
            if not hasattr(self, 'options_guarantees_results'):
                self.total_value_options_garantees()
            
            # Approximate market value over time
            n = len(self.years)
            market_value_liabilities = np.zeros(n)
            
            for t in range(n):
                # Scale BEL by remaining contract duration
                remaining_duration = max(1, self.contracts_maturity - t)
                duration_factor = remaining_duration / self.contracts_maturity
                
                market_value_liabilities[t] = (
                    self.bel_results['bel_net'] * duration_factor +
                    self.bel_results['risk_margin'] * duration_factor +
                    self.options_guarantees_results['total_value'] * duration_factor
                )
            
            return market_value_liabilities
            
        except Exception as e:
            print(f"Error in total_liabilities_vm: {e}")
            return np.zeros(len(self.years))

    def report_asset_liability(self):
        """
        Comprehensive Asset-Liability Report with matching analysis.
        
        Returns:
            pd.DataFrame: Asset-liability matching report
        """
        try:
            # Ensure all components are calculated
            if not hasattr(self, 'asset_projections'):
                self.assets_variables_projection()
            
            if not hasattr(self, 'liability_projections'):
                self.cash_flows_liabilities()
            
            # Calculate totals
            total_assets_bv = self.total_assets_booked_value()
            total_assets_mv = self.total_assets_market_value()
            total_liabilities_bv = self.total_liabilities_vnc()
            total_liabilities_mv = self.total_liabilities_vm()
            
            # Calculate surplus/deficit
            surplus_bv = total_assets_bv - total_liabilities_bv
            surplus_mv = total_assets_mv - total_liabilities_mv
            
            # Duration analysis
            if hasattr(self, 'deflator'):
                # Asset duration (simplified)
                asset_cf = self.bonds_vnc * self.coupon_rate  # Bond coupons
                asset_duration = np.sum(np.arange(len(self.years)) * asset_cf * self.deflator) / np.sum(asset_cf * self.deflator)
                
                # Liability duration
                liability_cf = self.benefit_payments + self.surrender_benefits
                liability_duration = np.sum(np.arange(len(self.years)) * liability_cf * self.deflator) / np.sum(liability_cf * self.deflator)
                
                duration_gap = asset_duration - liability_duration
            else:
                asset_duration = liability_duration = duration_gap = 0
            
            # Create comprehensive report
            report_df = pd.DataFrame({
                'Assets BV': total_assets_bv,
                'Assets MV': total_assets_mv,
                'Liabilities BV': total_liabilities_bv,
                'Liabilities MV': total_liabilities_mv,
                'Surplus BV': surplus_bv,
                'Surplus MV': surplus_mv,
                'Asset Yield': self.forward_rates_selected if hasattr(self, 'forward_rates_selected') else np.zeros(len(self.years)),
                'Liability Cost': np.full(len(self.years), self.guaranteed_minimum_rate),
                'Spread': (self.forward_rates_selected - self.guaranteed_minimum_rate) if hasattr(self, 'forward_rates_selected') else np.zeros(len(self.years))
            }, index=[str(year) for year in self.years])
            
            # Add summary statistics as attributes
            self.al_summary = {
                'asset_duration': asset_duration,
                'liability_duration': liability_duration,
                'duration_gap': duration_gap,
                'coverage_ratio_bv': np.mean(total_assets_bv / total_liabilities_bv) if np.mean(total_liabilities_bv) > 0 else 0,
                'coverage_ratio_mv': np.mean(total_assets_mv / total_liabilities_mv) if np.mean(total_liabilities_mv) > 0 else 0
            }
            
            return report_df
            
        except Exception as e:
            print(f"Error in report_asset_liability: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame({
                'Assets BV': [],
                'Assets MV': [],
                'Liabilities BV': [],
                'Liabilities MV': [],
                'Surplus BV': [],
                'Surplus MV': [],
                'Asset Yield': [],
                'Liability Cost': [],
                'Spread': []
            })

    def report_cash_flow(self):
        """
        Comprehensive Cash Flow Report with detailed projections.
        
        Returns:
            pd.DataFrame: Cash flow analysis report
        """
        try:
            # Ensure all components are calculated
            if not hasattr(self, 'asset_projections'):
                self.assets_variables_projection()
            
            if not hasattr(self, 'liability_projections'):
                self.cash_flows_liabilities()
            
            if not hasattr(self, 'pnl_results'):
                self.local_gaap_pnl()
            
            # Asset cash flows
            bond_coupons = self.bonds_vnc * self.coupon_rate
            stock_dividends = self.stocks_mv * 0.03  # 3% dividend yield
            cash_interest = self.cash_balance * 0.02  # 2% interest on cash
            
            total_asset_cf = bond_coupons + stock_dividends + cash_interest
            
            # Liability cash flows
            total_liability_cf = self.benefit_payments + self.surrender_benefits + self.expenses
            
            # Net cash flows
            net_operating_cf = self.premium_income - total_liability_cf
            net_investment_cf = total_asset_cf
            net_total_cf = net_operating_cf + net_investment_cf
            
            # Cumulative cash flows
            cumulative_operating = np.cumsum(net_operating_cf)
            cumulative_investment = np.cumsum(net_investment_cf)
            cumulative_total = np.cumsum(net_total_cf)
            
            # Cash flow ratios
            cf_coverage_ratio = np.where(total_liability_cf > 0, 
                                       total_asset_cf / total_liability_cf, 
                                       np.inf)
            
            # Create comprehensive cash flow report
            report_df = pd.DataFrame({
                'Premium Income': self.premium_income,
                'Investment Income': total_asset_cf,
                'Total Inflows': self.premium_income + total_asset_cf,
                'Benefit Payments': self.benefit_payments,
                'Surrender Benefits': self.surrender_benefits,
                'Expenses': self.expenses,
                'Total Outflows': total_liability_cf,
                'Net Operating CF': net_operating_cf,
                'Net Investment CF': net_investment_cf,
                'Net Total CF': net_total_cf,
                'Cumulative CF': cumulative_total,
                'CF Coverage Ratio': cf_coverage_ratio
            }, index=[str(year) for year in self.years])
            
            # Add cash flow metrics as attributes
            self.cf_metrics = {
                'total_net_cf': np.sum(net_total_cf),
                'avg_coverage_ratio': np.mean(cf_coverage_ratio[cf_coverage_ratio != np.inf]),
                'cf_volatility': np.std(net_total_cf),
                'break_even_year': np.argmax(cumulative_total > 0) if np.any(cumulative_total > 0) else len(self.years)
            }
            
            return report_df
            
        except Exception as e:
            print(f"Error in report_cash_flow: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame({
                'Premium Income': [],
                'Investment Income': [],
                'Total Inflows': [],
                'Benefit Payments': [],
                'Surrender Benefits': [],
                'Expenses': [],
                'Total Outflows': [],
                'Net Operating CF': [],
                'Net Investment CF': [],
                'Net Total CF': [],
                'Cumulative CF': [],
                'CF Coverage Ratio': []
            })
