# ALM Python

**Asset and Liability Management in Python**

Asset and liability management (ALM) is the practice of managing financial risks arising from mismatches between assets and liabilities. This Python‑based toolkit provides end‑to‑end functionality for projecting contract cash flows, valuing assets and liabilities, and generating key ALM reports. It includes:

* A flexible `ALM` model class with configurable portfolio parameters
* PyQt5‑based GUI for parameter editing and interactive reporting
* Matplotlib integration for time‑series visualization
* Utilities for loading data and displaying DataFrames in Qt tables

---

## Features

* **Model Configuration**: Define portfolio parameters (premiums, contract maturity, charges, fees, tax rates, asset allocations)
* **Data Loading**: Import forward rates, liquidity premiums, mortality tables, and repurchase rates via CSV
* **Discount and Risk Reports**: Compute discount rates, deflators, liquidity premiums, and neutral risk factors
* **Interactive GUI**: Edit parameters in a dialog, select reports, and visualize series in tables and charts
* **Extensible Framework**: Skeleton methods for full ALM workflow (asset projections, liability cash flows, P&L, BEL, VIF) marked with `NotImplementedError` for custom extensions

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/alm-python.git
   cd alm-python
   ```

2. **Create a virtual environment (optional but recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate     # macOS / Linux
   venv\Scripts\activate        # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   * **Python 3.8+**
   * **NumPy**, **pandas**
   * **PyQt5**, **matplotlib**

---

## Usage

### GUI Application

Run the main application:

```bash
python main.py
```

This launches the PyQt5 GUI. Use **Parameters → Edit** to adjust model inputs, then select **Report** types (Discount Rate or Neutral Risk) to generate tables and plots.

### Command Line

You can also run the GUI directly:

```bash
python main_GUI.py
```

### Programmatic Usage

Use the `ALM` class in scripts:

```python
from ALM import ALM
import pandas as pd

# Instantiate with defaults or override via kwargs
model = ALM(insured_premium=2000, contracts_maturity=15)

# Load forward rates and premiums
model.load_data_from_file('input/fwd_rates.csv', 'forward_rates')
model.load_data_from_file('input/liquidity_premium.csv', 'liquidity_premium')

# Generate discount rate report
df_discount = model.report_discount_rate()
print(df_discount)

# Generate neutral risk report (requires discount rate report first)
df_neutral = model.report_neutral_risk()
print(df_neutral)
```

---

## Project Structure

```text
alm-python/
├── ALM/
│   ├── __init__.py         # ALM package initialization
│   └── ALM.py              # Core ALM model class
├── tools/
│   ├── __init__.py         # Tools package initialization
│   └── df_to_qtable.py     # Helpers for DataFrame → QTable
├── input/                  # Sample CSV files
│   ├── fwd_rates.csv       # Forward interest rates
│   ├── liquidity_premium.csv # Liquidity premium data
│   ├── mortality_table.csv # Mortality table
│   └── repurchase_rates.csv # Repurchase rates
├── main.py                 # Main entry point
├── main_GUI.py             # PyQt5 main window application
├── dialog_parameters.py    # PyQt5 dialog for editing parameters
├── main_window.ui          # Qt Designer layout for main window
├── dialog_window.ui        # Qt Designer layout for parameter dialog
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## Data Files

The `input/` directory contains sample CSV data files:

* **fwd_rates.csv**: Forward interest rates over the projection horizon
* **liquidity_premium.csv**: Liquidity premium adjustments
* **mortality_table.csv**: Mortality rates by age
* **repurchase_rates.csv**: Policy repurchase rates

Data files should be formatted as single-row CSV files (no headers) with values corresponding to each year in the projection timeline.

---

## GUI Features

### Main Window
* **Report Selection**: Choose between "Discount Rate" and "Neutral Risk" reports
* **Data Table**: View calculated results in a tabular format
* **Chart Visualization**: Interactive matplotlib plots with navigation toolbar
* **Figure List**: Select specific data series to plot

### Parameter Dialog
* Edit key ALM model parameters including:
  * Insurance contract details (number, premium, age, maturity)
  * Fees and charges (rates, fixed fees, inflation)
  * Asset allocation parameters
* Reset to defaults or validate and apply changes

---

## Extending the Model

Several methods in `ALM.py` are placeholders with `NotImplementedError`. To implement a full ALM workflow, override or extend:

* `assets_variables_projection()`: Project asset book/market values over time
* `cash_flows_liabilities()`: Calculate liability cash flows
* `calculation_BEL()`: Compute Best Estimate Liabilities
* `local_gaap_pnl()`: Generate local GAAP P&L statements
* `value_in_force()`: Calculate value in force
* `total_value_options_garantees()`: Compute total value of options and guarantees
* `total_liabilities_vnc()` / `total_liabilities_vm()`: Total liabilities calculations

Use numpy/pandas for vectorized computations and maintain consistency with the `self.years` timeline.

---

## Example Usage

```python
from ALM import ALM

# Create ALM instance with custom parameters
alm = ALM(
    insured_number=1000,
    insured_premium=5000,
    contracts_maturity=20,
    average_age=45
)

# Load market data
alm.load_data_from_file('input/fwd_rates.csv', 'forward_rates')
alm.load_data_from_file('input/liquidity_premium.csv', 'liquidity_premium')

# Generate reports
discount_report = alm.report_discount_rate()
neutral_risk_report = alm.report_neutral_risk()

# Display results
print("Discount Rate Report:")
print(discount_report)
print("\nNeutral Risk Report:")
print(neutral_risk_report)
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to your branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

Please adhere to PEP8 and include docstrings for new methods.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
