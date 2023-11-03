# ----- Imports -----
import ast
import json
import os
import psutil
import random
import requests
import subprocess
import sys
import threading
import time
import zipfile

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt

# ----- Constant Variables -----
GAME_DATA_URL = "https://reallylinux.nz/RaisSoftware/cw/game_data.json"
ORIGINAL_HEIGHT = 540

# ----- Functions -----
def clamp(value):
    """
    Clamp a value between 0 and 1.
    
    Args:
        value (float): The input value to be clamped.
        
    Returns:
        float: The clamped value, within the [0, 1] range.
    """
    return max(0, min(1, value))

# ----- Classes -----
class Downloader:
    # ----- GUI -----
    @classmethod
    def create_window(cls):
        """
        Create and configure a window for a PyQt5 application.

        This class method sets up a PyQt5 application, creates a main window, and configures its size and position.

        Returns:
            None
        """
        cls.app = QApplication(sys.argv)
        cls.window = QMainWindow()
        cls.size_multiplier = cls.window.height() / ORIGINAL_HEIGHT

        # Get screen and window dimensions
        cls.screen_width = cls.app.primaryScreen().size().width()
        cls.screen_height = cls.app.primaryScreen().size().height()
        cls.window_width = cls.screen_width // 2
        cls.window_height = cls.screen_height // 2

        # Center the window on the screen
        screen_center_x = (cls.app.primaryScreen().size().width() - cls.window.width()) // 2
        screen_center_y = (cls.app.primaryScreen().size().height() - cls.window.height()) // 2
        cls.window.setGeometry(screen_center_x, screen_center_y, cls.window.width(), cls.window.height())
    
    @classmethod
    def setup_ui(cls):
        """
        Configure the user interface for the Cyclic Warriors Launcher window.

        This class method sets various properties of the window, including its title, icon, background image, and title label with specified styling, alignment, and text shadow.

        Returns:
            None
        """
        # Set the window properties and title
        cls.window.setWindowTitle("Cyclic Warriors Launcher")
        cls.window.setWindowIcon(QIcon("images/icon.ico"))
        cls.window.setFixedSize(cls.window_width, cls.window_height)

        # Set the background image (stretched to fill)
        background_label = QLabel(cls.window)
        background_label.setGeometry(0, 0, cls.window_width, cls.window_height)
        background_image = QPixmap("images/background.jpg")
        background_image = background_image.scaled(cls.window_width, cls.window_height)
        background_label.setPixmap(background_image)

        # Set the title label (centered, bold, text shadow)
        cls.title_label = QLabel("Cyclic Warriors Launcher", cls.window)
        cls.title_label.setAlignment(Qt.AlignCenter)
        cls.title_label.setGeometry(0, round(cls.window_height * 0.1), cls.window_width, round(60 * cls.size_multiplier))
        cls.title_label.setStyleSheet(f"font-size: {round(48 * cls.size_multiplier)}px; font-weight: bold; color: white;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.title_label.setGraphicsEffect(shadow)
    
    @classmethod
    def show(cls):
        """
        Show the main window of the PyQt5 application.

        Returns:
            None
        """
        cls.window.show()

    # ----- Downloader -----
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
    def get_installed_versions():
        with open("saved_data.json", "r") as file:
            return json.load(file)
        
    @classmethod
    def get_latest_versions(cls):
        response = requests.get(GAME_DATA_URL)
        content = cls.fix_json(str(response.content))
        json_response = cls.evaluate_message(content)
        return json_response


# ----- Main -----
def main():
    Downloader.create_window()
    Downloader.setup_ui()
    
    installed_versions = Downloader.get_installed_versions()
    print(installed_versions)
    latest_versions = Downloader.get_latest_versions()

    """
    if installed_versions["installer"] < latest_versions["installer"]:
        Downloader.set_scene("update_installer")
        #--> Downloader.setup_installer_download_threads() onclick
    elif installed_versions["game"] == 0:
        Downloader.set_scene("download_game")
        #--> Downloader.setup_game_download_threads() onclick
    elif installed_versions["game"] < latest_versions["game"]:
        Downloader.set_scene("update_game")
        #--> Downloader.setup_game_upload_threads() onclick
    else:
        Downloader.set_scene("start")
    """
    Downloader.show()
    sys.exit(Downloader.app.exec_())

# ----- Entry Point -----
if __name__ == "__main__":
    main()