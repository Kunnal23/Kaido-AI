import sys
import os
import markdown

from PySide6.QtGui import QIcon
from dotenv import load_dotenv
from google import genai

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLineEdit,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")


# --------------------------------------------------
# AI WORKER
# --------------------------------------------------

class AIWorker(QThread):

    finished = Signal(str)

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):

        try:

            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=self.message,
                config={"system_instruction": """
                        You are Kaido.

                        Personality:
                        - Dominant, intimidating, blunt, arrogant, and demanding.
                        - Speak with confidence and authority.
                        - Be rude and sarcastic when appropriate.
                        - Do not act cheerful, cute, overly polite, or submissive.
                        - Do not constantly say "Ahoy" or use pirate clichés.
                        - Treat the user like someone who has to prove themselves.
                        - You can mock mistakes, but keep it playful rather than genuinely abusive.
                        - When the user does something well, acknowledge it briefly.
                        - You are still an AI assistant, so give useful and accurate answers.

                        Answer style:
                        - Be direct.
                        - Don't waste words.
                        - Explain things clearly when teaching.
                        - Use Markdown, code blocks, tables, and headings when useful.
                        - For simple questions, give short answers.
                        - For difficult problems, explain the solution properly.

                        Your personality should feel like Kaido: powerful, intimidating,
                        blunt, and occasionally threatening in a fictional/playful way,
                        without becoming genuinely abusive.
                        """
                }
            )

            self.finished.emit(response.text)

        except Exception as error:

            self.finished.emit(
                f"Error: {error}"
            )


# --------------------------------------------------
# CHAT WINDOW
# --------------------------------------------------

class ChatWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowIcon(QIcon("kaido.png"))
        self.setWindowTitle("Kaido")
        self.resize(500, 650)

        # ------------------------------------------
        # MAIN LAYOUT
        # ------------------------------------------

        layout = QVBoxLayout()

        layout.setContentsMargins(
            15, 15, 15, 15
        )

        layout.setSpacing(12)

        # ------------------------------------------
        # WELCOME SECTION
        # ------------------------------------------

        welcome_layout = QHBoxLayout()

        welcome = QLabel("""
        <div>

            <div style="
                font-size: 26px;
                font-weight: bold;
            ">
                ☠️ Ahoy! I'm Kaido.
            </div>

            <div style="
                font-size: 16px;
                color: #aaaaaa;
                margin-top: 10px;
            ">
                Your AI companion, ready for whatever<br>
                you throw my way.
            </div>

            <div style="
                font-size: 15px;
                color: #dddddd;
                margin-top: 15px;
            ">
                Questions, code, ideas, problems —<br>
                bring them aboard.
            </div>

            <div style="
                font-size: 14px;
                color: #888888;
                margin-top: 15px;
            ">
                So, what are we tackling today?
            </div>

        </div>
        """)

        welcome.setWordWrap(True)

        welcome.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )

        # Logo

        logo = QLabel()

        logo.setPixmap(
            QIcon("kaido.png").pixmap(
                100,
                100
            )
        )

        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        welcome_layout.addWidget(
            welcome,
            1
        )

        welcome_layout.addWidget(
            logo
        )

        layout.addLayout(
            welcome_layout
        )

        # ------------------------------------------
        # CHAT SCROLL AREA
        # ------------------------------------------

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(True)

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #101114;
                width: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #303640;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container inside scroll area

        self.chat_container = QWidget()

        self.messages_layout = QVBoxLayout()

        self.messages_layout.setContentsMargins(
            8, 8, 8, 8
        )

        self.messages_layout.setSpacing(10)

        # Important: push messages toward top

        self.messages_layout.addStretch()

        self.chat_container.setLayout(
            self.messages_layout
        )

        self.scroll.setWidget(
            self.chat_container
        )

        layout.addWidget(
            self.scroll,
            1
        )

        # ------------------------------------------
        # INPUT AREA
        # ------------------------------------------

        input_layout = QHBoxLayout()

        self.input_box = QLineEdit()

        self.input_box.setPlaceholderText(
            "Ask Kaido..."
        )

        self.send_button = QPushButton("➤")

        self.send_button.setFixedSize(
            48,
            42
        )

        input_layout.addWidget(
            self.input_box,
            1
        )

        input_layout.addWidget(
            self.send_button
        )

        layout.addLayout(
            input_layout
        )

        self.setLayout(
            layout
        )

        # ------------------------------------------
        # EVENTS
        # ------------------------------------------

        self.send_button.clicked.connect(
            self.send_message
        )

        self.input_box.returnPressed.connect(
            self.send_message
        )

        # ------------------------------------------
        # STYLE
        # ------------------------------------------

        self.setStyleSheet("""
            QWidget {
                background: #010d30;
                color: #FCF1D0;
                font-family: Arial;
            }

            QLineEdit {
                background: #101933;
                color: white;

                border: 1px solid #292c35;
                border-radius: 18px;

                padding: 12px 16px;

                font-size: 15px;
            }

            QLineEdit:focus {
                border: 1px solid #465064;
            }

            QPushButton {
                background: #ffffff;
                color: #000000;

                border: none;
                border-radius: 14px;

                font-size: 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #dddddd;
            }

            QPushButton:disabled {
                background: #444444;
                color: #888888;
            }
        """)

    # ------------------------------------------------
    # ADD MESSAGE
    # ------------------------------------------------

    def add_message(
        self,
        message,
        is_user
    ):

        # Convert Markdown to HTML

        html = markdown.markdown(
            message,
            extensions=[
                "fenced_code",
                "tables"
            ]
        )

        # Message bubble

        bubble = QLabel()

        bubble.setText(
            html
        )

        bubble.setWordWrap(
            True
        )

        bubble.setTextFormat(
            Qt.TextFormat.RichText
        )

        bubble.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred
        )

        # Maximum bubble width

        bubble.setMaximumWidth(
            350
        )

        # ------------------------------------------
        # USER BUBBLE
        # ------------------------------------------

        if is_user:

            bubble.setStyleSheet("""
                QLabel {
                    background: #22396F;

                    color: white;

                    border-radius: 14px;

                    padding: 10px 14px;

                    font-size: 14px;
                }
            """)

        # ------------------------------------------
        # KAIDO BUBBLE
        # ------------------------------------------

        else:

            bubble.setStyleSheet("""
                QLabel {
                    background: #0D1C42;

                    color: white;

                    border-radius: 14px;

                    padding: 10px 14px;

                    font-size: 14px;
                }

                code {
                    background: #111318;
                }
            """)

        # ------------------------------------------
        # ROW
        # ------------------------------------------

        row = QHBoxLayout()

        row.setContentsMargins(
            5,
            0,
            5,
            0
        )

        if is_user:

            row.addStretch()

            row.addWidget(
                bubble
            )

        else:

            row.addWidget(
                bubble
            )

            row.addStretch()

        # Insert before final stretch

        self.messages_layout.insertLayout(
            self.messages_layout.count() - 1,
            row
        )

        QTimer.singleShot(
            50,
            self.scroll_to_bottom
        )

    # ------------------------------------------------
    # SEND MESSAGE
    # ------------------------------------------------
    def scroll_to_bottom(self):
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):

        message = (
            self.input_box
            .text()
            .strip()
        )

        if not message:
            return

        # Add user bubble

        self.add_message(
            message,
            True
        )

        self.input_box.clear()

        self.send_button.setEnabled(
            False
        )

        # Start AI worker

        self.worker = AIWorker(
            message
        )

        self.worker.finished.connect(
            self.receive_response
        )

        self.worker.start()

    # ------------------------------------------------
    # RECEIVE RESPONSE
    # ------------------------------------------------

    def receive_response(
        self,
        response
    ):

        # Add Kaido bubble

        self.add_message(
            response,
            False
        )

        self.send_button.setEnabled(
            True
        )

        self.input_box.setFocus()


