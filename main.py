import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt

ORIGINAL_HEIGHT = 540

def clamp(value):
    return max(0, min(1, value))

class GUI:
    class Download:
        def __init__(self, app, window, size_multiplier):
            self.app = app
            self.window = window
            self.size_multiplier = size_multiplier

            self.setup_ui()
            self.setup_download_button()
            self.setup_progress_bar()

        def setup_ui(self):
            # Set the window icon
            self.window.setWindowIcon(QIcon("images/icon.ico"))  # Replace with the actual path to your icon file

            # Get screen dimensions
            screen_width = self.app.primaryScreen().size().width()
            screen_height = self.app.primaryScreen().size().height()
            window_width = screen_width // 2
            window_height = screen_height // 2

            # Set the window title and dimensions
            self.window.setWindowTitle("Cyclic Warriors Launcher")
            self.window.setFixedSize(window_width, window_height)

            # Create a QLabel for the background image
            background_label = QLabel(self.window)
            background_label.setGeometry(0, 0, window_width, window_height)
            background_image = QPixmap("images/background.jpg")  # Change to your image file path
            background_image = background_image.scaled(window_width, window_height)
            background_label.setPixmap(background_image)

            # Add a title label with bold text, centered
            self.title_label = QLabel("Cyclic Warriors Launcher", self.window)
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setGeometry(0, round(window_height * 0.1), window_width, round(60 * self.size_multiplier))
            self.title_label.setStyleSheet(f"font-size: {round(48 * self.size_multiplier)}px; font-weight: bold; color: white;")
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0))
            shadow.setOffset(0, 0)
            self.title_label.setGraphicsEffect(shadow)

        def setup_download_button(self):
            # Create a button widget and style it
            self.download_button = QPushButton("Download", self.window)
            self.download_button.setGeometry(round(self.window.width() / 2 - round(200 * self.size_multiplier) / 2), int(self.window.height() * 0.42), round(200 * self.size_multiplier), round(50 * self.size_multiplier))
            self.download_button.clicked.connect(self.download)
            self.download_button.canceled = False
            self.download_button.setStyleSheet(
                f"""
                :!hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #1948d1;
                    border-radius: 5px;
                }}

                :hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #2c59de;
                    border-radius: 5px;
                }}
                """
            )
            self.download_button.setCursor(QCursor(Qt.PointingHandCursor))
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0))
            shadow.setOffset(0, 0)
            self.download_button.setGraphicsEffect(shadow)

        def setup_progress_bar(self):
            # Create a Progressbar widget
            self.progress_bar = QProgressBar(self.window)
            self.progress_bar.setGeometry(self.window.width() // 5, int(self.window.height() * 0.55), 3 * self.window.width() // 5, round(30 * self.size_multiplier))
            self.progress_bar.setStyleSheet(
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
            self.progress_bar.setGraphicsEffect(shadow)

        def download(self):
            self.download_button.setStyleSheet(
                f"""
                :!hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #3e64d6;
                    border-radius: 5px;
                }}

                :hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #5377e0;
                    border-radius: 5px;
                }}
                """
            )
            self.download_button.clicked.disconnect(self.download)
            self.download_button.clicked.connect(self.pause)
            self.download_button.setText("Pause")

            import time
            for i in range(1001):
                if self.download_button.canceled:
                    break
                self.progress_bar.setValue(round(i / 10))
                self.app.processEvents()
                time.sleep(0.01)
            else:
                self.download_button.setStyleSheet(
                    f"""
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #2ad452;
                    border-radius: 5px;
                    """
                )
                self.download_button.clicked.disconnect(self.pause)
                self.download_button.setText("FINISHED!")
                self.download_button.setCursor(QCursor(Qt.ArrowCursor))
                self.app.processEvents()
                time.sleep(1)
                self.close_elements()
                return

            self.download_button.setStyleSheet(
                f"""
                :!hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #1948d1;
                    border-radius: 5px;
                }}

                :hover {{
                    border: 1px solid black;
                    font-size: {round(24 * self.size_multiplier)}px;
                    font-weight: bold;
                    color: white;
                    background-color: #2c59de;
                    border-radius: 5px;
                }}
                """
            )
            self.download_button.clicked.disconnect(self.pause)
            self.download_button.clicked.connect(self.download)
            self.download_button.canceled = False
            self.download_button.setText("Resume")

        def pause(self):
            self.download_button.canceled = True

        def close_elements(self):
            # Hide or remove the download button, progress bar, and other elements
            self.download_button.hide()  # Hide the download button
            self.progress_bar.hide()    # Hide the progress bar

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    size_multiplier = window.height() / ORIGINAL_HEIGHT

    download_manager = GUI.Download(app, window, size_multiplier)

    # Center the window on the screen
    screen_center_x = (app.primaryScreen().size().width() - window.width()) // 2
    screen_center_y = (app.primaryScreen().size().height() - window.height()) // 2
    window.setGeometry(screen_center_x, screen_center_y, window.width(), window.height())

    window.show()
    sys.exit(app.exec_())
