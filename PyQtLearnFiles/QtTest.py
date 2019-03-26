import sys
from PyQt5 import QtWidgets,QtCore

app = QtWidgets.QApplication(sys.argv)
widget = QtWidgets.QWidget()
widget.resize(625,625)
widget.setWindowTitle('QtTest Window')
widget.show()
sys.exit(app.exec_())