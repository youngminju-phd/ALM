"""
DataFrame to QTableWidget Utility Module

This module provides utility functions for converting pandas DataFrames to PyQt5
QTableWidget displays. It handles data formatting, header management, and
professional table presentation for ALM assessment applications.

Key Features:
- Seamless pandas DataFrame to QTableWidget conversion
- Intelligent numeric formatting with precision control
- Professional header and index management
- Optimized for financial data display

Author: ALM Development Team
Version: 2.0
License: MIT
"""

from PyQt5 import QtWidgets

# ------------------------------------------------------------------------------
# Utility function to populate a QTableWidget with a pandas DataFrame
# ------------------------------------------------------------------------------
def write_df_to_qtable(df, table):
    """
    Convert and display a pandas DataFrame in a QTableWidget with professional formatting.

    This function provides a comprehensive solution for displaying pandas DataFrames
    in PyQt5 QTableWidget components. It handles data type conversion, formatting,
    and professional presentation suitable for financial and analytical applications.

    Features:
    - Automatic data type detection and formatting
    - Professional numeric precision (6 decimal places for financial data)
    - Header management for both columns and row indices
    - Optimized table sizing and layout
    - Support for various DataFrame index types (datetime, numeric, string)

    Args:
        df (pandas.DataFrame): Source DataFrame containing the data to display.
                              Supports various data types including numeric, datetime,
                              and string data with automatic formatting.
        table (QTableWidget): Target Qt table widget that will display the DataFrame.
                             The widget will be configured and populated with the
                             DataFrame's data and structure.

    Returns:
        None: The function modifies the QTableWidget in-place.

    Example:
        >>> import pandas as pd
        >>> from PyQt5.QtWidgets import QTableWidget
        >>> 
        >>> # Create sample financial data
        >>> data = {
        ...     'Forward_Rate': [0.025, 0.028, 0.031],
        ...     'Discount_Rate': [0.024, 0.027, 0.030],
        ...     'Volatility': [0.012, 0.015, 0.018]
        ... }
        >>> df = pd.DataFrame(data, index=['2022', '2023', '2024'])
        >>> 
        >>> # Display in QTableWidget
        >>> table = QTableWidget()
        >>> write_df_to_qtable(df, table)

    Note:
        - The DataFrame's column names become horizontal headers
        - The DataFrame's index becomes vertical headers
        - All numeric values are formatted to 6 decimal places for consistency
        - The function assumes the QTableWidget is already initialized
    """
    # Validate input parameters
    if df is None or df.empty:
        # Handle empty DataFrame case
        table.setRowCount(0)
        table.setColumnCount(0)
        return
    
    # Extract and format column headers for professional display
    col_headers = [str(col) for col in df.columns]
    
    # Extract and format row headers (index) for various index types
    if hasattr(df.index, 'strftime'):
        # Handle datetime index with appropriate formatting
        row_headers = df.index.strftime('%Y-%m-%d').tolist()
    else:
        # Handle numeric, string, or other index types
        row_headers = [str(idx) for idx in df.index]

    # Configure table dimensions based on DataFrame shape
    table.setRowCount(df.shape[0])
    table.setColumnCount(df.shape[1])

    # Apply professional headers to the table widget
    table.setHorizontalHeaderLabels(col_headers)
    table.setVerticalHeaderLabels(row_headers)

    # Extract underlying numpy array for efficient data access
    df_array = df.values
    
    # Populate table cells with professionally formatted data
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            # Get raw value from DataFrame
            raw_value = df_array[row, col]
            
            # Apply intelligent formatting based on data type
            formatted_value = _format_table_value(raw_value)
            
            # Create table item with formatted value
            item = QtWidgets.QTableWidgetItem(formatted_value)
            
            # Apply professional alignment for numeric data
            item.setTextAlignment(QtWidgets.QTableWidgetItem.AlignRight | 
                                QtWidgets.QTableWidgetItem.AlignVCenter)
            
            # Insert item into table
            table.setItem(row, col, item)


def _format_table_value(value):
    """
    Apply intelligent formatting to table values based on data type and magnitude.
    
    Provides context-aware formatting for different types of financial and
    analytical data, ensuring optimal readability and precision.
    
    Args:
        value: Raw value from DataFrame (any type)
        
    Returns:
        str: Professionally formatted string representation
    """
    # Handle numeric values with precision-based formatting
    if isinstance(value, (int, float)):
        # Check for special numeric cases
        if pd.isna(value):
            return "N/A"
        elif value == 0:
            return "0.000000"
        elif abs(value) < 1e-10:
            # Scientific notation for very small values
            return f"{value:.2e}"
        else:
            # Standard 6-decimal precision for financial data
            return f"{value:.6f}"
    
    # Handle non-numeric values
    elif pd.isna(value):
        return "N/A"
    else:
        # String representation for other data types
        return str(value)


# Import pandas for type checking and utility functions
import pandas as pd
