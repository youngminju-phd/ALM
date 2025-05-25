# ALM Python

**Asset and Liability Management in Python**

Asset and liability management (ALM) is the practice of managing financial risks arising from mismatches between assets and liabilities. This Python‑based toolkit provides end‑to‑end functionality for projecting contract cash flows, valuing assets and liabilities, and generating key ALM reports. It includes:

* A flexible `ALM` model class with default portfolio parameters
* PyQt5‑based GUI for parameter editing and interactive reporting
* Matplotlib integration for time‑series visualization
* Utilities for loading data and displaying DataFrames in Qt tables

---

## Features

* **Model Configuration**: Define portfolio parameters (premiums, contract maturity, charges, fees, tax rates, asset allocations).
* **Data Loading**: Import forward rates, liquidity premiums, mortality tables, and other time series via CSV.
* **Discount and Risk Reports**: Compute discount rates, deflators, liquidity premiums, and neutral risk factors.
* **Interactive GUI**: Edit parameters in a dialog, select reports, and visualize series in tables and charts.
* **Extensible Placeholders**: Skeleton methods for full ALM workflow (asset projections, liability cash flows, P\&L, BEL, VIF) marked with `NotImplementedError` for custom extensions.

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
   venv\Scripts\activate      # Windows
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

### Command‑Line

Run the main application:

```bash
python main.py
```

This launches the GUI. Use **Parameters → Edit** to adjust model inputs, then select **Report** types (Discount Rate or Neutral Risk) to generate tables and plots.

### Programmatic

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
```

---

## Project Structure

```text
alm-python/
├── ALM.py              # Core ALM model class
├── dialog_parameters.py# PyQt5 dialog for editing parameters
├── main_window.py      # Main GUI application
├── tools.py            # Helpers for DataFrame → QTable
├── input/              # Sample CSV files (forward_rates, premiums...)
├── main_window.ui      # Qt Designer layout for main window
├── dialog_window.ui    # Qt Designer layout for parameter dialog
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Extending the Model

Several methods in `ALM.py` are placeholders with `NotImplementedError`. To implement full ALM workflow, override or extend:

* `assets_variables_projection()`
* `cash_flows_liabilities()`
* `calculation_BEL()`
* `local_gaap_pnl()`
* `value_in_force()`
* `total_value_options_garantees()`
* `total_liabilities_vnc()` / `total_liabilities_vm()`

Use numpy/pandas for vectorized computations and maintain consistency with the `self.years` timeline.

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
