import sys
import os
import base64
import json
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QFileDialog, QMessageBox, QLineEdit, QListWidget, 
                             QSplitter, QProgressBar, QComboBox, QStackedWidget, QScrollArea, QCheckBox)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QSize

class WorkerSignals(QObject):
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

class ImageProcessWorker(QRunnable):
    def __init__(self, api_url, image_data, prompt):
        super().__init__()
        self.api_url = api_url
        self.image_data = image_data
        self.prompt = prompt
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(25)
            encoded_image = base64.b64encode(self.image_data).decode('utf-8')
            self.signals.progress.emit(50)
            payload = {
                "contents": [{
                    "parts": [
                        {"text": self.prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded_image
                            }
                        }
                    ]
                }]
            }
            headers = {'Content-Type': 'application/json'}
            self.signals.progress.emit(75)
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json()
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                self.signals.result.emit(generated_text)
            else:
                self.signals.error.emit(f"API request failed with status code: {response.status_code}")
            self.signals.progress.emit(100)
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.progress.emit(100)

class AdvancedGeminiImageIdentifierApp(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        self.image_data = None
        self.history = []
        self.threadpool = QThreadPool()
        self.dark_mode = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced Image Identifier")
        self.setGeometry(100, 100, 1200, 800)
        self.apply_stylesheet()
        
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel for image and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("border: 2px dashed #cccccc; border-radius: 8px;")
        left_layout.addWidget(self.image_label)

        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select Image")
        self.select_button.clicked.connect(self.select_image)
        button_layout.addWidget(self.select_button)

        save_button = QPushButton("Save Image with Analysis")
        save_button.clicked.connect(self.save_image_with_analysis)
        button_layout.addWidget(save_button)

        left_layout.addLayout(button_layout)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter custom prompt here")
        left_layout.addWidget(self.prompt_input)

        self.identify_button = QPushButton("Identify Image")
        self.identify_button.clicked.connect(self.identify_image)
        left_layout.addWidget(self.identify_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        left_panel.setLayout(left_layout)

        # Right panel for results and history
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        self.result_tabs = QStackedWidget()

        # Text result widget
        text_result_widget = QWidget()
        text_result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        text_result_layout.addWidget(QLabel("Text Analysis:"))
        text_result_layout.addWidget(self.result_text)
        text_result_widget.setLayout(text_result_layout)

        self.result_tabs.addWidget(text_result_widget)

        result_type_selector = QComboBox()
        result_type_selector.addItems(["Text Analysis"])
        right_layout.addWidget(result_type_selector)
        right_layout.addWidget(self.result_tabs)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        right_layout.addWidget(QLabel("History:"))
        right_layout.addWidget(self.history_list)

        button_layout = QHBoxLayout()

        clear_history_button = QPushButton("Clear History")
        clear_history_button.clicked.connect(self.clear_history)
        button_layout.addWidget(clear_history_button)

        export_button = QPushButton("Export Results")
        export_button.clicked.connect(self.export_results)
        button_layout.addWidget(export_button)

        right_layout.addLayout(button_layout)

        # Additional customization options
        font_layout = QHBoxLayout()

        self.font_size_selector = QComboBox()
        self.font_size_selector.addItems([str(i) for i in range(10, 25)])
        self.font_size_selector.currentTextChanged.connect(self.change_font_size)
        font_layout.addWidget(QLabel("Font Size:"))
        font_layout.addWidget(self.font_size_selector)

        self.dark_mode_toggle = QCheckBox("Dark Mode")
        self.dark_mode_toggle.stateChanged.connect(self.toggle_dark_mode)
        font_layout.addWidget(self.dark_mode_toggle)

        right_layout.addLayout(font_layout)

        right_panel.setLayout(right_layout)

        # Add splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.statusBar().showMessage("Ready")

    def apply_stylesheet(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 14px;
                    margin: 4px 2px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QLineEdit, QTextEdit, QListWidget {
                    border: 1px solid #666666;
                    background-color: #3c3c3c;
                    color: #f0f0f0;
                    border-radius: 4px;
                    padding: 6px;
                }
                QLabel {
                    font-size: 14px;
                    color: #f0f0f0;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    text-align: center;
                    text-decoration: none;
                    font-size: 14px;
                    margin: 4px 2px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QLineEdit, QTextEdit, QListWidget {
                    border: 1px solid #dcdcdc;
                    background-color: #ffffff;
                    color: #000000;
                    border-radius: 4px;
                    padding: 6px;
                }
                QLabel {
                    font-size: 14px;
                    color: #000000;
                }
            """)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            self.load_image(file_name)

    def load_image(self, file_path):
        with open(file_path, "rb") as image_file:
            self.image_data = image_file.read()
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.statusBar().showMessage("Image loaded successfully")

    def identify_image(self):
        if self.image_data is None:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return

        prompt = self.prompt_input.text() or "Describe this image in detail. Identify objects, people, or scenes present."
        self.statusBar().showMessage("Processing...")
        self.progress_bar.setValue(0)
        
        worker = ImageProcessWorker(self.api_url, self.image_data, prompt)
        worker.signals.result.connect(self.handle_result)
        worker.signals.error.connect(self.handle_error)
        worker.signals.progress.connect(self.update_progress)
        self.threadpool.start(worker)

    def handle_result(self, result):
        self.result_text.setPlainText(result)
        self.statusBar().showMessage("Image identified successfully")
        self.add_to_history(result)
        self.progress_bar.setValue(100)

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.statusBar().showMessage("Failed to identify image")
        self.progress_bar.setValue(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def add_to_history(self, result):
        self.history.append(result)
        self.history_list.addItem(f"Analysis {len(self.history)}")

    def load_history_item(self, item):
        index = self.history_list.row(item)
        self.result_text.setPlainText(self.history[index])

    def clear_history(self):
        self.history.clear()
        self.history_list.clear()
        self.result_text.clear()
        self.statusBar().showMessage("History cleared")

    def export_results(self):
        if not self.history:
            QMessageBox.warning(self, "Error", "No results to export.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'w') as f:
                for i, result in enumerate(self.history, 1):
                    f.write(f"Analysis {i}:\n{result}\n\n")
            self.statusBar().showMessage(f"Results exported to {file_name}")

    def save_image_with_analysis(self):
        if self.image_data is None or not self.result_text.toPlainText():
            QMessageBox.warning(self, "Error", "Please select an image and perform analysis first.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image with Analysis", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = self.image_label.pixmap()
            image = pixmap.toImage()

            painter = QPainter(image)
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Arial", 20))
            painter.drawText(image.rect(), Qt.AlignBottom | Qt.AlignLeft, self.result_text.toPlainText())
            painter.end()

            image.save(file_name)
            self.statusBar().showMessage(f"Image saved with analysis to {file_name}")

    def change_font_size(self, size):
        font = self.result_text.font()
        font.setPointSize(int(size))
        self.result_text.setFont(font)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_stylesheet()

if __name__ == "__main__":
    API_KEY = ""  # Replace with your actual API key
    app = QApplication(sys.argv)
    ex = AdvancedGeminiImageIdentifierApp(API_KEY)
    ex.show()
    sys.exit(app.exec_())

