import sys
import random
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class CenteredButtonWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Changing Text Button")
        self.setGeometry(100, 100, 400, 200)

        # Create a central widget and set a layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Create a button and add it to the layout
        self.button = QPushButton("Change Me")
        layout.addWidget(self.button)

        # Center the button within the layout
        layout.addStretch(1)
        layout.addWidget(self.button)
        layout.addStretch(1)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

        # Create a QTimer to change the text every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_button_text)
        self.timer.start(1000)  # Trigger every 1000 milliseconds (1 second)

    def change_button_text(self):
        random_number = random.randint(1, 100)
        self.button.setText(str(random_number))

def main():
    app = QApplication(sys.argv)
    window = CenteredButtonWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