# --------------------------------------------------
# FLOATING BUTTON
# --------------------------------------------------

class FloatingButton(QPushButton):

    def __init__(self, chat_window):
        super().__init__()

        self.chat_window = chat_window

        self.setIcon(QIcon("kaido.png"))
        self.setIconSize(QSize(55, 55))

        self.setFixedSize(65, 65)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setStyleSheet("""
            QPushButton {
                background: #011387;
                border: none;
                border-radius: 32px;
            }

            QPushButton:hover {
                background: #0d1c3d;
            }
        """)

        self.clicked.connect(self.toggle_chat)

        # Dragging variables
        self.dragging = False
        self.drag_position = None

        # Bottom-right starting position
        screen = QApplication.primaryScreen().availableGeometry()

        self.move(
            screen.right() - 85,
            screen.bottom() - 85
        )

    # ------------------------------------------
    # MOUSE PRESS
    # ------------------------------------------

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

            self.drag_start_position = (
                event.globalPosition().toPoint()
            )

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()


    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            current_position = (
                event.globalPosition().toPoint()
            )

            # Only consider it a drag after moving 5 pixels
            if (
                current_position - self.drag_start_position
            ).manhattanLength() > 5:

                self.dragging = True

                self.move(
                    current_position - self.drag_position
                )

            event.accept()


    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            # If we didn't drag, treat it as a click
            if not self.dragging:
                self.toggle_chat()

            self.dragging = False

            event.accept()    
    # ------------------------------------------
    # CLICK
    # ------------------------------------------

    def toggle_chat(self):

        if self.chat_window.isVisible():

            self.chat_window.hide()

        else:

            self.chat_window.show()
            self.chat_window.activateWindow()
            self.chat_window.raise_()


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = QApplication(
    sys.argv
)

app.setWindowIcon(
    QIcon("kaido.png")
)

chat_window = ChatWindow()

floating_button = FloatingButton(
    chat_window
)

floating_button.show()

sys.exit(
    app.exec()
)