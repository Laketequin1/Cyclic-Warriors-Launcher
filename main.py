import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QProgressBar, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QIcon, QColor, QCursor
from PyQt5.QtCore import Qt, QPropertyAnimation

ORIGINAL_HEIGHT = 540

def download():
    import time
    for i in range(101):
        progress_bar.setValue(i)
        app.processEvents()
        time.sleep(0.05)

app = QApplication(sys.argv)
window = QMainWindow()

# Set the window icon
window.setWindowIcon(QIcon("images/icon.ico"))  # Replace with the actual path to your icon file

# Get screen dimensions
screen_width = app.primaryScreen().size().width()
screen_height = app.primaryScreen().size().height()
window_width = screen_width // 2
window_height = screen_height // 2

size_multiplier = window_height / ORIGINAL_HEIGHT

# Set the window title and dimensions
window.setWindowTitle("Cyclic Warriors Launcher")
window.setFixedSize(window_width, window_height)

# Create a QLabel for the background image
background_label = QLabel(window)
background_label.setGeometry(0, 0, window_width, window_height)
background_image = QPixmap("images/background.jpg")  # Change to your image file path
background_image = background_image.scaled(window_width, window_height)
background_label.setPixmap(background_image)

# Add a title label with bold text, centered
title_label = QLabel("Cyclic Warriors Launcher", window)
title_label.setAlignment(Qt.AlignCenter)
title_label.setGeometry(0, round(window_height * 0.1), window_width, round(60 * size_multiplier))
title_label.setStyleSheet(f"font-size: {round(48 * size_multiplier)}px; font-weight: bold; color: white;")
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(10)
shadow.setColor(QColor(0, 0, 0))
shadow.setOffset(0, 0)
title_label.setGraphicsEffect(shadow)

# Create a button widget and style it
download_button = QPushButton("Download", window)
download_button.setGeometry(round(window_width / 2 - round(200 * size_multiplier) / 2), int(window_height * 0.4), round(200 * size_multiplier), round(50 * size_multiplier))
download_button.clicked.connect(download)
download_button.setStyleSheet(
    f"""
        :!hover {{
            border: 1px solid black;
            font-size: {round(24 * size_multiplier)}px;
            font-weight: bold;
            color: white;
            background-color: #1948d1;
            border-radius: 5px;
        }}

        :hover {{
            border: 1px solid black;
            font-size: {round(24 * size_multiplier)}px;
            font-weight: bold;
            color: white;
            background-color: #2c59de;
            border-radius: 5px;
        }}
    """
)
download_button.setCursor(QCursor(Qt.PointingHandCursor))
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(10)
shadow.setColor(QColor(0, 0, 0))
shadow.setOffset(0, 0)
download_button.setGraphicsEffect(shadow)

# Create a Progressbar widget
progress_bar = QProgressBar(window)
progress_bar.setGeometry(int(window_width / 2 - 100), int(window_height * 0.6), 200, 30)
progress_bar.setStyleSheet("QProgressBar {border: 2px solid grey; border-radius: 5px;} QProgressBar::chunk {background-color: blue; border-radius: 3px;}")
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(10)
shadow.setColor(QColor(0, 0, 0))
shadow.setOffset(0, 0)
progress_bar.setGraphicsEffect(shadow)


# Center the window on the screen
screen_center_x = (screen_width - window_width) // 2
screen_center_y = (screen_height - window_height) // 2
window.setGeometry(screen_center_x, screen_center_y, window_width, window_height)

window.show()
sys.exit(app.exec_())
