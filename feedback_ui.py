# Interactive Feedback MCP UI
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import argparse
from typing import Optional, TypedDict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QPlainTextEdit, QGroupBox,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QSettings
from PySide6.QtGui import QTextCursor, QIcon, QKeyEvent, QPalette, QColor, QFont

class FeedbackResult(TypedDict):
    interactive_feedback: str

def get_dark_mode_palette(app: QApplication):
    darkPalette = app.palette()
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.PlaceholderText, QColor(127, 127, 127))
    return darkPalette

class FeedbackTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Connect text change signal to update window size
        self.textChanged.connect(self._on_text_changed)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Find the parent FeedbackUI instance and call submit
            parent = self.parent()
            while parent and not isinstance(parent, FeedbackUI):
                parent = parent.parent()
            if parent:
                parent._submit_feedback()
        else:
            super().keyPressEvent(event)
    
    def _on_text_changed(self):
        # Find the parent FeedbackUI instance and trigger resize
        parent = self.parent()
        while parent and not isinstance(parent, FeedbackUI):
            parent = parent.parent()
        if parent:
            parent._adjust_window_size()

class FeedbackUI(QMainWindow):
    def __init__(self, prompt: str, predefined_options: Optional[List[str]] = None, font_size: int = 12):
        super().__init__()
        self.prompt = prompt
        self.predefined_options = predefined_options or []
        self.font_size = font_size

        self.feedback_result = None
        
        self.setWindowTitle("Interactive Feedback MCP")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.settings = QSettings("InteractiveFeedbackMCP", "InteractiveFeedbackMCP")
        
        # Load general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Start with a smaller initial size
            initial_width, initial_height = 600, 300
            self.resize(initial_width, initial_height)
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - initial_width) // 2
            y = (screen.height() - initial_height) // 2
            self.move(x, y)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        self.settings.endGroup() # End "MainWindow_General" group

        self._create_ui()

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Set up font with configured size
        font = QFont()
        font.setPointSize(self.font_size)

        # Feedback section
        self.feedback_group = QGroupBox("")
        self.feedback_group.setFont(font)
        feedback_layout = QVBoxLayout(self.feedback_group)

        # Description label (from self.prompt) - Support multiline
        self.description_label = QLabel(self.prompt)
        self.description_label.setWordWrap(True)
        self.description_label.setFont(font)
        self.description_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        feedback_layout.addWidget(self.description_label)

        # Add predefined options if any
        self.option_checkboxes = []
        if self.predefined_options and len(self.predefined_options) > 0:
            options_frame = QFrame()
            options_layout = QVBoxLayout(options_frame)
            options_layout.setContentsMargins(0, 10, 0, 10)
            
            for option in self.predefined_options:
                checkbox = QCheckBox(option)
                checkbox.setFont(font)
                self.option_checkboxes.append(checkbox)
                options_layout.addWidget(checkbox)
            
            feedback_layout.addWidget(options_frame)
            
            # Add a separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            feedback_layout.addWidget(separator)

        # Free-form text feedback
        self.feedback_text = FeedbackTextEdit()
        self.feedback_text.setFont(font)
        font_metrics = self.feedback_text.fontMetrics()
        row_height = font_metrics.height()
        # Calculate initial height for 3 lines + some padding for margins
        padding = self.feedback_text.contentsMargins().top() + self.feedback_text.contentsMargins().bottom() + 5 # 5 is extra vertical padding
        self.initial_text_height = 3 * row_height + padding
        self.feedback_text.setMinimumHeight(self.initial_text_height)
        
        # Store font metrics for dynamic resizing
        self.row_height = row_height
        self.text_padding = padding

        self.feedback_text.setPlaceholderText("Enter your feedback here (Ctrl+Enter to submit)")
        submit_button = QPushButton("&Send Feedback")
        submit_button.setFont(font)
        submit_button.clicked.connect(self._submit_feedback)

        feedback_layout.addWidget(self.feedback_text)
        feedback_layout.addWidget(submit_button)

        # Note: minimum height will be dynamically adjusted

        # Add widgets
        layout.addWidget(self.feedback_group)

    def _adjust_window_size(self):
        """Dynamically adjust window size based on text content"""
        text_content = self.feedback_text.toPlainText()
        lines = text_content.split('\n')
        line_count = len(lines)
        
        # Calculate the width needed for the longest line
        font_metrics = self.feedback_text.fontMetrics()
        max_line_width = 0
        for line in lines:
            line_width = font_metrics.horizontalAdvance(line)
            max_line_width = max(max_line_width, line_width)
        
        # Calculate new text area height (minimum 3 lines, maximum 15 lines)
        min_lines = 3
        max_lines = 15
        actual_lines = max(min_lines, min(line_count + 1, max_lines))  # +1 for cursor line
        new_text_height = actual_lines * self.row_height + self.text_padding
        
        # Calculate new window width (minimum 600, maximum 1200)
        min_width = 600
        max_width = 1200
        content_width = max_line_width + 100  # Add padding for margins and scrollbar
        new_width = max(min_width, min(content_width, max_width))
        
        # Get current window size
        current_size = self.size()
        current_height = current_size.height()
        
        # Calculate height difference
        current_text_height = self.feedback_text.height()
        height_diff = new_text_height - current_text_height
        new_height = max(300, current_height + height_diff)  # Minimum height of 300
        
        # Update text area height
        self.feedback_text.setMinimumHeight(new_text_height)
        self.feedback_text.setMaximumHeight(new_text_height)
        
        # Resize window
        self.resize(new_width, new_height)

    def _submit_feedback(self):
        feedback_text = self.feedback_text.toPlainText().strip()
        selected_options = []
        
        # Get selected predefined options if any
        if self.option_checkboxes:
            for i, checkbox in enumerate(self.option_checkboxes):
                if checkbox.isChecked():
                    selected_options.append(self.predefined_options[i])
        
        # Combine selected options and feedback text
        final_feedback_parts = []
        
        # Add selected options
        if selected_options:
            final_feedback_parts.append("; ".join(selected_options))
        
        # Add user's text feedback
        if feedback_text:
            final_feedback_parts.append(feedback_text)
            
        # Join with a newline if both parts exist
        final_feedback = "\n\n".join(final_feedback_parts)
            
        self.feedback_result = FeedbackResult(
            interactive_feedback=final_feedback,
        )
        self.close()

    def closeEvent(self, event):
        # Save general UI settings for the main window (geometry, state)
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()

        super().closeEvent(event)

    def run(self) -> FeedbackResult:
        self.show()
        QApplication.instance().exec()

        if not self.feedback_result:
            return FeedbackResult(interactive_feedback="")

        return self.feedback_result

def feedback_ui(prompt: str, predefined_options: Optional[List[str]] = None, output_file: Optional[str] = None, font_size: int = 12) -> Optional[FeedbackResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
    ui = FeedbackUI(prompt, predefined_options, font_size)
    result = ui.run()

    if output_file and result:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # Save the result to the output file
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the feedback UI")
    parser.add_argument("--prompt", default="I implemented the changes you requested.", help="The prompt to show to the user")
    parser.add_argument("--predefined-options", default="", help="Pipe-separated list of predefined options (|||)")
    parser.add_argument("--output-file", help="Path to save the feedback result as JSON")
    parser.add_argument("--font-size", type=int, default=12, help="Font size for the UI (default: 12)")
    args = parser.parse_args()

    predefined_options = [opt for opt in args.predefined_options.split("|||") if opt] if args.predefined_options else None
    
    result = feedback_ui(args.prompt, predefined_options, args.output_file, args.font_size)
    if result:
        print(f"\nFeedback received:\n{result['interactive_feedback']}")
    sys.exit(0)
