import sys
import traceback
import subprocess
import pyperclip
import black
import sys
import re
import enchant
import difflib
import datetime
import time
import shutil
import os
import glob
import qdarkstyle
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog
from PyQt5 import QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from mainwindow import Ui_MainWindow
import res_rc
from classes import Task


def run_text(text, timeout):
    with open('code.py', 'w', encoding='utf-8') as c:
        c.write(text)
    try:
        completed_process = subprocess.run(['python', 'code.py'], capture_output=True, text=True, timeout=timeout)
        if completed_process.returncode == 0:
            t = completed_process.stdout
            t = t.encode('cp1251').decode('utf-8')
            if len(t) > 25:
                return t[:25] + '..'
            else:
                return t
        else:
            t = completed_process.stderr
            t = t.encode('cp1251').decode('utf-8')
            if len(t) > 50:
                return t[:50] + '\n' + t[50:]
            else:
                return t
    except subprocess.TimeoutExpired:
        return f'Программа выполнялась более {timeout} секунд'


def remove_comments(code):
    return re.sub(r'#.*', '', code)


def spell_check(text):
    rus_alph = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    words = []
    word = ''
    for c in text:
        if c.lower() in rus_alph:
            word += c
        else:
            if len(word) > 0:
                words.append(word)
                word = ''
    result = []
    dictionary = enchant.Dict("ru_RU")
    for w in words:
        if not dictionary.check(w):
            sim = dict()
            suggestions = set(dictionary.suggest(w))
            for word in suggestions:
                measure = difflib.SequenceMatcher(None, w, word).ratio()
                sim[measure] = word
            result.append([w, sim[max(sim.keys())]])
    return result


def check_dict():
    file1 = '/_venv/Lib/site-packages/enchant/data/mingw64/share/enchant/hunspell/ru_RU.aff'
    file2 = '/_venv/Lib/site-packages/enchant/data/mingw64/share/enchant/hunspell/ru_RU.dic'
    file_path1 = os.getcwd() + '/venv/Lib/site-packages/enchant/data/mingw64/share/enchant/hunspell/ru_RU.aff'
    file_path2 = os.getcwd() + '/venv/Lib/site-packages/enchant/data/mingw64/share/enchant/hunspell/ru_RU.dic'
    file_path = os.getcwd() + '/venv/Lib/site-packages/enchant/data/mingw64/share/enchant/hunspell/'
    if (not os.path.exists(file_path1)) or (not os.path.exists(file_path2)):
        for file in glob.glob(os.getcwd() + file1):
            shutil.copy(file, file_path)
        for file in glob.glob(os.getcwd() + file2):
            shutil.copy(file, file_path)


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.current_part = 1
        self.part_buttons = [
            self.task1_btn, self.task2_btn, self.task3_btn, self.task4_btn,
            self.task5_btn, self.task6_btn, self.task7_btn, self.task8_btn,
            self.task9_btn, self.task10_btn
        ]
        for button in self.part_buttons:
            button.clicked.connect(self.part_button_click)
        self.amount_buttons = 10
        self.task = Task()
        self.clear_controls()
        self.toggle_theme_btn.clicked.connect(self.change_theme)
        self.corrected_cb.clicked.connect(self.mark_part_checked)
        self.insert_answer_btn.clicked.connect(self.insert)

        check_dict()

    def change_theme(self):
        if self.toggle_theme_btn.text() == 'Светлая тема':
            self.toggle_theme_btn.setText('Тёмная тема')
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=qdarkstyle.LightPalette))
        else:
            self.toggle_theme_btn.setText('Светлая тема')
            app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=qdarkstyle.DarkPalette))

    def change_icon(self, button, checked):
        icon = QtGui.QIcon()
        if checked:
            icon.addPixmap(QtGui.QPixmap(":/img/check_green.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(":/img/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        button_to_change = self.part_buttons[button - 1]
        button_to_change.setIcon(icon)

    def mark_part_checked(self):
        self.change_icon(self.current_part, self.corrected_cb.isChecked())
        self.task.tasks[self.current_part - 1].checked = self.corrected_cb.isChecked()
        if self.task.is_ready():
            self.copy_answer_btn.setEnabled(True)
        else:
            self.copy_answer_btn.setEnabled(False)

    def clear_controls(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/check.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        for i in range(1, self.amount_buttons):
            self.change_icon(i, False)
            if i > 0:
                self.part_buttons[i].setVisible(False)

    def set_controls(self):
        for i in range(len(self.task.tasks)):
            self.part_buttons[i].setVisible(True)
            self.part_buttons[i].setEnabled(True)

    def insert(self):
        s = pyperclip.paste()
        self.current_part = 1
        self.teacher_answer_pte.setPlainText(s)
        self.processing()

    def processing(self):
        t = self.teacher_answer_pte.toPlainText()
        self.task.parse(t)
        self.explanation_pte.clear()
        self.explanation_pte.appendPlainText(self.task.tasks[0].explanation)
        self.correct_code_pte.clear()
        self.correct_code_pte.appendPlainText(self.task.tasks[0].code)
        self.my_answer_pte.clear()
        self.my_answer_pte.appendPlainText(self.task.get_text())
        self.set_controls()
        # self.create_my_answer

    def load_task(self, task_id):
        self.explanation_pte.clear()
        self.explanation_pte.appendPlainText(self.task.tasks[task_id].explanation)
        self.correct_code_pte.clear()
        self.correct_code_pte.appendPlainText(self.task.tasks[task_id].code)
        self.corrected_cb.setChecked(self.task.tasks[task_id].checked)

    def part_button_click(self):
        t = self.sender().text()
        task_id = int(t) - 1
        self.load_task(task_id)
        self.current_part = int(t)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb)
    msg = QMessageBox.critical(
        None,
        "Error catched!:",
        tb
    )
    QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    sys.excepthook = excepthook
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=qdarkstyle.DarkPalette))
    ex.show()
    sys.exit(app.exec_())
