# ----- Imports -----
import ast
import json
import math
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
from PyQt5.QtCore import Qt, QTimer

# ----- Constant Variables -----
GAME_DATA_URL = "https://reallylinux.nz/RaisSoftware/cw/game_data.json"
ZIP_FILES_URL = "https://reallylinux.nz/RaisSoftware/cw/game/"
CORE_FILES_URL = "https://reallylinux.nz/RaisSoftware/cw/game/corefiles/"

GAME_FOLDER = "CyclicWarriors"

ORIGINAL_HEIGHT = 540

DISPLAY_FPS = 60

MAX_COREFILE_THREADS = 4

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
    button_lock = threading.Lock()
    progress_lock = threading.Lock()
    pause_lock = threading.Lock()
    filesize_lock = threading.Lock()
    saved_data_lock = threading.Lock()

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
        Show the main window of the PyQt5 application, and start the update loop.

        Returns:
            None
        """
        cls.window.show()

        # Create a QTimer to update at the set FPS
        cls.timer = QTimer()
        cls.timer.timeout.connect(cls.update)
        cls.timer.start(1000 // DISPLAY_FPS)

    @classmethod
    def set_scene(cls, scene_id):
        # Remove all existing buttons and progressbar

        if scene_id == "update_launcher":
            pass
        elif scene_id == "download_game":
            cls.create_button("Download", cls.download_game)
            cls.setup_progress_bar()
        elif scene_id == "update_game":
            pass
        elif scene_id == "start":
            pass
        else:
            raise Exception(f'The scene_id "{scene_id}" in set_scene() is not valid.')
        
        cls.current_scene = scene_id
        
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
        cls.button = QPushButton(content, cls.window)
        cls.button.setGeometry(round(cls.window.width() / 2 - round(200 * cls.size_multiplier) / 2), int(cls.window.height() * 0.42), round(200 * cls.size_multiplier), round(50 * cls.size_multiplier))
        cls.button.setStyleSheet(
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

        # Add a shadow around the button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.button.setGraphicsEffect(shadow)

        # Apply hover and click changes
        cls.button.clicked.connect(connect)
        cls.button.setCursor(QCursor(Qt.PointingHandCursor))

        # Custom variable to declare when button state is paused
        cls.resume()

        cls.button_style_sheet = cls.button.styleSheet()
        cls.button_text = cls.button.text()
        cls.button_cursor = cls.button.cursor()
        cls.button_onclick = connect
        cls.button_previous_onclick = connect

    @classmethod
    def setup_progress_bar(cls):
        """
        Set up and configure the progress bar widget within the application window.

        This class method creates a QProgressBar widget, sets its position and style, and adds a drop shadow effect. It also initializes the progress bar and starts a separate thread for the marquee animation.

        Returns:
            None
        """
        # Create a Progressbar widget and style it
        cls.progress_bar = QProgressBar(cls.window)
        cls.progress_bar.setGeometry(cls.window.width() // 5, int(cls.window.height() * 0.55), 3 * cls.window.width() // 5, round(40 * cls.size_multiplier))
        cls.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 2px solid black;
                border-radius: 5px;
                text-align: center;
                font-size: {round(24 * cls.size_multiplier)}px;
            }}
            QProgressBar::chunk {{
                background-color: #2ad452;
                border-radius: 3px;
            }}
            """
        )

        # Add a shadow around the progress bar
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0))
        shadow.setOffset(0, 0)
        cls.progress_bar.setGraphicsEffect(shadow)

        # Progress bar completion
        cls.progress = 0
        
        # Color shift for marquee
        cls.color_base = 115
        cls.color_paused = 360
        cls.color_shift = 0
        cls.color_shift_increment = 0.04

    @classmethod
    def progress_bar_marquee(cls):
        """
        Function to animate a marquee-style progress bar.

        This class method is used to create an animated progress bar. It runs as a separate thread and continuously updates the progress bar's style, giving it a shifting gradient appearance. The animation enhances the visual feedback for users during long-running tasks. The animation is achieved by modifying the background color of the progress bar using HSL color values, and shifting along the bar with a sin wave.

        Returns:
            None
        """
        # Exit loop if progress bar does not exist
        multi = cls.progress_bar.value() / 100

        # Prevent unnecessary calculations and plausable errors
        if multi <= 0 or multi > 100:
            return

        cls.color_shift += cls.color_shift_increment
        
        if cls.get_paused():
            color_base = cls.color_paused
        else:
            color_base = cls.color_base

        # Define the background color using a single hsl() function
        hsl_color = lambda offset: f"hsl({round(color_base + math.sin(cls.color_shift + cls.color_shift_increment * offset) * 36) % 360}, 100%, 60%)"

        # Set the progress bar style to contain a shifting gradient
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
                    x1: 0, y1: 0,
                    x2: {1 / multi}, y2: 0,
                    stop: 0.0 {hsl_color(0)},
                    stop: 0.2 {hsl_color(12)},
                    stop: 0.4 {hsl_color(24)},
                    stop: 0.5 {hsl_color(36)},
                    stop: 0.6 {hsl_color(48)},
                    stop: 0.8 {hsl_color(60)},
                    stop: 1.0 {hsl_color(72)}
                );
                border-radius: 3px;
            }}
            """
        )

    @classmethod
    def pause(cls):
        """
        Pause the application and configure the button to resume when clicked.

        This class method is used to pause the application by safely setting the 'paused' flag to True and configuring the button's style sheet, behavior, and text for the resume action. This method is thread-safe.

        Returns:
            None
        """
        with cls.pause_lock:
            cls.paused = True
        
        cls.button_style_sheet = f"""
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
        cls.button_onclick = cls.resume
        cls.button_text = "Resume"

    @classmethod
    def resume(cls):
        """
        Resume the application and configure the button to pause when clicked.

        This class method is used to resume the application by safely setting the 'paused' flag to False and configuring the appearance and behavior of a button to indicate a pause action. This method is thread-safe.

        Returns:
        None
        """
        with cls.pause_lock:
            cls.paused = False
        
        cls.button_style_sheet = f"""
            :!hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #3e64d6;
                border-radius: 5px;
            }}

            :hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #5377e0;
                border-radius: 5px;
            }}
            """
        cls.button_onclick = cls.pause
        cls.button_text = "Pause"
    
    @classmethod
    def get_paused(cls):
        """
        Get the current pause state of the application.

        This class method is used to retrieve the current pause state of the application in a thread-safe manner by accessing the 'paused' flag within a lock.

        Returns:
            bool: True if the application is paused, False otherwise.
        """
        with cls.pause_lock:
            return cls.paused

    @classmethod
    def update(cls):
        if cls.current_scene == "update_launcher":
            pass
        elif cls.current_scene == "download_game":
            cls.progress_bar_marquee()

            with cls.progress_lock:
                if f"{cls.progress:.2f}%" != cls.progress_bar.format():
                    cls.progress_bar.setValue(round(cls.progress))

                    # Displaying the decimal value 
                    cls.progress_bar.setFormat(f"{cls.progress:.2f}%")
            
            with cls.button_lock:
                if cls.button_style_sheet != cls.progress_bar.styleSheet():
                    cls.button.setStyleSheet(cls.button_style_sheet)
                
                if cls.button_previous_onclick != cls.button_onclick:
                    cls.button_previous_onclick = cls.button_onclick
                    cls.button.clicked.disconnect()
                    cls.button.clicked.connect(cls.button_onclick)

                if cls.button_text != cls.button.text():
                    cls.button.setText(cls.button_text)

                if cls.button_cursor != cls.button.cursor():
                    cls.button.setCursor(cls.button_cursor)

        elif cls.current_scene == "update_game":
            pass
        elif cls.current_scene == "start":
            pass

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

    @classmethod
    def get_saved_data(cls):
        """
        Retrieve installed versions of an application from a JSON file.

        This static method reads "saved_data.json" to retrieve the installed versions of this Launcher and Cyclic Warriors, then returns these as a Python data structure.

        Returns:
            dict: A dictionary containing information about versions, and update progress.
        """
        with cls.saved_data_lock:
            with open("saved_data.json", "r") as file:
                    cls.saved_data = json.load(file)
                    return cls.saved_data
        
    @classmethod
    def set_saved_data(cls):
        """
        Save the current state of the application's saved data to a JSON file.

        This class method writes the contents of the 'saved_data' attribute to a file named "saved_data.json" in a formatted JSON structure with an indentation of 4 spaces.

        Returns:
            None
        """
        with cls.saved_data_lock:
            with open("saved_data.json", "w") as file:
                    json.dump(cls.saved_data, file, indent=4)
        
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

        cls.data = json_response
        return json_response
    
    @classmethod
    def extract_version_data(cls, parsed_json_data):
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
        cls.latest_version_data = {"GameVersion": latest_game_version, "LauncherVersion": latest_launcher_version}
        return cls.latest_version_data
    
    @classmethod
    def get_total_filesize(cls, urls, total_files):
        """
        Calculate the total file size for a list of URLs.

        This class method takes a list of file URLs, calculates the total size of the files by sending HEAD requests to each URL and summing the 'content-length' values from the response headers. It also updates a progress value based on the number of files processed.

        Args:
            urls (list): A list of URLs for the files.
            total_files (int): The total number of files to be processed.

        Returns:
            int: The total size of the files in bytes.
        """
        total_size = 0
        for url in urls:
            file_name = url.split("/")[-1]

            url = CORE_FILES_URL + file_name
            try:
                response = requests.head(url)
                if 'content-length' in response.headers:
                    total_size += int(response.headers['content-length'])
            except requests.exceptions.RequestException:
                pass
            
            with cls.progress_lock:
                cls.progress += (2 / total_files)

            while cls.get_paused():
                time.sleep(0.1)

        return total_size

    @classmethod
    def download_file(cls, file_path, folder_directory):
        file_path = f"{folder_directory}/{file_path}"

        file_name = file_path.split("/")[-1]
        file_location = "/".join(file_path.split("/")[:-1])

        url = CORE_FILES_URL + file_name

        response = requests.get(url, stream=True)

        if response.status_code == 200:
            os.makedirs(file_location, exist_ok=True)

            total_size = int(response.headers.get('content-length', 0))

            print(f"Downloading {file_path} ({total_size} bytes)")

            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=8192):
                    if data:
                        file.write(data)
                        downloaded_size = len(data)
                        with cls.progress_lock:
                            cls.progress += (98 / cls.total_filesize) * downloaded_size
                    
                    while cls.get_paused():
                        time.sleep(0.1)
            
            with cls.saved_data_lock:
                cls.saved_data["GameUpdate"]["CompletedProgress"] += (98 / cls.total_filesize) * total_size
                cls.saved_data["GameUpdate"]["DownloadedFiles"].append(file_path)
            
            cls.set_saved_data()

            print(f"File downloaded as {file_path}")
        else:
            print(f"Failed to download the file: {file_path}. Status code: {response.status_code}")

    @classmethod
    def download_core_files(cls, file_paths, total_files):
        """
        Download core game files concurrently and manage file size calculation.

        This class method is responsible for downloading core game files concurrently. It calculates the total file size of the specified files, updates shared variables to track download progress, and then initiates the file downloads.

        Args:
            file_paths (list): List of file paths to be downloaded.
            total_files (int): Total number of files to download.

        Returns:
            None
        """
        with cls.saved_data_lock:
            if cls.saved_data["GameUpdate"]["PartialDownload"] and cls.saved_data["GameUpdate"]["TotalFilesize"] > 0:
                skip_get_total_filesize = True
            else:
                skip_get_total_filesize = False

        if not skip_get_total_filesize:
            chunk_filesize = cls.get_total_filesize(file_paths, total_files)

            with cls.filesize_lock:
                cls.total_filesize += chunk_filesize
                cls.threads_finished_get_filesize += 1
            
            while True:
                with cls.filesize_lock:
                    if cls.threads_finished_get_filesize >= len(cls.threads):
                        break
                
                time.sleep(0.01)
            
            with cls.saved_data_lock and cls.filesize_lock:
                if cls.saved_data["GameUpdate"]["TotalFilesize"] != cls.total_filesize:
                    cls.saved_data["GameUpdate"]["TotalFilesize"] = cls.total_filesize
                    call_set_saved_data = True
                else:
                    call_set_saved_data = False

            if call_set_saved_data:
                cls.set_saved_data()

        for path in file_paths:
            cls.download_file(path, GAME_FOLDER)

    @classmethod
    def download_game(cls):
        cls.button_style_sheet = f"""
            :!hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #3e64d6;
                border-radius: 5px;
            }}

            :hover {{
                border: 1px solid black;
                font-size: {round(24 * cls.size_multiplier)}px;
                font-weight: bold;
                color: white;
                background-color: #5377e0;
                border-radius: 5px;
            }}
            """
        cls.button_onclick = cls.pause
        cls.button_text = "Pause"

        game_update = cls.saved_data["GameUpdate"]

        with cls.saved_data_lock:
            if game_update["PartialDownload"] and game_update["AttemptVersion"] == cls.latest_version_data["GameVersion"] and game_update["AttemptType"] == "Download":
                files = [item for item in cls.data["CurrentFiles"] if item not in game_update["DownloadedFiles"]]

                with cls.progress_lock:
                    cls.progress = game_update["CompletedProgress"] + 2

                cls.total_filesize = game_update["TotalFilesize"]
            else:
                files = cls.data["CurrentFiles"]
                game_update["PartialDownload"] = True
                game_update[""] = []
                game_update["AttemptVersion"] = cls.latest_version_data["GameVersion"]
                game_update["TotalFilesize"] = 0
                game_update["CompletedProgress"] = 0
                game_update["AttemptType"] = "Download"

                cls.total_filesize = 0

        cls.set_saved_data()

        # Split the list into chunks for each thread
        file_count = len(files)
        chunk_size = max(file_count // MAX_COREFILE_THREADS, 1)
        chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

        cls.threads_finished_get_filesize = 0

        # Create and start threads
        cls.threads = []
        for chunk in chunks:
            thread = threading.Thread(target=cls.download_core_files, args=(chunk, file_count), daemon=True)
            cls.threads.append(thread)
        
        for thread in cls.threads:
            thread.start()

        if cls.data["InitialDownload"] not in game_update["DownloadedFiles"]:
            pass

        #cls.initial_download_thread = threading.Thread(target=cls.download_initial, args=(GAME_FOLDER, ), daemon=True)


# ----- Main -----
def main():
    # Setup GUI
    Launcher.create_window()
    Launcher.setup_ui()
    
    # Get version data
    saved_data = Launcher.get_saved_data()
    data = Launcher.get_version_data()
    latest_versions = Launcher.extract_version_data(data)

    # Set required scene
    if saved_data["LauncherVersion"] < latest_versions["LauncherVersion"] and False:
        Launcher.set_scene("update_launcher")
        #--> Launcher.setup_launcher_download_threads() onclick
    elif saved_data["GameVersion"] == 0:
        Launcher.set_scene("download_game")
        #--> Launcher.setup_game_download_threads() onclick
    elif saved_data["GameVersion"] < latest_versions["GameVersion"]:
        Launcher.set_scene("update_game")
        #--> Launcher.setup_game_upload_threads() onclick
    else:
        Launcher.set_scene("start")
    
    Launcher.show()
    sys.exit(Launcher.app.exec_())

# ----- Entry Point -----
if __name__ == "__main__":
    main()