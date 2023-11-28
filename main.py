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
    try:
        if (not os.path.exists(file_path1)) or (not os.path.exists(file_path2)):
            for file in glob.glob(os.getcwd() + file1):
                shutil.copy(file, file_path)
            for file in glob.glob(os.getcwd() + file2):
                shutil.copy(file, file_path)
        return True
    except Exception:
        return False


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.current_part = None
        self.part_buttons = [
            self.task1_btn, self.task2_btn, self.task3_btn, self.task4_btn,
            self.task5_btn, self.task6_btn, self.task7_btn, self.task8_btn,
            self.task9_btn, self.task10_btn
        ]
        for button in self.part_buttons:
            button.clicked.connect(self.part_button_click)
        self.amount_buttons = 10
        self.task = Task()
        self.correct_code_model = QStandardItemModel()
        self.explanation_pte.textChanged.connect(self.explanation_changed)
        self.correct_code_pte.textChanged.connect(self.code_changed)
        self.clear_controls()
        self.toggle_theme_btn.clicked.connect(self.change_theme)
        self.corrected_cb.clicked.connect(self.mark_part_checked)
        self.insert_answer_btn.clicked.connect(self.insert)
        self.add_part_btn.clicked.connect(self.add_part)
        self.run_btn.clicked.connect(self.run_correct)
        self.run_test_btn.clicked.connect(self.run_test)
        self.clear_btn.clicked.connect(self.clear_task)
        self.pep8_btn.clicked.connect(self.pep8_correct)
        self.pep8_test_btn.clicked.connect(self.pep8_test)
        self.del_part_btn.clicked.connect(self.del_part)
        self.copy_answer_btn.clicked.connect(self.copy_my_answer)
        self.copy_to_test_btn.clicked.connect(self.copy_to_test)
        self.correct_tw.currentChanged.connect(self.correct_row_generator)
        self.paste_test_btn.clicked.connect(self.paste_test)
        self.allow_spell_check = check_dict()

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
        if self.allow_spell_check:
            errors = spell_check(self.explanation_pte.toPlainText())
            if len(errors) > 0 and self.allow_spell_check:
                s = 'Обнаружены ошибки в тексте, всё равно пометить как корректный?\n'
                for err in errors:
                    s += err[0] + ':    ' + err[1] + '\n'
                message = QMessageBox.question(self, "Орфографические ошибки", s,
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if message != QMessageBox.Yes:
                    self.corrected_cb.setChecked(False)
                    return
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
        self.correct_code_pte.clear()
        self.explanation_pte.clear()
        self.my_answer_pte.clear()
        self.teacher_answer_pte.clear()
        self.corrected_cb.setChecked(False)
        self.copy_answer_btn.setEnabled(False)

    def set_controls(self):
        for i in range(10):
            if i in range(len(self.task.tasks)):
                self.part_buttons[i].setVisible(True)
                self.part_buttons[i].setEnabled(True)
                self.change_icon(i, self.task.tasks[i].checked)
            else:
                self.part_buttons[i].setVisible(False)
                self.part_buttons[i].setEnabled(False)
                self.change_icon(i, False)
        self.mark_button()

    def insert(self):
        s = pyperclip.paste()
        self.current_part = 1
        self.teacher_answer_pte.setPlainText(s)
        self.processing()

    def processing(self):
        t = self.teacher_answer_pte.toPlainText()
        self.explanation_pte.clear()
        self.correct_code_pte.clear()
        self.my_answer_pte.clear()
        self.corrected_cb.setChecked(False)
        self.copy_answer_btn.setEnabled(False)
        self.task = Task()
        self.task.parse(t)
        self.explanation_pte.appendPlainText(self.task.tasks[0].explanation)
        self.correct_code_pte.appendPlainText(self.task.tasks[0].code)
        self.my_answer_pte.appendPlainText(self.task.get_text())
        self.set_controls()
        # self.create_my_answer

    def load_task(self, task_id):
        code = self.task.tasks[task_id].code
        explanation = self.task.tasks[task_id].explanation
        checked = self.task.tasks[task_id].checked
        self.explanation_pte.clear()
        self.correct_code_pte.clear()
        self.task.tasks[task_id].code = code
        self.task.tasks[task_id].explanation = explanation
        self.task.tasks[task_id].checked = checked
        self.explanation_pte.appendPlainText(self.task.tasks[task_id].explanation)
        self.correct_code_pte.appendPlainText(self.task.tasks[task_id].code)
        self.corrected_cb.setChecked(self.task.tasks[task_id].checked)

    def part_button_click(self):
        t = self.sender().text()
        task_id = int(t) - 1
        self.current_part = int(t)
        self.load_task(task_id)
        self.mark_button()

    def clear_task(self):
        self.task = Task()
        self.current_part = None
        self.clear_controls()

    def run_correct(self):
        file_names = ['9.txt', '9.csv', '17.txt', '22.txt', '24.txt', '26.txt', '27_A.txt', '27_B.txt']
        code = self.correct_code_pte.toPlainText()
        file_name = self.number_cb.currentText() + '.*'
        for file in file_names:
            if file in code:
                file_name = file
                break
        if (self.part_cb.currentText() == 'beta' or
                self.number_cb.currentText() in ['17', '22', '24']):
            folder = '/files/beta/'
        else:
            folder = '/files/' + self.part_cb.currentText() + '/'
        try:
            for file in glob.glob(os.getcwd() + folder + file_name):
                shutil.copy(file, os.getcwd())
        except Exception:
            self.correct_output_lb.setText('Файл не найден')
            return
        code = self.correct_code_pte.toPlainText()
        timeout = self.timeout_sb.value()
        self.correct_output_lb.setText('Вывод: ' + run_text(remove_comments(code), timeout))

    def run_test(self):
        file_names = ['9.txt', '9.csv', '17.txt', '22.txt', '24.txt', '26.txt', '27_A.txt', '27_B.txt']
        code = self.test_pte.toPlainText()
        file_name = self.number_cb.currentText() + '.*'
        for file in file_names:
            if file in code:
                file_name = file
                break
        if (self.part_cb.currentText() == 'beta' or
                self.number_cb.currentText() in ['17', '22', '24']):
            folder = '/files/beta/'
        else:
            folder = '/files/' + self.part_cb.currentText() + '/'
        try:
            for file in glob.glob(os.getcwd() + folder + file_name):
                shutil.copy(file, os.getcwd())
        except Exception:
            self.output_test_lb.setText('Файл не найден')
            return
        code = self.test_pte.toPlainText()
        timeout = self.timeout_test_sb.value()
        self.output_test_lb.setText('Вывод: ' + run_text(remove_comments(code), timeout))

    def explanation_changed(self):
        if len(self.task.tasks) > 0 and self.current_part is not None:
            self.task.tasks[self.current_part - 1].explanation = self.explanation_pte.toPlainText()
        else:
            self.task.add_part()
            self.current_part = 1
            self.task.tasks[self.current_part - 1].explanation = self.explanation_pte.toPlainText()
        self.my_answer_pte.clear()
        self.my_answer_pte.appendPlainText(self.task.get_text())

    def code_changed(self):
        if len(self.task.tasks) > 0 and self.current_part is not None:
            self.task.tasks[self.current_part - 1].code = self.correct_code_pte.toPlainText()
        else:
            self.task.add_part()
            self.current_part = 1
            self.task.tasks[self.current_part - 1].code = self.correct_code_pte.toPlainText()
        self.my_answer_pte.clear()
        self.my_answer_pte.appendPlainText(self.task.get_text())

    def add_part(self):
        self.task.add_part()
        self.current_part = len(self.task.tasks)
        self.part_buttons[self.current_part - 1].setVisible(True)
        self.part_buttons[self.current_part - 1].setEnabled(True)
        self.correct_code_pte.clear()
        self.explanation_pte.clear()

    def pep8_correct(self):
        self.correct_code_pte.setPlainText(self.correct_code_pte.toPlainText().replace('\t', '    '))
        code = self.correct_code_pte.toPlainText()
        try:
            code = black.format_str(code, mode=black.Mode(
                target_versions={black.TargetVersion.PY310},
                line_length=101,
                string_normalization=False,
                is_pyi=False,
            ), )
        except Exception as err:
            code = code.strip()
        self.correct_code_pte.setPlainText(code)
        self.correct_code = code

    def pep8_test(self):
        self.test_pte.setPlainText(self.test_pte.toPlainText().replace('\t', '    '))
        code = self.test_pte.toPlainText()
        try:
            code = black.format_str(code, mode=black.Mode(
                target_versions={black.TargetVersion.PY310},
                line_length=101,
                string_normalization=False,
                is_pyi=False,
            ), )
        except Exception as err:
            code = code.strip()
        self.test_pte.setPlainText(code)

    def del_part(self):
        if len(self.task.tasks) > 1:
            self.task.del_part(self.current_part - 1)
            pyperclip.copy(self.task.get_text())
            self.insert()

    def copy_my_answer(self):
        pyperclip.copy(self.my_answer_pte.toPlainText())

    def copy_to_test(self):
        self.test_pte.clear()
        self.test_pte.appendPlainText(self.correct_code_pte.toPlainText())

    def correct_row_generator(self):
        if self.correct_tw.currentIndex() == 1:
            self.correct_code_model.clear()
            for row in self.correct_code_pte.toPlainText().split('\n'):
                it = QStandardItem(row)
                self.correct_code_model.appendRow(it)
            self.correct_code_tv.setModel(self.correct_code_model)
            self.correct_code_tv.horizontalHeader().setVisible(False)
            self.correct_code_tv.resizeColumnToContents(0)

    def mark_button(self):
        if self.current_part is None:
            return
        for button in self.part_buttons:
            if button.text() == str(self.current_part):
                button.setStyleSheet('QPushButton {background-color: #A3C1DA}')
            else:
                button.setStyleSheet('QPushButton {background-color: #54687A}')

    def paste_test(self):
        self.test_pte.clear()
        self.test_pte.appendPlainText(pyperclip.paste())


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
