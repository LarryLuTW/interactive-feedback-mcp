# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import tempfile
import subprocess
import argparse

from typing import Annotated, Dict

from fastmcp import FastMCP
from pydantic import Field

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

# Global variable to store font size from CLI args
FONT_SIZE = 14  # Default font size

def launch_feedback_ui() -> dict[str, str]:
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to feedback_ui.py relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")

        # Run feedback_ui.py as a separate process
        # NOTE: There appears to be a bug in uv, so we need
        # to pass a bunch of special flags to make this work
        args = [
            sys.executable,
            "-u",
            feedback_ui_path,
            "--prompt", "",
            "--output-file", output_file,
            "--predefined-options", "",
            "--font-size", str(FONT_SIZE)
        ]
        result = subprocess.run(
            args,
            check=False,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        if result.returncode != 0:
            raise Exception(f"Failed to launch feedback UI: {result.returncode}")

        # Read the result from the temporary file
        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

@mcp.tool()
def interactive_feedback() -> Dict[str, str]:
    """Request interactive feedback from the user"""
    result = launch_feedback_ui()
    
    # Check if user requested git commit
    if result.get('git_commit', False):
        # Add instruction for git commit to the response
        git_instruction = "\n\n[AUTO COMMIT REQUESTED] Create concise git commit message and commit changes"
        result['interactive_feedback'] = result.get('interactive_feedback', '') + git_instruction
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Feedback MCP Server")
    parser.add_argument("--font-size", type=int, default=14, 
                       help="Font size for the feedback UI (default: 14)")
    args = parser.parse_args()
    
    # Update global font size from CLI args
    FONT_SIZE = args.font_size
    
    mcp.run(transport="stdio")
