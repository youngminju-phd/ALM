"""
ALM Parameter Configuration Dialog

This module provides a PyQt5-based dialog for editing and validating ALM model parameters.
The dialog allows users to modify key insurance portfolio parameters including contract
details, fees, charges, and other financial settings.

Key Features:
- User-friendly parameter editing interface
- Real-time validation and type conversion
- Default parameter restoration
- Integration with ALM model instances

Author: ALM Development Team
Version: 2.0
License: MIT
"""

from PyQt5 import QtCore, QtGui, QtWidgets, uic


class parameter_Dialog(QtWidgets.QDialog):
    """
    Parameter configuration dialog for ALM model settings.
    
    This dialog provides a comprehensive interface for editing ALM model parameters
    including insurance portfolio characteristics, fee structures, and financial
    settings. The dialog integrates seamlessly with ALM model instances and provides
    validation and type conversion for all parameter inputs.
    
    Features:
    - Intuitive parameter editing with labeled input fields
    - Automatic data type conversion (integer/float)
    - Default parameter restoration functionality
    - Real-time parameter validation
    - Seamless ALM model integration
    
    The dialog supports modification of:
    - Portfolio characteristics (number of contracts, premiums, demographics)
    - Fee structures (charges, premiums, fixed costs)
    - Financial parameters (inflation rates, redemption rates)
    """
    
    def __init__(self, parent=None, ALM=None):
        """
        Initialize the parameter configuration dialog.
        
        Sets up the UI, establishes connection to the ALM model, and populates
        the form fields with current parameter values.
        
        Args:
            parent (QWidget, optional): Parent widget for the dialog
            ALM (ALM, optional): ALM model instance to configure
        """
        super(parameter_Dialog, self).__init__(parent)
        
        # Store reference to the ALM model for parameter loading/saving
        self.ALM = ALM

        # Load the UI design from Qt Designer file
        uic.loadUi('dialog_window.ui', self)
        
        # Set descriptive window title
        self.setWindowTitle("ALM Parameter Configuration")

        # Populate UI fields with current ALM parameter values
        self.load_parameters()

        # Connect dialog buttons to their respective handler methods
        self._connect_button_signals()

    def _connect_button_signals(self):
        """
        Connect dialog buttons to their respective handler methods.
        
        Establishes signal-slot connections for:
        - Cancel button: Discard changes and close dialog
        - Default button: Reset parameters to default values
        - Validate button: Apply changes and close dialog
        """
        self.cancelButton.clicked.connect(self.cancel)
        self.defaultButton.clicked.connect(self.default)
        self.validateButton.clicked.connect(self.validate)

    def load_parameters(self):
        """
        Populate UI input fields with current ALM model parameter values.
        
        Loads all configurable parameters from the ALM model instance and
        displays them in the corresponding QTextEdit fields. This method
        is called during dialog initialization and when resetting to defaults.
        
        Parameters loaded include:
        - Insurance portfolio characteristics
        - Fee and charge structures
        - Financial and actuarial settings
        """
        if self.ALM is None:
            return
            
        # Load integer parameters (portfolio characteristics)
        self._load_integer_parameters()
        
        # Load floating-point parameters (rates and financial settings)
        self._load_float_parameters()

    def _load_integer_parameters(self):
        """
        Load integer-type parameters into their respective UI fields.
        
        Handles portfolio size, demographic, and contract parameters
        that require integer values.
        """
        # Portfolio size and contract details
        self.textEdit_insured_number.setText(str(self.ALM.insured_number))
        self.textEdit_insured_premium.setText(str(self.ALM.insured_premium))
        self.textEdit_average_age.setText(str(self.ALM.average_age))
        self.textEdit_contracts_maturity.setText(str(self.ALM.contracts_maturity))

    def _load_float_parameters(self):
        """
        Load floating-point parameters into their respective UI fields.
        
        Handles rate-based parameters including fees, charges, and
        financial ratios that require decimal precision.
        """
        # Fee and charge structures
        self.textEdit_charges_rate.setText(str(self.ALM.charges_rate))
        self.textEdit_fee_pct_premium.setText(str(self.ALM.fee_pct_premium))
        self.textEdit_fixed_fee.setText(str(self.ALM.fixed_fee))
        
        # Financial and actuarial parameters
        self.textEdit_fixed_cost_inflation.setText(str(self.ALM.fixed_cost_inflation))
        self.textEdit_redemption_rates.setText(str(self.ALM.redemption_rates))

    def default(self):
        """
        Reset ALM model parameters to their default values.
        
        Restores all parameters to their class-level defaults and refreshes
        the UI to reflect the changes. This provides users with a quick way
        to return to standard industry parameter values.
        
        Called when the user clicks the 'Default' button.
        """
        if self.ALM is not None:
            # Reset ALM model to default parameter values
            self.ALM.set_default()
            
            # Refresh UI fields to show default values
            self.load_parameters()
            
            # Provide user feedback
            print("✓ Parameters reset to default values")

    def validate(self):
        """
        Validate and apply parameter changes to the ALM model.
        
        Reads values from all UI input fields, performs type conversion,
        and applies the changes to the ALM model instance. Includes
        comprehensive error handling for invalid input values.
        
        The method handles:
        - Type conversion (string to int/float)
        - Parameter validation and range checking
        - Error reporting for invalid inputs
        - Model state updates
        
        Called when the user clicks the 'Validate' button.
        """
        if self.ALM is None:
            self.close()
            return
            
        try:
            # Apply integer parameter changes with validation
            self._apply_integer_parameters()
            
            # Apply floating-point parameter changes with validation
            self._apply_float_parameters()
            
            # Provide success feedback
            print("✓ Parameters successfully updated")
            
        except ValueError as e:
            # Handle invalid input values
            QtWidgets.QMessageBox.warning(
                self, 
                "Parameter Validation Error",
                f"Invalid parameter value detected:\n{str(e)}\n\n"
                f"Please check your inputs and try again."
            )
            return
            
        except Exception as e:
            # Handle unexpected errors
            QtWidgets.QMessageBox.critical(
                self,
                "Parameter Update Error", 
                f"An unexpected error occurred while updating parameters:\n{str(e)}"
            )
            return

        # Close dialog on successful validation
        self.close()

    def _apply_integer_parameters(self):
        """
        Apply integer parameter changes with validation.
        
        Converts string inputs to integers and validates ranges
        for portfolio and contract parameters.
        
        Raises:
            ValueError: If conversion fails or values are out of valid range
        """
        # Portfolio size parameters
        insured_number = int(self.textEdit_insured_number.toPlainText())
        if insured_number <= 0:
            raise ValueError("Number of insured contracts must be positive")
        self.ALM.insured_number = insured_number
        
        # Premium parameters
        insured_premium = int(self.textEdit_insured_premium.toPlainText())
        if insured_premium <= 0:
            raise ValueError("Insurance premium must be positive")
        self.ALM.insured_premium = insured_premium
        
        # Demographic parameters
        average_age = int(self.textEdit_average_age.toPlainText())
        if not (18 <= average_age <= 100):
            raise ValueError("Average age must be between 18 and 100")
        self.ALM.average_age = average_age
        
        # Contract maturity parameters
        contracts_maturity = int(self.textEdit_contracts_maturity.toPlainText())
        if not (1 <= contracts_maturity <= 50):
            raise ValueError("Contract maturity must be between 1 and 50 years")
        self.ALM.contracts_maturity = contracts_maturity

    def _apply_float_parameters(self):
        """
        Apply floating-point parameter changes with validation.
        
        Converts string inputs to floats and validates ranges
        for rate and fee parameters.
        
        Raises:
            ValueError: If conversion fails or values are out of valid range
        """
        # Charge rate parameters
        charges_rate = float(self.textEdit_charges_rate.toPlainText())
        if not (0.0 <= charges_rate <= 1.0):
            raise ValueError("Charges rate must be between 0.0 and 1.0")
        self.ALM.charges_rate = charges_rate
        
        # Fee percentage parameters
        fee_pct_premium = float(self.textEdit_fee_pct_premium.toPlainText())
        if not (0.0 <= fee_pct_premium <= 1.0):
            raise ValueError("Fee percentage of premium must be between 0.0 and 1.0")
        self.ALM.fee_pct_premium = fee_pct_premium
        
        # Fixed fee parameters
        fixed_fee = float(self.textEdit_fixed_fee.toPlainText())
        if fixed_fee < 0:
            raise ValueError("Fixed fee must be non-negative")
        self.ALM.fixed_fee = fixed_fee
        
        # Inflation rate parameters
        fixed_cost_inflation = float(self.textEdit_fixed_cost_inflation.toPlainText())
        if not (-0.1 <= fixed_cost_inflation <= 0.5):
            raise ValueError("Fixed cost inflation must be between -10% and 50%")
        self.ALM.fixed_cost_inflation = fixed_cost_inflation
        
        # Redemption rate parameters
        redemption_rates = float(self.textEdit_redemption_rates.toPlainText())
        if not (0.0 <= redemption_rates <= 1.0):
            raise ValueError("Redemption rates must be between 0.0 and 1.0")
        self.ALM.redemption_rates = redemption_rates

    def cancel(self):
        """
        Cancel parameter changes and close the dialog.
        
        Discards any modifications made in the dialog without applying
        them to the ALM model. This provides users with a safe way to
        exit the dialog without affecting the current model state.
        
        Called when the user clicks the 'Cancel' button.
        """
        # Provide user feedback
        print("⚠ Parameter changes cancelled")
        
        # Close dialog without applying changes
        self.close()
