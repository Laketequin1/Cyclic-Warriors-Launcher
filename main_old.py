import sys
import json
import ast
import os
import subprocess
import zipfile
import time
import psutil
import random
import requests
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt

ORIGINAL_HEIGHT = 540

def clamp(value):
    return max(0, min(1, value))

class Downloader:
    url = 'https://reallylinux.nz/RaisSoftware/cw/game_data.json'

    @classmethod
    def init(cls):
        response = requests.get(cls.url)
        data = cls.evaluate_message(cls.fix_json(str(response.content)))
        saved_data = cls.get_saved_data()

        if saved_data["LauncherVersion"] < data["Launcher"] and False:
            cls.update_launcher()
        elif saved_data["GameVersion"] == 0:
            cls.download_game_setup()
        elif saved_data["GameVersion"] < max(data["PatchChanges"].keys()):
            cls.update_game()
        else:
            cls.start()

    @staticmethod
    def get_saved_data():
        with open("saved_data.json", "r") as file:
            return json.load(file)

    @staticmethod
    def fix_json(message: str):
        message = message.replace("\\n", "").replace("\\r", "").replace("\\t", "")
        return message[2:len(message) - 1]
    
    @staticmethod
    def evaluate_message(message):
        if message:
            return ast.literal_eval(message)
        return None

    @staticmethod
    def execute(executable_path):
        subprocess.Popen(executable_path)
    
    @classmethod
    def update_launcher(cls):
        print("UPDATE LAUNCHER!!")

    @classmethod
    def download_game_setup(cls):
        print("DOWNLOAD SETUP!!")
        GUI.setup_download_ui()

    @classmethod
    def update_game(cls):
        print("UPDATE GAME!!")

    @classmethod
    def download_loop(cls):
        cls

    @classmethod
    def download_game(cls):
        print("DOWNLOAD GAME!!")
        GUI.download_button.setStyleSheet(
            f"""
            :!hover {{
                border: 1px solid black;
                font-size: {round(24 * GUI.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #3e64d6;
                border-radius: 5px;
            }}

            :hover {{
                border: 1px solid black;
                font-size: {round(24 * GUI.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #5377e0;
                border-radius: 5px;
            }}
            """
        )
        GUI.download_button.clicked.disconnect(cls.download_game)
        GUI.download_button.clicked.connect(cls.pause)
        GUI.download_button.setText("Pause")

        for i in range(1001):
            if GUI.download_button.canceled:
                break
            GUI.progress_bar.setValue(round(i / 10))
            GUI.app.processEvents()
            if random.randint(1, 100) == 100:
                time.sleep(4.5)
            else:
                time.sleep(0.005)
        else:
            GUI.download_button.setStyleSheet(
                f"""
                border: 1px solid black;
                font-size: {round(24 * GUI.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #2ad452;
                border-radius: 5px;
                """
            )
            GUI.download_button.clicked.disconnect(cls.pause)
            GUI.download_button.setText("FINISHED!")
            GUI.download_button.setCursor(QCursor(Qt.ArrowCursor))
            GUI.app.processEvents()
            time.sleep(1)
            GUI.close_elements()
            return

        GUI.download_button.setStyleSheet(
            f"""
            :!hover {{
                border: 1px solid black;
                font-size: {round(24 * GUI.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #1948d1;
                border-radius: 5px;
            }}

            :hover {{
                border: 1px solid black;
                font-size: {round(24 * GUI.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #2c59de;
                border-radius: 5px;
            }}
            """
        )
        GUI.download_button.clicked.disconnect(cls.pause)
        GUI.download_button.clicked.connect(cls.download_game)
        GUI.download_button.canceled = False
        GUI.download_button.setText("Resume")

    @classmethod
    def pause(cls):
        GUI.download_button.canceled = True

    @classmethod
    def start(cls):
        print("START!!")

        
