# src/calcterm/__main__.py
import sys
from PyQt5.QtWidgets import QApplication
from calcterm.app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()