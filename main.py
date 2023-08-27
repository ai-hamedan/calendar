import sys
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QListWidget, \
    QPushButton, QLineEdit, QComboBox, QTimeEdit, QTextEdit, QMessageBox, QTabWidget
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTime
import sqlite3


class Calendar(QMainWindow):
    def __init__(self):
        super(Calendar,self).__init__()

        uic.loadUi("calendar.ui", self)

        self.calendar = self.findChild(QCalendarWidget, "calendar")
        self.event_list = self.findChild(QListWidget, "event_list")
        self.event_title = self.findChild(QLineEdit, "event_title")
        self.event_category = self.findChild(QComboBox, "event_category")
        self.event_time = self.findChild(QTimeEdit, "event_time")
        self.event_detail = self.findChild(QTextEdit, "event_detail")
        self.del_button = self.findChild(QPushButton, "del_button")
        self.add_button = self.findChild(QPushButton, "add_button")

        # related to task
        self.tasksListWidget = self.findChild(QListWidget, "listWidget")
        self.addButton = self.findChild(QPushButton, "btnaddNewTask")
        self.taskLineEdit = self.findChild(QLineEdit, "taskLineEdit")
        self.saveButton = self.findChild(QPushButton, "btnsaveChanges")

        self.tabs = self.findChild(QTabWidget,"tabs")

        self.saveButton.clicked.connect(self.saveChanges)
        self.addButton.clicked.connect(self.addNewTask1)

        # Dictionary mapping categories to colors
        self.category_colors = {'New...': QColor(197, 217, 241),
                                'Work': QColor(245, 123, 125),
                                'Doctor': QColor(117, 197, 138),
                                'Meeting': QColor(254, 232, 154)}

        self.calendar.selectionChanged.connect(self.calendarDateChanged)
        self.tabs.currentChanged.connect(self.calendarDateChanged)
        self.calendarDateChanged()
        self.add_button.clicked.connect(self.addNewTask)
        self.del_button.clicked.connect(self.delete_task)

        self.show()


    def calendarDateChanged(self):

        date = self.calendar.selectedDate()
        dateSelected = date.toPyDate()

        if self.tabs.currentIndex() == 0:
            self.updateTaskList(dateSelected)
        else:
            self.updateTaskList1(dateSelected)


    def updateTaskList(self, date):
        self.event_list.clear()
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        query = "SELECT event_title,category,time,event_detail FROM events WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QtWidgets.QListWidgetItem(str(result[0])+"  "+str(result[1])+ "  " + str(result[2]) + " " + str(result[3]))
            category = str(result[1])
            item.setBackground(self.category_colors[category])
            self.event_list.addItem(item)
        cursor.close()
        db.close()


    def addNewTask(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        event_title = str(self.event_title.text())
        category = str(self.event_category.currentText())
        category_index = self.event_category.currentIndex()
        time = str(self.event_time.time().toPyTime())
        event_detail = self.event_detail.toPlainText()
        date = self.calendar.selectedDate().toPyDate()
        if event_title =="" or event_detail=="":
            warning_box = QMessageBox()
            warning_box.setIcon(QMessageBox.Warning)
            warning_box.setText("event title and detail and category can't be empty")
            warning_box.setWindowTitle("Warning!")
            warning_box.setStandardButtons(QMessageBox.Ok)

            # Show the message box and wait for user response
            response = warning_box.exec_()
        else:
            query = "INSERT INTO events(event_title,category,time,event_detail,date) VALUES (?,?,?,?,?)"
            row = (event_title,category,time,event_detail,date)

            cursor.execute(query, row)
            db.commit()
            db.close()
            self.updateTaskList(date)
            self.event_title.clear()
            self.event_detail.clear()
            self.event_category.setCurrentIndex(0)
            self.event_time.setTime(QTime(12,0,0))



    def delete_task(self):

        mbox = QMessageBox.question(self, 'Message', "Do you want to delete?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if mbox == QMessageBox.Yes:
            selected_row = self.event_list.currentRow()
            t=self.event_list.item(selected_row)
            if t is not None:
                t1=t.text().split()
                title = t1[0]
                category = t1[1]
                time=t1[2]
                detail=t1[3]
                if selected_row != -1:
                    item = self.event_list.takeItem(selected_row)
                    del item
                    conn = sqlite3.connect("data.db")
                    cursor = conn.cursor()
                    selected_row_id = selected_row  # Replace with the ID of the row you want to delete
                    cursor.execute("DELETE FROM events WHERE event_title=? and category=? and time=? and event_detail=?", (title,category,time,detail))
                    conn.commit()
                    conn.close()
            else:
                print("item is None")



    def updateTaskList1(self, date):
        self.tasksListWidget.clear()

        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QtWidgets.QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasksListWidget.addItem(item)



    def addNewTask1(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        newTask = str(self.taskLineEdit.text())
        date = self.calendar.selectedDate().toPyDate()

        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        db.commit()
        self.updateTaskList1(date)
        self.taskLineEdit.clear()



    def saveChanges(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        date = self.calendar.selectedDate().toPyDate()

        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        messageBox = QtWidgets.QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        messageBox.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    UIWindow = Calendar()
    app.exec_()


