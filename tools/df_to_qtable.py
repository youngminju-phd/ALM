from PyQt5 import QtWidgets

# ------------------------------------------------------------------------------
# Utility function to populate a QTableWidget with a pandas DataFrame
# ------------------------------------------------------------------------------
def write_df_to_qtable(df, table):
    """
    Write the contents of a pandas DataFrame to a QTableWidget.

    Parameters:
    - df (pandas.DataFrame): DataFrame whose data and headers will be displayed.
    - table (QTableWidget): The Qt table widget to populate.

    The DataFrame's columns become the horizontal headers, and the index becomes the vertical headers.
    Numeric values are formatted to six decimal places.
    """
    # Convert DataFrame column names to strings for the table headers
    col_headers = list(map(str, list(df.columns)))
    # Use the DataFrame index as the row headers
    row_headers = list(map(str, df.index))

    # Set the number of rows and columns in the QTableWidget
    table.setRowCount(df.shape[0])
    table.setColumnCount(df.shape[1])

    # Apply the headers to the table widget
    table.setHorizontalHeaderLabels(col_headers)
    table.setVerticalHeaderLabels(row_headers)

    # Extract the underlying numpy array for faster access
    df_array = df.values
    # Populate each cell of the table with formatted string values
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            # Format numeric values to 6 decimal places
            value_str = f"{df_array[row, col]:.6f}"
            item = QtWidgets.QTableWidgetItem(value_str)
            table.setItem(row, col, item)
