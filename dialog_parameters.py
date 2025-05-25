from PyQt5 import QtCore, QtGui, QtWidgets, uic

class parameter_Dialog(QtWidgets.QDialog):
    """
    QDialog subclass to edit and validate ALM parameters via a UI form.
    Loads values from an ALM instance and writes back on validation.
    """
    def __init__(self, parent=None, ALM=None):
        super(parameter_Dialog, self).__init__(parent)
        # Reference to the ALM model object to load/save parameters
        self.ALM = ALM

        # Load the .ui file created in Qt Designer
        uic.loadUi('dialog_window.ui', self)
        # Set window title
        self.setWindowTitle("Input parameters")

        # Populate UI fields with current ALM values
        self.load_parameters()

        # Connect buttons to their respective methods
        self.cancelButton.clicked.connect(self.cancel)
        self.defaultButton.clicked.connect(self.default)
        self.validateButton.clicked.connect(self.validate)

    def load_parameters(self):
        """
        Populate each QTextEdit field with the corresponding ALM attribute.
        Called on dialog initialization and when resetting to defaults.
        """
        if self.ALM is not None:
            # Integer parameters
            self.textEdit_insured_number.setText(str(self.ALM.insured_number))
            self.textEdit_insured_premium.setText(str(self.ALM.insured_premium))
            self.textEdit_average_age.setText(str(self.ALM.average_age))
            self.textEdit_contracts_maturity.setText(str(self.ALM.contracts_maturity))

            # Floating-point parameters
            self.textEdit_charges_rate.setText(str(self.ALM.charges_rate))
            self.textEdit_fee_pct_premium.setText(str(self.ALM.fee_pct_premium))
            self.textEdit_fixed_fee.setText(str(self.ALM.fixed_fee))
            self.textEdit_fixed_cost_inflation.setText(str(self.ALM.fixed_cost_inflation))
            self.textEdit_redemption_rates.setText(str(self.ALM.redemption_rates))

    def default(self):
        """
        Reset ALM model parameters to their defaults and reload fields.
        Called when the user clicks the 'Default' button.
        """
        # Reset model
        self.ALM.set_default()
        # Refresh UI
        self.load_parameters()

    def validate(self):
        """
        Read values from UI fields, convert to correct types, and write
        back into the ALM instance. Close dialog on completion.
        """
        if self.ALM is not None:
            # Parse and assign integer fields
            self.ALM.insured_number = int(self.textEdit_insured_number.toPlainText())
            self.ALM.insured_premium = int(self.textEdit_insured_premium.toPlainText())
            self.ALM.average_age = int(self.textEdit_average_age.toPlainText())
            self.ALM.contracts_maturity = int(self.textEdit_contracts_maturity.toPlainText())

            # Parse and assign floating-point fields
            self.ALM.charges_rate = float(self.textEdit_charges_rate.toPlainText())
            self.ALM.fee_pct_premium = float(self.textEdit_fee_pct_premium.toPlainText())
            self.ALM.fixed_fee = float(self.textEdit_fixed_fee.toPlainText())
            self.ALM.fixed_cost_inflation = float(self.textEdit_fixed_cost_inflation.toPlainText())
            self.ALM.redemption_rates = float(self.textEdit_redemption_rates.toPlainText())

        # Close the dialog window
        self.close()

    def cancel(self):
        """
        Discard any changes and close the dialog.
        Called when the user clicks the 'Cancel' button.
        """
        self.close()
