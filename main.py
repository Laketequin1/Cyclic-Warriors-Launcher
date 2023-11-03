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
class Launcher:
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

    @classmethod
    def set_scene(cls, scene_id):
        if scene_id == "update_launcher":
            pass
        elif scene_id == "download_game":
            cls.create_button("Download", print)
        elif scene_id == "update_game":
            pass
        elif scene_id == "start":
            pass
        else:
            raise Exception(f'The scene_id "{scene_id}" in set_scene() is not valid.')
        
    @classmethod
    def create_button(cls, content, connect):
        """
        Create and style a custom button widget in the application window.

        Args:
            content (str): The text content displayed on the button.
            connect (callable): The function or method to connect to the button's click event.

        Returns:
            None
        """
        # Create a button widget and style it
        button = QPushButton(content, cls.window)
        button.setGeometry(round(cls.window.width() / 2 - round(200 * cls.size_multiplier) / 2), int(cls.window.height() * 0.42), round(200 * cls.size_multiplier), round(50 * cls.size_multiplier))
        button.setStyleSheet(
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

        # Add shadow around the button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        button.setGraphicsEffect(shadow)

        # Apply hover and click changes
        button.clicked.connect(connect)
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # Custom variable to declare ???? 
        button.canceled = "Why? Rename?"

    # ----- Launcher -----
    @staticmethod
    def fix_json(message: str):
        """
        Fix a JSON-like string by removing escape characters.

        This static method takes a JSON message as input, removes escape characters for newline, carriage return, tab, and trims any leading and trailing spaces.

        Args:
            message (str): The input JSON-like string to be fixed.

        Returns:
            str: The fixed JSON-like string with escape characters removed and outer quotes stripped.
        """
        message = message.replace("\\n", "").replace("\\r", "").replace("\\t", "").strip()
        return message[2:len(message) - 1]
    
    @staticmethod
    def evaluate_message(message):
        """
        Safely evaluate a message as a literal Python expression.

        This function is used to convert the request content to a Python data structure.

        Args:
            message (str): The message to be evaluated as a Python expression.

        Returns:
            object: The result of the evaluation, or None if the message is empty or unable to be evaluated.
        """
        if message:
            return ast.literal_eval(message)
        return None

    @staticmethod
    def get_installed_versions():
        """
        Retrieve installed versions of an application from a JSON file.

        This static method reads "saved_data.json" to retrieve the installed versions of this Launcher and Cyclic Warriors, then returns these as a Python data structure.

        Returns:
            dict: A dictionary containing information about installed Game and Launcher versions.
        """
        with open("saved_data.json", "r") as file:
            return json.load(file)
        
    @classmethod
    def get_version_data(cls):
        """
        Fetch and process the latest versions of the Launcher and Cyclic Warriors game data.

        This class method sends a GET request to the GAME_DATA_URL on the official website, processes the response content, and then evaluates it as JSON data.
        
        The JSON content includes information on:
        - InitialDownload (str): Name of the zip file required for the original download.
        - CurrentFiles (list): Required files and binary paths for the latest game version.
        - PatchChanges (dict): File changes for each version update, with version numbers as keys and affected files in a dict.
        - Launcher (int): The most recent launcher version.

        Returns:
            dict: A dictionary containing the parsed JSON data.
        """
        response = requests.get(GAME_DATA_URL)
        content = cls.fix_json(str(response.content))
        json_response = cls.evaluate_message(content)
        return json_response
    
    @staticmethod
    def extract_version_data(parsed_json_data):
        """
        Extract the latest game and launcher versions from parsed JSON data.

        This static method takes a parsed JSON data dictionary as input and extracts the latest game version and launcher version information.

        Args:
            parsed_json_data (dict): Parsed JSON data containing version information.

        Returns:
            dict: A dictionary with keys "GameVersion" and "LauncherVersion" representing the latest game and launcher versions.
        """
        latest_game_version = max(parsed_json_data["PatchChanges"].keys())
        latest_launcher_version = int(parsed_json_data["Launcher"])
        return {"GameVersion": latest_game_version, "LauncherVersion": latest_launcher_version}


# ----- Main -----
def main():
    # Setup GUI
    Launcher.create_window()
    Launcher.setup_ui()
    
    # Get version data
    installed_versions = Launcher.get_installed_versions()
    data = Launcher.get_version_data()
    latest_versions = Launcher.extract_version_data(data)

    # Set required scene
    if installed_versions["LauncherVersion"] < latest_versions["LauncherVersion"] and False:
        Launcher.set_scene("update_launcher")
        #--> Launcher.setup_launcher_download_threads() onclick
    elif installed_versions["GameVersion"] == 0:
        Launcher.set_scene("download_game")
        #--> Launcher.setup_game_download_threads() onclick
    elif installed_versions["GameVersion"] < latest_versions["GameVersion"]:
        Launcher.set_scene("update_game")
        #--> Launcher.setup_game_upload_threads() onclick
    else:
        Launcher.set_scene("start")
    
    Launcher.show()
    sys.exit(Launcher.app.exec_())

# ----- Entry Point -----
if __name__ == "__main__":
    main()