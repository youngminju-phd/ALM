import sys
from PyQt5 import QtWidgets, uic, Qt
from dialog_parameters import parameter_Dialog

# Matplotlib integration for embedding figures in PyQt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from ALM import ALM          # ALM model class
from tools import write_df_to_qtable  # Helper to display DataFrame in QTableWidget


class MyWindow(QtWidgets.QMainWindow):
    """
    Main application window for ALM assessments.
    Loads ALM data, displays reports in table and chart, and manages parameter dialog.
    """
    def __init__(self):
        super(MyWindow, self).__init__()
        # Load UI layout from Qt Designer .ui file
        uic.loadUi('main_window.ui', self)
        self.setWindowTitle("ALM assessments")

        # Create a Matplotlib Figure and embed it in the GUI
        fig1 = Figure()
        self.ax1f1 = fig1.add_subplot(111)  # Main axes for plotting
        self.addmpl(fig1)  # Add figure canvas and toolbar

        # Prepare ALM instance and load time series data
        data_input = {
            'forward_rates': "input/fwd_rates.csv",
            'liquidity_premium': "input/liquidity_premium.csv",
            'repurchase_rates': "input/repurchase_rates.csv",
            'mortality_table': "input/mortality_table.csv"
        }
        self.currentALM = ALM()  # Instantiate model with defaults
        # Load each CSV into corresponding attribute array
        for attr, path in data_input.items():
            self.currentALM.load_data_from_file(path, attr)

        # Connect menu action to parameter dialog
        self.actionParameters.triggered.connect(self.onParameters)
        # Connect report dropdown selection changes
        self.reportBox.currentIndexChanged.connect(self.onChooseReport)
        # Connect double-click on figure list to handler
        self.mplfigs.itemDoubleClicked.connect(self.onChooseListFigs)
        # Connect table selection changes to handler
        self.pandasWidget.itemSelectionChanged.connect(self.onChooseTable)

        # Initialize display: select first report type
        self.reportBox.setCurrentIndex(0)
        self.onChooseReport(0)

        self.show()

    def onParameters(self):
        """
        Open the parameter dialog to allow editing ALM model inputs.
        """
        dialog = parameter_Dialog(self, self.currentALM)
        dialog.show()

    def onChooseReport(self, index):
        """
        When the user selects a report type from the combo box:
        - Generate DataFrame via ALM methods
        - Populate QTableWidget and list of available series
        - Display the first series in the plot
        """
        if index == 0:  # Discount rate report
            self.df = self.currentALM.report_discount_rate()
        elif index == 1:  # Neutral risk report
            self.df = self.currentALM.report_neutral_risk()
        else:
            self.df = None

        if self.df is not None:
            # Write DataFrame to the table widget
            write_df_to_qtable(self.df, self.pandasWidget)
            # Populate list widget with DataFrame row labels
            self.mplfigs.clear()
            for row_label in self.df.index:
                self.mplfigs.addItem(row_label)
            # Show the first series by default
            self.showFigure(self.df.index[0])

    def onChooseTable(self):
        """
        When the user selects rows in the table, extract those series
        and redraw the plot with selected rows.
        """
        # Determine selected row labels
        rows = set([self.df.index[idx.row()] for idx in self.pandasWidget.selectedIndexes()])
        self.showFigure(rows)

    def onChooseListFigs(self, item):
        """
        When the user double-clicks a series in the list widget,
        select the corresponding table row and plot that series.
        """
        # Sync table selection
        self.pandasWidget.selectRow(self.mplfigs.row(item))
        # Plot the clicked series
        self.showFigure(item.text())

    def showFigure(self, index):
        """
        Plot one or multiple series on the Matplotlib canvas.
        - If index is a set: plot all in set with legend
        - If index is a single label: plot that series only
        """
        self.ax1f1.cla()  # Clear previous plot
        if isinstance(index, set):
            # Plot each selected series
            for label in index:
                series = self.df.loc[label]
                self.ax1f1.plot(series.keys(), series.values, '.-', label=label)
            self.ax1f1.legend()
        else:
            # Single series plot
            series = self.df.loc[index]
            self.ax1f1.plot(series.keys(), series.values, '.-')
            self.ax1f1.set_title(index)
        # Label x-axis and refresh canvas
        self.ax1f1.set_xlabel("Time")
        self.canvas.draw()

    def addmpl(self, fig):
        """
        Helper to embed a Matplotlib figure and toolbar into the Qt layout.
        """
        # Create a FigureCanvas widget from the Figure
        self.canvas = FigureCanvas(fig)
        # Add canvas to the vertical layout in the UI
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        # Create and add navigation toolbar below the plot
        toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        toolbar.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.mplvLayout.addWidget(toolbar)


if __name__ == '__main__':
    # Standard PyQt5 application bootstrap
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
