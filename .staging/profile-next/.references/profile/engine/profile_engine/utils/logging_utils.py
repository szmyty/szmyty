"""
Logging utilities for profile scripts.
Provides centralized logging functionality with rotation support.
"""

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Default configuration
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 5 * 1024 * 1024))  # 5MB
LOG_MAX_ROTATIONS = int(os.getenv("LOG_MAX_ROTATIONS", 3))


class WorkflowLogger:
    """
    Centralized logger for workflow scripts with rotation support.
    """
    
    def __init__(self, workflow_name: str, log_level: int = logging.INFO):
        """
        Initialize the workflow logger.
        
        Args:
            workflow_name: Name of the workflow (e.g., 'location', 'weather')
            log_level: Logging level (default: INFO)
        """
        self.workflow_name = workflow_name
        self.log_dir = LOG_DIR / workflow_name
        self.log_file = self.log_dir / f"{workflow_name}.log"
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(workflow_name)
        self.logger.setLevel(log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_MAX_ROTATIONS,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%SZ'
        )
        formatter.converter = lambda *args: datetime.now(timezone.utc).timetuple()
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logging initialized: {self.log_file}")
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def log_workflow_start(self, description: Optional[str] = None):
        """
        Log the start of a workflow.
        
        Args:
            description: Optional workflow description
        """
        separator = "=" * 60
        self.logger.info(separator)
        self.logger.info(f"Workflow: {self.workflow_name}")
        if description:
            self.logger.info(f"Description: {description}")
        self.logger.info(f"Started at: {datetime.now(timezone.utc).isoformat()}Z")
        self.logger.info(separator)
    
    def log_workflow_end(self, exit_code: int = 0):
        """
        Log the end of a workflow.
        
        Args:
            exit_code: Exit code (0 for success, non-zero for failure)
        """
        separator = "=" * 60
        self.logger.info(separator)
        if exit_code == 0:
            self.logger.info(f"Workflow: {self.workflow_name} - COMPLETED SUCCESSFULLY")
        else:
            self.logger.error(f"Workflow: {self.workflow_name} - FAILED (exit code: {exit_code})")
        self.logger.info(f"Ended at: {datetime.now(timezone.utc).isoformat()}Z")
        self.logger.info(separator)
    
    def log_command(self, command: str, output: Optional[str] = None, exit_code: int = 0):
        """
        Log command execution details.
        
        Args:
            command: Command that was executed
            output: Optional command output
            exit_code: Command exit code
        """
        self.logger.info(f"Executing: {command}")
        if exit_code == 0:
            self.logger.info(f"Command succeeded (exit code: {exit_code})")
        else:
            self.logger.error(f"Command failed (exit code: {exit_code})")
        
        if output:
            # Log first 500 characters of output to avoid huge log entries
            if len(output) > 500:
                self.logger.info(f"Output: {output[:500]}... (truncated)")
            else:
                self.logger.info(f"Output: {output}")


def get_logger(workflow_name: str, log_level: int = logging.INFO) -> WorkflowLogger:
    """
    Get a logger instance for a workflow.
    
    Args:
        workflow_name: Name of the workflow
        log_level: Logging level (default: INFO)
    
    Returns:
        WorkflowLogger instance
    """
    return WorkflowLogger(workflow_name, log_level)


# Convenience function for scripts that need a simple logger
def setup_logging(workflow_name: str) -> WorkflowLogger:
    """
    Set up logging for a script.
    
    Args:
        workflow_name: Name of the workflow
    
    Returns:
        WorkflowLogger instance
    """
    return get_logger(workflow_name)
