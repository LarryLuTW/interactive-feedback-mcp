# Font Size Configuration

## Overview
The Interactive Feedback MCP now supports configurable font sizes for the popup window through CLI arguments.

## Implementation Details

### Server Side (`server.py`)
- Added `--font-size` CLI argument with default value of 12
- Global variable `FONT_SIZE` stores the font size configuration
- Modified `launch_feedback_ui()` to pass `--font-size` argument to the subprocess

### UI Side (`feedback_ui.py`)
- Added `--font-size` argument parser with default value of 12
- Modified `FeedbackUI` class constructor to accept `font_size` parameter
- Applied font size to all UI components:
  - Group box labels
  - Description labels
  - Checkbox options
  - Text edit areas
  - Submit buttons

## Usage

### Running the server with custom font size
```bash
python server.py --font-size 16
```

### Testing the UI directly with custom font size
```bash
python feedback_ui.py --prompt "Test message" --font-size 14
```

## Font Size Range
- Minimum recommended: 8pt
- Default: 12pt
- Maximum practical: 24pt (larger sizes may cause layout issues)

## Technical Notes
- Font size is applied using QFont.setPointSize()
- All UI components inherit the configured font size
- Height calculations for text areas are automatically adjusted based on font metrics 