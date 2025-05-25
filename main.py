#!/usr/bin/env python3
"""
Main entry point for the ALM (Asset and Liability Management) application.
Launches the PyQt5 GUI interface for ALM assessments.
"""

if __name__ == '__main__':
    from main_GUI import MyWindow
    import sys
    from PyQt5 import QtWidgets
    
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_()) 