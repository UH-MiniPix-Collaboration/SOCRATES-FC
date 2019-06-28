# -----------------------------------------------------------------------------------
# This script demonstrate usage of pygui module
# -----------------------------------------------------------------------------------
import pygui  # import the gui module
import time
import os


# -----------------------------------------------------------------------------------
#                                 EVENT/CALLBACK FUNCTIONS
# -----------------------------------------------------------------------------------
def onButtonClicked():
    print "Button clicked"

def onCheckBoxClicked():
    print "Checkbox clicked"

def onRadioButtonClicked():
    print "Radio clicked"

def onSpinBoxValueChanged():
    print window.spinBox.value()

def onComboBoxChanged():
    print window.comboBox.currentText()
    print window.comboBox.currentIndex()

def onDoubleSpinBoxValueChanged():
    print window.doubleSpinBox.value()

def onListWidgetChanged():
    print window.listWidget.selectedIndexes()

def onTabWidgetChanged():
    print window.tabWidget.currentIndex()


# -----------------------------------------------------------------------------------
#                                 BASIC CONTROL
# -----------------------------------------------------------------------------------

# load the window (form/widget) from UI file:
# the compoments put on the form in designer as mapped by their name 
# as attributes of returned window object. (e.g. if the button with name pushButton is 
# placed on the form, it's accessible via window.pushButton)
scriptDir = os.path.dirname(__file__) # gets the directory where this script is located
window = pygui.loadFromUiFile(scriptDir + "/form.ui")
window.show()
#window.hide()


# Label example:
window.label.setText("Test label")
window.label.setStyleSheet("color: red")
print window.label.text()

# Button example:
window.pushButton.setText("Start")
print window.pushButton.text()
window.pushButton.clicked = onButtonClicked  # register function to be called when button is clicked

# LineEdit example:
window.lineEdit.setText("Text")
print window.lineEdit.text()

# Checkbox example:
window.checkBox.setText("Test Check Box")
print window.checkBox.text()
window.checkBox.setChecked(True)
print window.checkBox.isChecked()
window.checkBox.clicked = onCheckBoxClicked

# RadioButton example:
window.radioButton.setText("Test Check Box")
print window.radioButton.text()
window.radioButton.setChecked(True)
print window.radioButton.isChecked()
window.radioButton.clicked = onRadioButtonClicked

# SpinBox example:
window.spinBox.setMaximum(100) # set maximum possible value to set
window.spinBox.setMinimum(0) # set minimum possible value to set
window.spinBox.setValue(12) # set value of spin box
print window.spinBox.value() # get value of spin box
window.spinBox.changed = onSpinBoxValueChanged # register function that is called when value of spinbox changes

# DoubleSpinBox example:
window.doubleSpinBox.setMaximum(100.5) # set maximum possible value to set
window.doubleSpinBox.setMinimum(0.5) # set minimum possible value to set
window.doubleSpinBox.setValue(13.3) # set value of spin box
print window.doubleSpinBox.value() # get value of spin box
window.doubleSpinBox.changed = onDoubleSpinBoxValueChanged # register function that is called when value of double spinbox changes

# ComboBox example:
items = ["Item A", "ItemB"]
window.comboBox.setItems(items)
print window.comboBox.currentIndex()
print window.comboBox.currentText()
window.comboBox.setCurrentIndex(1)
window.comboBox.changed = onComboBoxChanged # register function that is called when combobox selected item changes


# List Widget
window.listWidget.setItemSelected(1, True)
window.listWidget.changed = onListWidgetChanged # register function that is called when combobox selected item changes

# Tab Widget
window.tabWidget.changed = onTabWidgetChanged

# TreeView Widget
window.treeView.addString("Group", "String", "Value", True)
window.treeView.addInt("Group", "Int", 1, -100, 100, True)
window.treeView.addDouble("Group", "Double", 1, -100, 100, 2, True)
window.treeView.addBool("Group", "Bool", True, True)
window.treeView.expandAll()
print window.treeView.getProperty("Group", "String")
print window.treeView.getProperty("Group", "Int")
print window.treeView.getProperty("Group", "Double")
print window.treeView.getProperty("Group", "Bool")

window.treeView.setString("Group","String", "Test value3")
window.treeView.setInt("Group","Int", 111)
window.treeView.setDouble("Group","Double", 123.4)
window.treeView.setBool("Group","Bool", False)

# Mpx Frame
data = [0]*65536
data[100] = 100
data[101] = 102
data[103] = 104
print(window.mpxFrame)
window.mpxFrame.setData(data, 256, 256)
window.mpxFrame.setRange(0, 100)
window.mpxFrame.setColorMap(1)

# Plot
p = window.plot
p.addLine(0)
p.addPoint(0, 0, 10, 5)
p.addPoint(0, 0, 12, 50)
p.addPoint(0, 0, 13, 50)

# Messages and Dialog
#pygui.showMessage("Title", "Message")
#pygui.showWarning("Title", "Message")
#pygui.showError("Title", "Message")
#pygui.inputText("Title", "Label")
#pygui.getOpenFileName("", "*.txt") # directory, filter
#pygui.getSaveFileName("", "") # directory, filter
