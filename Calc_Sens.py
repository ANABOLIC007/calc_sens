import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import QDir

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calc DPI-Sens + Create Sens-Config Quake III Arena Excessive Plus")
        self.setFixedSize(750, 350) # Увеличиваем высоту окна для нового поля

        folder = os.path.dirname(__file__)  # Получаем путь к директории, где находится скрипт
        self.settings_file = os.path.join(folder, "sens_settings.json")

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.folder_input = QLineEdit("")
        self.folder_input.setObjectName("folder_input")  # Уникальное имя для первого поля
        folder_layout = self._labeled_input("Folder Path:", self.folder_input, button_text="Browse", button_action=self.browse_folder)

        self.from_cm_input = QLineEdit("1")
        self.from_cm_input.setValidator(QDoubleValidator())
        self.from_cm_input.setMaxLength(4)
        self.from_cm_input.textChanged.connect(self._update_realtime_sens)
        self.from_cm_realtime_label = QLabel("")

        self.max_decrease_input = QLineEdit("25")
        self.max_decrease_input.setValidator(QIntValidator(0, 100))
        self.max_decrease_input.setMaxLength(4)
        self.max_decrease_input.textChanged.connect(self._update_realtime_sens)
        self.max_decrease_realtime_label = QLabel("")

        self.to_cm_input = QLineEdit("100")
        self.to_cm_input.setValidator(QDoubleValidator())
        self.to_cm_input.setMaxLength(4)
        self.to_cm_input.textChanged.connect(self._update_realtime_sens)
        self.to_cm_realtime_label = QLabel("")

        self.min_decrease_input = QLineEdit("5")
        self.min_decrease_input.setValidator(QIntValidator(0, 100))
        self.min_decrease_input.setMaxLength(4)
        self.min_decrease_input.textChanged.connect(self._update_realtime_sens)
        self.min_decrease_realtime_label = QLabel("")

        self.step_input = QLineEdit("1")
        self.step_input.setValidator(QDoubleValidator())
        self.step_input.setMaxLength(4)
        self.step_input.setStyleSheet("QLineEdit { margin-right: 531px; }") # Добавляем отступ слева

        self.dpi_input = QLineEdit("400")
        self.dpi_input.setValidator(QIntValidator())
        self.dpi_input.setMaxLength(4)
        self.dpi_input.setStyleSheet("QLineEdit { margin-right: 531px; }") # Добавляем отступ слева
        self.dpi_input.textChanged.connect(self._update_realtime_sens)

        self.zoom_bind_layout = QHBoxLayout()
        zoom_bind_label = QLabel("Bind Zoom:")
        self.zoom_bind_layout.addWidget(zoom_bind_label)
        self.zoom_bind_input = QLineEdit("mouse2") # Поле ввода
        self.zoom_bind_input.setStyleSheet("QLineEdit { margin-right: 531px; width: 40px; }") # Настраиваем сдвиг и ширину
        self.zoom_bind_layout.addWidget(self.zoom_bind_input)

        self.from_layout = self._labeled_double_input("First Config cm/360:", self.from_cm_input, self.from_cm_realtime_label, "Sens Decrease at Zoom %", self.max_decrease_input, self.max_decrease_realtime_label)
        self.to_layout = self._labeled_double_input("Last Config cm/360:", self.to_cm_input, self.to_cm_realtime_label, "Sens Decrease at Zoom %", self.min_decrease_input, self.min_decrease_realtime_label)
        step_layout = self._labeled_input("Step (cm):", self.step_input)
        dpi_layout = self._labeled_input("DPI:", self.dpi_input)

        layout.addLayout(folder_layout)
        layout.addLayout(self.from_layout)
        layout.addLayout(self.to_layout)
        layout.addLayout(step_layout)
        layout.addLayout(dpi_layout)
        layout.addLayout(self.zoom_bind_layout) # Добавляем наш настроенный layout

        self.generate_button = QPushButton("Generate")
        self.generate_button.setFixedWidth(150)  # Устанавливаем фиксированную ширину кнопки
        self.generate_button.clicked.connect(self.generate_config)  # Подключаем обработчик события нажатия

        button_layout = QHBoxLayout()  # Создаём новый горизонтальный layout
        button_layout.addStretch(1)  # Добавляем отступ слева
        button_layout.addWidget(self.generate_button)
        button_layout.addStretch(1)  # Добавляем отступ справа
        layout.addLayout(button_layout)  # Добавляем горизонтальный layout с кнопкой в основной

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Загрузка сохраненных настроек
        self.load_settings()
        self._update_realtime_sens() # Первоначальное обновление realtime sens

    def _labeled_input(self, label_text, input_field, button_text=None, button_action=None):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(input_field)
        if button_text and button_action:
            button = QPushButton(button_text)
            button.clicked.connect(button_action)
            button.setFixedWidth(90)  # Устанавливаем фиксированную ширину кнопки
            layout.addWidget(button)
        return layout

    def _labeled_double_input(self, label1, input1, realtime_label1, label2, input2, realtime_label2):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label1))
        layout.addWidget(input1)
        layout.addWidget(realtime_label1)
        layout.addWidget(QLabel(label2))
        layout.addWidget(input2)
        layout.addWidget(realtime_label2)
        return layout

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder:
            self.folder_input.setText(folder)

    def validate_inputs(self):
        """Проверка всех полей на пустоту"""
        if not self.folder_input.text():
            QMessageBox.warning(self, "Warning", "Folder path cannot be empty!")
            return False

        fields = [
            (self.from_cm_input, "Minimum cm"),
            (self.to_cm_input, "Maximum cm"),
            (self.min_decrease_input, "Decrease at zoom (min)"),
            (self.max_decrease_input, "Decrease at zoom (max)"),
            (self.step_input, "Step"),
            (self.dpi_input, "DPI"),
            (self.zoom_bind_input, "Bind Zoom") # Добавлена проверка для нового поля
        ]

        for field, name in fields:
            if not field.text():
                QMessageBox.warning(self, "Warning", f"Field '{name}' cannot be empty!")
                return False

        return True

    def _calculate_realtime_sens(self):
        try:
            dpi = int(self.dpi_input.text()) if self.dpi_input.text() else 400
            from_cm = float(self.from_cm_input.text()) if self.from_cm_input.text() else 1.0
            max_decrease = float(self.max_decrease_input.text()) if self.max_decrease_input.text() else 25.0
            to_cm = float(self.to_cm_input.text()) if self.to_cm_input.text() else 100.0
            min_decrease = float(self.min_decrease_input.text()) if self.min_decrease_input.text() else 5.0

            def base_sensitivity(cm, current_dpi):
                base = 25.977 / cm
                return base * (1600 / current_dpi)

            sens_from = base_sensitivity(from_cm, dpi)
            decrease_from_percent = max_decrease / 100
            zoom_factor_from = 1 - decrease_from_percent
            zoom_sensitivity_from = round(sens_from * zoom_factor_from, 3)

            sens_to = base_sensitivity(to_cm, dpi)
            decrease_to_percent = min_decrease / 100
            zoom_factor_to = 1 - decrease_to_percent
            zoom_sensitivity_to = round(sens_to * zoom_factor_to, 3)

            return round(sens_from, 3), round(zoom_sensitivity_from, 3), round(sens_to, 3), round(zoom_sensitivity_to, 3)

        except ValueError:
            return "", "", "", ""

    def _update_realtime_sens(self):
        base_from, zoom_from, base_to, zoom_to = self._calculate_realtime_sens()
        self.from_cm_realtime_label.setText(f"{base_from}")
        self.max_decrease_realtime_label.setText(f"{zoom_from}")
        self.to_cm_realtime_label.setText(f"{base_to}")
        self.min_decrease_realtime_label.setText(f"{zoom_to}")

    def generate_config(self):
        if not self.validate_inputs():
            return

        try:
            folder = self.folder_input.text()
            from_cm = float(self.from_cm_input.text())
            to_cm = float(self.to_cm_input.text())
            step = float(self.step_input.text())
            dpi = int(self.dpi_input.text())
            max_decrease = float(self.max_decrease_input.text())
            min_decrease = float(self.min_decrease_input.text())
            zoom_bind = self.zoom_bind_input.text() if self.zoom_bind_input.text() else "mouse2" # Получаем бинд зума

            if not os.path.exists(folder):
                os.makedirs(folder)

            decrease_range = max_decrease - min_decrease

            def base_sensitivity(cm, current_dpi):
                base = 25.977 / cm
                return base * (1600 / current_dpi)

            for cm in range(int(from_cm), int(to_cm) + 1, int(step)):
                sensitivity = base_sensitivity(cm, dpi)
                decrease_percent = (max_decrease - (cm - from_cm) * (decrease_range / (to_cm - from_cm))) / 100
                zoom_factor = 1 - decrease_percent
                zoom_sensitivity = round(sensitivity * zoom_factor, 3)

                file_path = os.path.join(folder, f'{cm}.cfg')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"// MOUSE SENSITIVITY AT DPI {dpi}\n")
                    f.write(f"set zon \"+zoom; sensitivity {zoom_sensitivity}\" \t\t\t// Zoom ON: decreased sensitivity\n")
                    f.write(f"set zof \"-zoom; sensitivity {round(sensitivity, 3)}\" \t\t// Zoom OFF: standard sensitivity\n")
                    f.write(f"bind {zoom_bind} +vstr zon zof\n") # Используем введенный бинд зума

            QMessageBox.information(self, "Done", f"Files successfully created in folder:\n{folder}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during generation: {str(e)}")

        # Сохранение настроек
        self.save_settings()


    def load_settings(self):
        """Загрузка настроек из JSON файла"""
        if not os.path.exists(self.settings_file):
            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            self.folder_input.setText(settings.get('folder_path', ''))
            self.from_cm_input.setText(settings.get('from_cm', '1'))
            self.to_cm_input.setText(settings.get('to_cm', '100'))
            self.min_decrease_input.setText(settings.get('min_decrease', '5'))
            self.max_decrease_input.setText(settings.get('max_decrease', '25'))
            self.step_input.setText(settings.get('step', '1'))
            self.dpi_input.setText(settings.get('dpi', '400'))
            self.zoom_bind_input.setText(settings.get('zoom_bind', 'mouse2')) # Загрузка бинда зума

        except json.JSONDecodeError:
            QMessageBox.warning(self, "Warning", "Settings file is corrupted or has incorrect format.")
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load settings: {str(e)}")


    def save_settings(self):
        """Сохранение настроек в JSON файл"""
        settings = {
            'folder_path': self.folder_input.text(),
            'from_cm': self.from_cm_input.text(),
            'to_cm': self.to_cm_input.text(),
            'min_decrease': self.min_decrease_input.text(),
            'max_decrease': self.max_decrease_input.text(),
            'step': self.step_input.text(),
            'dpi': self.dpi_input.text(),
            'zoom_bind': self.zoom_bind_input.text() # Сохранение бинда зума
        }

        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to save settings: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border-radius: 4px;
        }
        QWidget {
            border-radius: 5px;
        }

        QTreeWidget, QTableWidget {
            background-color: #333333;
            border: 1px solid #555555;
            color: #ffffff;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #1e2a3d;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            border: 1px solid #151f2d;

        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QGroupBox {
            background: #303030;
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 0.2ex;
            padding: 2px;
            margin: 5px;
            color: #ffffff;
        }
        QLineEdit {
            padding: 2px;
            background-color: #424242;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
            min-width: 23px;
            max-width: 23px;
            margin-left: 0px;
        }
        QLineEdit#folder_input {
            min-width: 400px;
            max-width: 400px;
            padding: 2px;
            background-color: #424242;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            background: #333333;
            border-radius: 4px;
        }
        QTabBar::tab {
            background: #424242;
            padding: 2px 12px;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
        }
        QTabBar::tab:selected {
            background: #1e2a3d;
        }
        QHeaderView::section {
            background-color: #424242;
            color: #ffffff;
            padding: 2px;
            border: 1px solid #555555;
            border-radius: 3px;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #072f6b;
            border-radius: 1px;
        }
        QCheckBox::indicator:checked {
            background-color: #1565c0;
            border: 2px solid #1e2a3d;
            border-radius: 1px;
        }
        QLabel {
            color: #ffffff;
            border-radius: 4px;
        }
        QMessageBox {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMessageBox QPushButton {
            background-color: #1e2a3d;
            color: white;
            border-radius: 4px;
            padding: 6px 12px;
            border: 1px solid #151f2d;
            min-width: 80px;
        }
    """)
    app.setStyle("Fusion")
    window.show()
    sys.exit(app.exec_())