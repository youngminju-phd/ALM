"""
Asset and Liability Management (ALM) Assessment Dashboard

This module provides a comprehensive PyQt5-based GUI application for ALM analysis.
The application features modern UI design, interactive controls, and advanced
visualization capabilities for financial risk management.

Key Features:
- Professional gradient theme with responsive design
- Interactive maturity selection (1Y-30Y) for scenario analysis
- Four comprehensive report types with real-time updates
- Advanced matplotlib integration with multi-series visualization
- Optimized table display with intelligent formatting
- 10-year historical data support with volatility analysis

Author: ALM Development Team
Version: 2.0
License: MIT
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from dialog_parameters import parameter_Dialog
import pandas as pd

# Matplotlib integration for embedding figures in PyQt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from ALM import ALM          # ALM model class
from tools import write_df_to_qtable  # Helper to display DataFrame in QTableWidget


class MyWindow(QtWidgets.QMainWindow):
    """
    Main application window for comprehensive ALM assessments.
    
    This class provides a modern, professional interface for Asset and Liability
    Management analysis with the following capabilities:
    
    Features:
    - Interactive report generation with real-time parameter updates
    - Professional matplotlib visualization with multi-series support
    - Responsive table display with intelligent column management
    - Maturity selection for interest rate scenario analysis
    - Modern gradient UI theme with enhanced user experience
    
    The window integrates multiple components:
    - ALM model for financial calculations
    - Parameter dialog for model configuration
    - Advanced charting with professional styling
    - Comprehensive data table with formatting
    """
    
    def __init__(self):
        """
        Initialize the main ALM assessment window.
        
        Sets up the UI, configures matplotlib styling, loads data files,
        and establishes signal connections for interactive functionality.
        """
        super().__init__()
        # Load the UI design from Qt Designer file
        self.ui = uic.loadUi('main_window.ui', self)
        self.setWindowTitle("ALM Assessment Dashboard - Professional Risk Analysis")

        # Initialize matplotlib figure with professional styling
        self._setup_matplotlib_figure()
        
        # Configure professional matplotlib theme
        self._configure_matplotlib_theme()
        
        # Embed the matplotlib figure in the GUI
        self.addmpl(self.fig1)

        # Initialize ALM model with realistic industry defaults
        self.currentALM = ALM()
        
        # Load comprehensive market data files
        self._load_market_data()
        
        # Connect UI signals to their respective handlers
        self._connect_signals()
        
        # Set default configuration and generate initial report
        self._initialize_defaults()

        # Display the main window
        self.show()

    def _setup_matplotlib_figure(self):
        """
        Create and configure the matplotlib figure for professional visualization.
        
        Sets up a high-quality figure with appropriate size and background
        for embedding in the PyQt5 interface.
        """
        self.fig1 = Figure(figsize=(10, 6), facecolor='white')
        self.fig1.patch.set_facecolor('white')
        self.ax1f1 = self.fig1.add_subplot(111)  # Main plotting axes

    def _configure_matplotlib_theme(self):
        """
        Configure matplotlib with a modern, professional theme.
        
        Applies a comprehensive styling configuration including:
        - Neutral color palette for professional appearance
        - Enhanced grid and axis styling
        - Optimized typography and spacing
        - Professional color cycle for multi-series plots
        """
        import matplotlib.pyplot as plt
        
        # Use default style as base
        plt.style.use('default')
        
        # Apply comprehensive professional styling
        plt.rcParams.update({
            # Figure and axes background
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            
            # Grid configuration for better readability
            'axes.grid': True,
            'grid.color': '#e0e0e0',
            'grid.linestyle': '-',
            'grid.linewidth': 0.8,
            'grid.alpha': 0.7,
            
            # Axes styling for professional appearance
            'axes.edgecolor': '#cccccc',
            'axes.linewidth': 1.5,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'axes.titleweight': 'bold',
            'axes.labelcolor': '#495057',
            'axes.titlecolor': '#495057',
            
            # Tick styling for enhanced readability
            'xtick.color': '#495057',
            'ytick.color': '#495057',
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            
            # Legend configuration for clarity
            'legend.fontsize': 11,
            'legend.frameon': True,
            'legend.facecolor': 'white',
            'legend.edgecolor': '#cccccc',
            'legend.framealpha': 0.9,
            'legend.shadow': False,
            
            # Line and marker styling
            'lines.linewidth': 1.5,
            'lines.markersize': 6,
            'lines.markeredgewidth': 1.0,
            
            # Typography settings
            'font.size': 11,
            'font.family': 'sans-serif'
        })
        
        # Define professional color palette for multi-series visualization
        professional_colors = [
            '#7bb3f0', '#6ba3d0', '#5a93c0', '#9b88f0', '#8a7ad0', 
            '#7aafdc', '#6692c4', '#5eb570', '#6cc381', '#50c2ba'
        ]
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=professional_colors)

    def _load_market_data(self):
        """
        Load comprehensive 10-year market data from CSV files.
        
        Loads and validates the following data sources:
        - Forward rates (2015-2024) with volatility across multiple maturities
        - Liquidity premiums with risk adjustments
        - Mortality tables for life insurance calculations
        - Repurchase rates for surrender modeling
        
        Displays error messages for any failed data loads.
        """
        # Define comprehensive data file mapping
        data_files = {
            'forward_rates': 'input/fwd_rates.csv',
            'liquidity_premium': 'input/liquidity_premium.csv',
            'mortality_table': 'input/mortality_table.csv',
            'repurchase_rates': 'input/repurchase_rates.csv'
        }
        
        # Load each data file with error handling
        for data_type, file_path in data_files.items():
            if not self.currentALM.load_data_from_file(file_path, data_type):
                QtWidgets.QMessageBox.critical(
                    self, 
                    "Data Loading Error", 
                    f"Failed to load {data_type} data from {file_path}.\n"
                    f"Please ensure the file exists and has the correct format."
                )
                return

    def _connect_signals(self):
        """
        Connect UI signals to their respective handler methods.
        
        Establishes the following connections:
        - Report type selection triggers report regeneration
        - Chart series selection updates visualization
        - Maturity selection triggers scenario analysis
        """
        # Report type selection handler
        self.ui.reportBox.currentIndexChanged.connect(self.onChooseReport)
        
        # Chart series selection handler (independent of table selection)
        self.ui.mplfigs.itemClicked.connect(self.onChooseFigure)
        
        # Maturity selection handler for scenario analysis
        self.ui.maturityBox.currentTextChanged.connect(self.onChooseReport)

    def _initialize_defaults(self):
        """
        Set default configuration and generate initial report.
        
        Configures the application with sensible defaults:
        - 5Y maturity as the standard benchmark
        - Initial report generation for immediate user feedback
        """
        # Set default maturity selection
        self.ui.maturityBox.setCurrentText('5Y')
        
        # Generate initial report to populate the interface
        self.onChooseReport(0)

    def onParameters(self):
        """
        Open the parameter configuration dialog.
        
        Launches a modal dialog allowing users to modify ALM model parameters
        such as portfolio size, fees, asset allocation, and other key inputs.
        Changes are applied to the current ALM model instance.
        """
        dialog = parameter_Dialog(self, self.currentALM)
        dialog.show()

    def onChooseReport(self, index=None):
        """
        Handle report type and maturity selection changes.
        
        Generates the selected report type using the chosen maturity for
        interest rate scenarios. Supports four comprehensive report types:
        
        1. Discount Rate Report: Forward rates, spot rates, deflators with bootstrapping
        2. Neutral Risk Report: Bond valuations with neutral risk factors
        3. Asset-Liability Report: Comprehensive matching analysis
        4. Cash Flow Report: Detailed cash flow projections
        
        Args:
            index (int, optional): Report selection index (not used directly)
        """
        try:
            # Get current selections from UI
            report_type = self.ui.reportBox.currentText()
            selected_maturity = self.ui.maturityBox.currentText()
            
            # Generate report based on selection
            if report_type == "Discount Rate Report":
                # Generate discount rate analysis with bootstrapping methodology
                self.df = self.currentALM.report_discount_rate(selected_maturity)
                
            elif report_type == "Neutral Risk Report":
                # Ensure discount rate report exists for deflator calculations
                self.currentALM.report_discount_rate(selected_maturity)
                self.df = self.currentALM.report_neutral_risk()
                
            elif report_type == "Asset-Liability Report":
                # Generate comprehensive asset-liability matching analysis
                self.df = self.currentALM.report_asset_liability()
                
            elif report_type == "Cash Flow Report":
                # Generate detailed cash flow projections
                self.df = self.currentALM.report_cash_flow()
                
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Update interface if report generation successful
            if self.df is not None:
                self.update_table()
                self.update_figure_list()
                
                # Provide user feedback on generated report
                if report_type in ["Discount Rate Report", "Neutral Risk Report"]:
                    print(f"✓ Generated {report_type} using {selected_maturity} interest rates")
                else:
                    print(f"✓ Generated {report_type}")
            else:
                print(f"✗ Failed to generate {report_type}")
                
        except NotImplementedError:
            print(f"⚠ {report_type} is not yet implemented")
        except Exception as e:
            print(f"✗ Error generating report: {e}")

    def update_table(self):
        """
        Update the data table with current report results.
        
        Provides comprehensive table formatting including:
        - Intelligent numeric formatting based on value ranges
        - Header text formatting (underscores to spaces)
        - Optimized column widths with text wrapping
        - Professional alignment and styling
        - Disabled sorting to prevent user confusion
        """
        if self.df is None:
            return
            
        # Clear existing table content
        self.ui.pandasWidget.setRowCount(0)
        self.ui.pandasWidget.setColumnCount(0)
        
        # Configure table dimensions
        self.ui.pandasWidget.setRowCount(len(self.df))
        self.ui.pandasWidget.setColumnCount(len(self.df.columns))
        
        # Format headers for better readability
        formatted_headers = [col.replace('_', ' ') for col in self.df.columns]
        self.ui.pandasWidget.setHorizontalHeaderLabels(formatted_headers)
        
        # Set row headers based on index type
        if isinstance(self.df.index, pd.DatetimeIndex):
            # Format dates for time series data
            self.ui.pandasWidget.setVerticalHeaderLabels(
                self.df.index.strftime('%Y-%m-%d')
            )
        else:
            # Use string representation for other index types
            self.ui.pandasWidget.setVerticalHeaderLabels(
                [str(idx) for idx in self.df.index]
            )
        
        # Populate table with intelligently formatted values
        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                value = self.df.iloc[i, j]
                
                # Apply intelligent numeric formatting
                if isinstance(value, (int, float)):
                    if abs(value) < 0.01:
                        formatted_value = f'{value:.6f}'  # High precision for small values
                    elif abs(value) < 1:
                        formatted_value = f'{value:.4f}'  # Medium precision for decimals
                    else:
                        formatted_value = f'{value:.2f}'  # Standard precision for larger values
                else:
                    formatted_value = str(value)
                
                # Create table item with right alignment
                item = QtWidgets.QTableWidgetItem(formatted_value)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.ui.pandasWidget.setItem(i, j, item)
        
        # Configure professional table appearance
        self._configure_table_appearance()

    def _configure_table_appearance(self):
        """
        Configure professional table appearance and behavior.
        
        Applies optimized column widths, header styling, and disables
        sorting functionality to maintain data integrity.
        """
        # Initial column width adjustment
        self.ui.pandasWidget.resizeColumnsToContents()
        
        # Configure header behavior
        header = self.ui.pandasWidget.horizontalHeader()
        header.setDefaultSectionSize(100)  # Reasonable default width
        header.setStretchLastSection(True)  # Stretch last column to fill space
        header.setSectionResizeMode(header.ResizeToContents)
        header.setMinimumSectionSize(80)  # Prevent columns from becoming too narrow
        
        # Disable sorting functionality to prevent data confusion
        self.ui.pandasWidget.setSortingEnabled(False)
        header.setSectionsClickable(False)  # Disable header clicking
        
        # Apply maximum width constraints for better layout
        max_column_width = 120
        for i in range(len(self.df.columns)):
            current_width = self.ui.pandasWidget.columnWidth(i)
            if current_width > max_column_width:
                self.ui.pandasWidget.setColumnWidth(i, max_column_width)

    def update_figure_list(self):
        """
        Update the list of available data series for visualization.
        
        Populates the figure selection list with all available columns
        from the current report, allowing users to select specific
        data series for charting.
        """
        self.ui.mplfigs.clear()
        if self.df is not None:
            # Add each column as a selectable chart series
            for column in self.df.columns:
                self.ui.mplfigs.addItem(column)

    def onChooseFigure(self, item):
        """
        Handle chart series selection from the figure list.
        
        Updates the visualization when a user selects a data series,
        without interfering with table row selection.
        
        Args:
            item (QListWidgetItem): Selected list item containing series name
        """
        # Generate chart for selected series
        self.showFigure(item.text())

    def showFigure(self, index):
        """
        Generate professional visualization for selected data series.
        
        Creates high-quality charts with the following features:
        - Automatic Y-axis unit detection and formatting
        - Professional color schemes and styling
        - Support for both single and multi-series plots
        - Enhanced transparency and visual effects
        - Intelligent axis formatting and labeling
        
        Args:
            index (str or set): Column name(s) to plot
        """
        # Clear previous plot
        self.ax1f1.cla()
        
        # Configure professional plot background
        self.ax1f1.set_facecolor('white')
        self.ax1f1.grid(True, color='#e0e0e0', linestyle='-', linewidth=0.8, alpha=0.7)
        
        # Determine appropriate Y-axis unit based on data type
        y_unit = self._determine_y_axis_unit(index)
        
        # Convert DataFrame index to appropriate X-axis values
        x_values = self._convert_to_x_values(self.df.index)
        
        # Generate plot based on selection type
        if isinstance(index, set):
            self._plot_multiple_series(index, x_values, y_unit)
        else:
            self._plot_single_series(index, x_values, y_unit)
        
        # Apply professional axis styling
        self._style_plot_axes(y_unit)
        
        # Refresh the canvas
        self.canvas.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def _determine_y_axis_unit(self, column_name):
        """
        Determine appropriate Y-axis unit based on data type.
        
        Args:
            column_name (str or set): Column name(s) to analyze
            
        Returns:
            str: Appropriate unit label for Y-axis
        """
        # Handle set of column names
        if isinstance(column_name, set):
            column_name = list(column_name)[0]
        
        # Determine unit based on column name content
        column_lower = column_name.lower()
        
        if any(term in column_lower for term in ['rate', 'discount', 'forward', 'volatility']):
            return 'Rate (%)'
        elif any(term in column_lower for term in ['deflator', 'factor']):
            return 'Factor'
        elif any(term in column_lower for term in ['cf', 'cash', 'flow']):
            return 'Cash Flow ($)'
        else:
            return 'Value'

    def _convert_to_x_values(self, df_index):
        """
        Convert DataFrame index to appropriate X-axis values.
        
        Args:
            df_index: DataFrame index (various types)
            
        Returns:
            list: X-axis values suitable for plotting
        """
        if hasattr(df_index, 'year'):
            # Extract years from datetime index
            return df_index.year
        elif all(isinstance(x, (int, float)) for x in df_index):
            # Use numeric index directly
            return df_index
        else:
            # Attempt to extract years from string representation
            try:
                return [int(str(x)[:4]) if len(str(x)) >= 4 else int(x) for x in df_index]
            except:
                # Fallback to sequential numbering
                return range(len(df_index))

    def _plot_multiple_series(self, series_set, x_values, y_unit):
        """
        Plot multiple data series with professional styling.
        
        Args:
            series_set (set): Set of column names to plot
            x_values (list): X-axis values
            y_unit (str): Y-axis unit for formatting
        """
        professional_colors = [
            '#7bb3f0', '#6ba3d0', '#5a93c0', '#9b88f0', '#8a7ad0', 
            '#7aafdc', '#6692c4', '#5eb570', '#6cc381', '#50c2ba'
        ]
        
        for i, label in enumerate(series_set):
            if label in self.df.columns:
                series = self.df[label]
                y_values = self._format_y_values(series.values, label)
                
                # Use professional color palette
                color = professional_colors[i % len(professional_colors)]
                
                # Plot with enhanced styling
                self.ax1f1.plot(
                    x_values, y_values, 
                    marker='o', linewidth=1.5, markersize=5,
                    label=label, color=color, 
                    markeredgecolor='white', markeredgewidth=0.8
                )
        
        # Add professional legend
        legend = self.ax1f1.legend(
            loc='best', frameon=True, facecolor='white', 
            edgecolor='#cccccc', framealpha=0.95, shadow=False
        )
        legend.get_frame().set_linewidth(1.0)
        
        # Set title for multiple series
        self.ax1f1.set_title(
            'Multiple Series Comparison', 
            fontsize=14, fontweight='bold', color='#495057', pad=20
        )

    def _plot_single_series(self, series_name, x_values, y_unit):
        """
        Plot a single data series with enhanced visual effects.
        
        Args:
            series_name (str): Column name to plot
            x_values (list): X-axis values
            y_unit (str): Y-axis unit for formatting
        """
        if series_name in self.df.columns:
            series = self.df[series_name]
            y_values = self._format_y_values(series.values, series_name)
            
            # Create main line plot with professional styling
            self.ax1f1.plot(
                x_values, y_values, 
                marker='o', linewidth=1.8, markersize=6,
                color='#7bb3f0', markerfacecolor='#6ba3d0',
                markeredgecolor='white', markeredgewidth=1.2,
                alpha=0.8
            )
            
            # Add subtle area fill for enhanced visual appeal
            self.ax1f1.fill_between(
                x_values, y_values, alpha=0.1, 
                color='#7bb3f0', interpolate=True
            )
            
            # Set descriptive title
            self.ax1f1.set_title(
                f'{series_name}', 
                fontsize=14, fontweight='bold', color='#495057', pad=20
            )
        else:
            # Display error message for missing data
            self.ax1f1.text(
                0.5, 0.5, f"Column '{series_name}' not found", 
                transform=self.ax1f1.transAxes, ha='center', va='center',
                fontsize=12, color='#dc3545', fontweight='bold'
            )
            self.ax1f1.set_title(
                'Data Not Available', 
                fontsize=14, fontweight='bold', color='#dc3545', pad=20
            )

    def _format_y_values(self, values, column_name):
        """
        Format Y-axis values based on data type.
        
        Args:
            values (array): Raw data values
            column_name (str): Column name for type detection
            
        Returns:
            array: Formatted values for plotting
        """
        # Convert rates to percentage for better readability
        if any(term in column_name.lower() for term in ['rate', 'discount', 'forward', 'volatility']):
            return values * 100
        else:
            return values

    def _style_plot_axes(self, y_unit):
        """
        Apply professional styling to plot axes.
        
        Args:
            y_unit (str): Y-axis unit label
        """
        # Set axis labels with professional styling
        self.ax1f1.set_xlabel("Year", fontsize=12, fontweight='bold', color='#495057')
        self.ax1f1.set_ylabel(y_unit, fontsize=12, fontweight='bold', color='#495057')
        
        # Style the plot spines
        for spine in self.ax1f1.spines.values():
            spine.set_color('#cccccc')
            spine.set_linewidth(1.5)
        
        # Configure tick styling
        self.ax1f1.tick_params(colors='#495057', which='both', labelsize=10)
        self.ax1f1.tick_params(axis='x', rotation=45)
        
        # Set intelligent tick spacing for years
        if hasattr(self, 'df') and len(self.df) > 0:
            import matplotlib.ticker as ticker
            self.ax1f1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=10))

    def addmpl(self, fig):
        """
        Embed matplotlib figure and navigation toolbar into the Qt layout.
        
        Creates a professional matplotlib integration with:
        - High-quality figure canvas
        - Interactive navigation toolbar
        - Proper layout management
        
        Args:
            fig (matplotlib.figure.Figure): Figure to embed
        """
        # Create FigureCanvas widget from the matplotlib figure
        self.canvas = FigureCanvas(fig)
        
        # Add canvas to the vertical layout in the UI
        self.ui.mplvl.addWidget(self.canvas)
        self.canvas.draw()
        
        # Create and configure navigation toolbar
        toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        toolbar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        # Add toolbar to the layout
        self.ui.mplvLayout.addWidget(toolbar)


if __name__ == '__main__':
    """
    Application entry point.
    
    Initializes the PyQt5 application and launches the main ALM assessment window.
    Provides comprehensive error handling for application lifecycle management.
    """
    # Create PyQt5 application instance
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("ALM Assessment Dashboard")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("ALM Development Team")
    
    # Create and display main window
    window = MyWindow()
    
    # Start application event loop
    sys.exit(app.exec_())