class GUI:
    @classmethod
    def setup_ui(cls, app: QApplication, window, size_multiplier):
        cls.app = app
        cls.window = window
        cls.size_multiplier = size_multiplier

        # Set the window icon
        cls.window.setWindowIcon(QIcon("images/icon.ico"))  # Replace with the actual path to your icon file

        # Get screen dimensions
        screen_width = app.primaryScreen().size().width()
        screen_height = app.primaryScreen().size().height()
        window_width = screen_width // 2
        window_height = screen_height // 2

        # Set the window title and dimensions
        cls.window.setWindowTitle("Cyclic Warriors Launcher")
        cls.window.setFixedSize(window_width, window_height)

        # Create a QLabel for the background image
        background_label = QLabel(cls.window)
        background_label.setGeometry(0, 0, window_width, window_height)
        background_image = QPixmap("images/background.jpg")  # Change to your image file path
        background_image = background_image.scaled(window_width, window_height)
        background_label.setPixmap(background_image)

        # Add a title label with bold text, centered
        cls.title_label = QLabel("Cyclic Warriors Launcher", cls.window)
        cls.title_label.setAlignment(Qt.AlignCenter)
        cls.title_label.setGeometry(0, round(window_height * 0.1), window_width, round(60 * size_multiplier))
        cls.title_label.setStyleSheet(f"font-size: {round(48 * size_multiplier)}px; font-weight: bold; color: white;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.title_label.setGraphicsEffect(shadow)

    @classmethod
    def setup_download_ui(cls):
        cls.setup_download_button()
        cls.setup_progress_bar()

    @classmethod
    def setup_download_button(cls):
        # Create a button widget and style it
        cls.download_button = QPushButton("Download", cls.window)
        cls.download_button.setGeometry(round(cls.window.width() / 2 - round(200 * cls.size_multiplier) / 2), int(cls.window.height() * 0.42), round(200 * cls.size_multiplier), round(50 * cls.size_multiplier))
        cls.download_button.clicked.connect(Downloader.download_game)
        cls.download_button.canceled = False
        cls.download_button.setStyleSheet(
            f"""
            :!hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #1948d1;
                border-radius: 5px;
            }}

            :hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #2c59de;
                border-radius: 5px;
            }}
            """
        )
        cls.download_button.setCursor(QCursor(Qt.PointingHandCursor))
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.download_button.setGraphicsEffect(shadow)

    @classmethod
    def setup_progress_bar(cls):
        # Create a Progressbar widget
        cls.progress_bar = QProgressBar(cls.window)
        cls.progress_bar.setGeometry(cls.window.width() // 5, int(cls.window.height() * 0.55), 3 * cls.window.width() // 5, round(40 * cls.size_multiplier))
        cls.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-size: 24px;
            }
            QProgressBar::chunk {
                background-color: #2ad452;
                border-radius: 3px;
            }
            """
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.progress_bar.setGraphicsEffect(shadow)
        
        progress_bar_thread = threading.Thread(target=cls.progress_bar_marquee, daemon=True)
        progress_bar_thread.start()

    @classmethod
    def progress_bar_marquee(cls):
        color_shift = 0
        color_shift_increment = 2
        while True:
            multi = cls.progress_bar.value() / 100
            if multi <= 0:
                time.sleep(0.1)
                continue
            elif multi >= 100:
                return
            
            color_shift += color_shift_increment
            
            cls.progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    border: 2px solid black;
                    border-radius: 5px;
                    text-align: center;
                    font-size: {round(24 * cls.size_multiplier)}px;
                }}
                QProgressBar::chunk {{
                    background-color: qlineargradient(
                        x1: 0,
                        y1: 0,
                        x2: {1 / multi},
                        y2: 0,
                        stop: 0.0 hsl({(0   + color_shift) % 360}, 100%, 60%),
                        stop: 0.1 hsl({(30  + color_shift) % 360}, 100%, 60%),
                        stop: 0.2 hsl({(60  + color_shift) % 360}, 100%, 60%),
                        stop: 0.3 hsl({(90  + color_shift) % 360}, 100%, 60%),
                        stop: 0.4 hsl({(120 + color_shift) % 360}, 100%, 60%),
                        stop: 0.5 hsl({(150 + color_shift) % 360}, 100%, 60%),
                        stop: 0.6 hsl({(180 + color_shift) % 360}, 100%, 60%),
                        stop: 0.7 hsl({(210 + color_shift) % 360}, 100%, 60%),
                        stop: 0.8 hsl({(240 + color_shift) % 360}, 100%, 60%),
                        stop: 0.9 hsl({(270 + color_shift) % 360}, 100%, 60%),
                        stop: 1.0 hsl({(300 + color_shift) % 360}, 100%, 60%)
                    );
                    border-radius: 3px;
                }}
                """
            )
            time.sleep(0.05)
            cls.app.processEvents()

    @classmethod
    def close_elements(cls):
        # Hide or remove the download button, progress bar, and other elements
        cls.download_button.hide()  # Hide the download button
        cls.progress_bar.hide()    # Hide the progress bar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    size_multiplier = window.height() / ORIGINAL_HEIGHT

    GUI.setup_ui(app, window, size_multiplier)
    Downloader.init()

    # Center the window on the screen
    screen_center_x = (app.primaryScreen().size().width() - window.width()) // 2
    screen_center_y = (app.primaryScreen().size().height() - window.height()) // 2
    window.setGeometry(screen_center_x, screen_center_y, window.width(), window.height())

    window.show()
    sys.exit(app.exec_())
