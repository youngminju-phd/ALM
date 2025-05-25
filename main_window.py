import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.color': '#e0e0e0',
            'grid.linestyle': '--',
            'grid.linewidth': 0.5,
            'axes.edgecolor': '#2c3e50',
            'axes.linewidth': 1.0,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'axes.titleweight': 'bold',
            'axes.labelcolor': '#2c3e50',
            'xtick.color': '#2c3e50',
            'ytick.color': '#2c3e50',
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'legend.frameon': True,
            'legend.facecolor': 'white',
            'legend.edgecolor': '#e0e0e0',
            'legend.framealpha': 0.8,
            'lines.linewidth': 2.0,
            'lines.markersize': 6,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif'],
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            'figure.dpi': 100,
            'figure.figsize': [8.0, 6.0],
            'figure.autolayout': True
        })
        
        # Color palette for plots
        self.colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', 
                      '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']
        
        # Initialize matplotlib figure
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ui.mplvLayout.addWidget(self.canvas)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.ui.plotWidget)
        self.ui.mplvLayout.addWidget(self.toolbar)
        
        # Connect signals
        self.ui.reportBox.currentIndexChanged.connect(self.update_report)
        self.ui.mplfigs.itemClicked.connect(self.update_plot)
        self.ui.updateButton.clicked.connect(self.update_report)
        
        # Initialize data
        self.load_data()
        self.update_report()

    def update_plot(self, item):
        """Update the plot when a figure is selected"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get data for selected figure
        figure_name = item.text()
        data = self.get_figure_data(figure_name)
        
        if data is not None:
            # Plot data with improved styling
            if isinstance(data, pd.DataFrame):
                for i, column in enumerate(data.columns):
                    color = self.colors[i % len(self.colors)]
                    ax.plot(data.index, data[column], label=column, 
                           color=color, linewidth=2, marker='o', markersize=4)
            else:
                ax.plot(data.index, data, color=self.colors[0], 
                       linewidth=2, marker='o', markersize=4)
            
            # Customize plot appearance
            ax.set_title(figure_name, pad=20, fontsize=14, fontweight='bold')
            ax.set_xlabel('Date', labelpad=10)
            ax.set_ylabel('Value', labelpad=10)
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.xticks(rotation=45)
            
            # Add grid with custom style
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Customize legend
            if len(data.columns) > 1:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                         borderaxespad=0., frameon=True, fancybox=True, 
                         shadow=True, fontsize=10)
            
            # Adjust layout
            self.figure.tight_layout()
            
            # Refresh canvas
            self.canvas.draw()

    def update_report(self):
        """Update the report based on selected type and date range"""
        report_type = self.ui.reportBox.currentText()
        start_date = self.ui.startDateEdit.date().toPyDate()
        end_date = self.ui.endDateEdit.date().toPyDate()
        
        # Get data for selected report type
        data = self.get_report_data(report_type, start_date, end_date)
        
        if data is not None:
            # Update table
            self.update_table(data)
            
            # Update available figures
            self.update_figures_list(data)
            
            # Update plot with first figure
            if self.ui.mplfigs.count() > 0:
                self.ui.mplfigs.setCurrentRow(0)
                self.update_plot(self.ui.mplfigs.currentItem())

    def update_table(self, data):
        """Update the data table with improved styling"""
        self.ui.pandasWidget.setRowCount(0)
        self.ui.pandasWidget.setColumnCount(0)
        
        if isinstance(data, pd.DataFrame):
            # Set table dimensions
            self.ui.pandasWidget.setRowCount(len(data))
            self.ui.pandasWidget.setColumnCount(len(data.columns))
            
            # Set headers
            self.ui.pandasWidget.setHorizontalHeaderLabels(data.columns)
            self.ui.pandasWidget.setVerticalHeaderLabels(data.index.strftime('%Y-%m-%d'))
            
            # Populate table with formatted values
            for i in range(len(data)):
                for j in range(len(data.columns)):
                    value = data.iloc[i, j]
                    if isinstance(value, (int, float)):
                        # Format numbers with appropriate precision
                        if abs(value) < 0.01:
                            formatted_value = f'{value:.6f}'
                        elif abs(value) < 1:
                            formatted_value = f'{value:.4f}'
                        else:
                            formatted_value = f'{value:.2f}'
                    else:
                        formatted_value = str(value)
                    
                    item = QTableWidgetItem(formatted_value)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.ui.pandasWidget.setItem(i, j, item)
            
            # Adjust column widths
            self.ui.pandasWidget.resizeColumnsToContents()
            
            # Apply custom styling
            header = self.ui.pandasWidget.horizontalHeader()
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 5px;
                    border: 1px solid #dee2e6;
                    font-weight: bold;
                }
            """)
            
            # Set alternating row colors
            self.ui.pandasWidget.setAlternatingRowColors(True)
            self.ui.pandasWidget.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #f8f9fa;
                    background-color: white;
                    gridline-color: #dee2e6;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #e9ecef;
                    color: black;
                }
            """) 