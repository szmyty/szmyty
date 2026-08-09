#!/usr/bin/env python3
"""
Audit MegaLinter configuration file for issues and recommendations.

This script validates the .megalinter.yml configuration file and provides
suggestions for improvements without failing the workflow.
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime, timezone


# Known valid MegaLinter configuration keys (v8)
# Reference: https://megalinter.io/latest/config-variables/
VALID_TOP_LEVEL_KEYS = {
    "ADDITIONAL_EXCLUDED_DIRECTORIES",
    "APPLY_FIXES",
    "CLEAR_REPORT_FOLDER",
    "CONFIG_PROPERTIES_TO_APPEND",
    "DEFAULT_BRANCH",
    "DEFAULT_WORKSPACE",
    "DISABLE",
    "DISABLE_ERRORS",
    "DISABLE_LINTERS",
    "DISABLE_ERRORS_LINTERS",
    "ENABLE",
    "ENABLE_LINTERS",
    "ENABLE_ERRORS_LINTERS",
    "ERROR_ON_MISSING_EXEC_BIT",
    "EXCLUDED_DIRECTORIES",
    "EXTENDS",
    "FAIL_IF_MISSING_LINTER_IN_FLAVOR",
    "FAIL_IF_UPDATED_SOURCES",
    "FILTER_REGEX_EXCLUDE",
    "FILTER_REGEX_INCLUDE",
    "FLAVOR_SUGGESTIONS",
    "FORMATTERS_DISABLE_ERRORS",
    "GITHUB_API_URL",
    "GITHUB_SERVER_URL",
    "GITHUB_TOKEN",
    "GITLAB_ACCESS_TOKEN_MEGALINTER",
    "GITLAB_CERTIFICATE_PATH",
    "GITLAB_CUSTOM_CERTIFICATE",
    "IGNORE_GENERATED_FILES",
    "IGNORE_GITIGNORED_FILES",
    "JAVASCRIPT_DEFAULT_STYLE",
    "KUBERNETES_HELM_DIRECTORY",
    "KUBERNETES_KUBECONFORM_DIRECTORY",
    "KUBERNETES_KUBESCAPE_DIRECTORY",
    "LINTER_RULES_PATH",
    "LOG_FILE",
    "LOG_LEVEL",
    "MARKDOWN_DEFAULT_STYLE",
    "PARALLEL",
    "PARALLEL_PROCESS_NUMBER",
    "PLUGINS",
    "POST_COMMANDS",
    "PRE_COMMANDS",
    "PRINT_ALPACA",
    "PRINT_ALL_FILES",
    "PYTHON_DEFAULT_STYLE",
    "REPORTERS_MARKDOWN_TYPE",
    "REPORT_OUTPUT_FOLDER",
    "SECURED_ENV_VARIABLES",
    "SHOW_ELAPSED_TIME",
    "SHOW_SKIPPED_LINTERS",
    "SKIP_CLI_LINT_MODES",
    "TYPESCRIPT_DEFAULT_STYLE",
    "VALIDATE_ALL_CODEBASE",
    # Reporter configs
    "AZURE_COMMENT_REPORTER",
    "BITBUCKET_COMMENT_REPORTER",
    "CONFIG_REPORTER",
    "CONFIG_REPORTER_SUB_FOLDER",
    "CONSOLE_REPORTER",
    "CONSOLE_REPORTER_SECTIONS",
    "EMAIL_REPORTER",
    "EMAIL_REPORTER_EMAIL",
    "EMAIL_REPORTER_SENDER",
    "EMAIL_REPORTER_SEND_SUCCESS",
    "EMAIL_REPORTER_SMTP_HOST",
    "EMAIL_REPORTER_SMTP_PORT",
    "EMAIL_REPORTER_SMTP_USERNAME",
    "FILEIO_REPORTER",
    "FILEIO_REPORTER_SEND_SUCCESS",
    "GITHUB_COMMENT_REPORTER",
    "GITHUB_STATUS_REPORTER",
    "GITLAB_COMMENT_REPORTER",
    "GITLAB_COMMENT_REPORTER_OVERWRITE_COMMENT",
    "JSON_REPORTER",
    "JSON_REPORTER_OUTPUT_DETAIL",
    "MARKDOWN_SUMMARY_REPORTER",
    "MARKDOWN_SUMMARY_REPORTER_FILE_NAME",
    "TAP_REPORTER",
    "TAP_REPORTER_SUB_FOLDER",
    "TEXT_REPORTER",
    "TEXT_REPORTER_SUB_FOLDER",
    "UPDATED_SOURCES_REPORTER",
    "UPDATED_SOURCES_REPORTER_DIR",
}

# Linter-specific config patterns (these are dynamic based on linter names)
LINTER_CONFIG_PATTERNS = [
    "_CONFIG_FILE",
    "_ARGUMENTS",
    "_DIRECTORY",
    "_FILTER_REGEX_INCLUDE",
    "_FILTER_REGEX_EXCLUDE",
    "_FILE_EXTENSIONS",
    "_FILE_NAMES_REGEX",
    "_PRE_COMMANDS",
    "_POST_COMMANDS",
    "_DISABLE_ERRORS",
    "_DISABLE_ERRORS_IF_LESS_THAN",
    "_CLI_LINT_MODE",
]


class MegaLinterConfigAuditor:
    """Auditor for MegaLinter configuration files."""

    def __init__(self, config_path: Path):
        """Initialize the auditor with a config file path."""
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
        self.info: List[str] = []

    def load_config(self) -> bool:
        """Load and parse the YAML configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            return True
        except FileNotFoundError:
            self.issues.append(f"Config file not found: {self.config_path}")
            return False
        except yaml.YAMLError as e:
            self.issues.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.issues.append(f"Error loading config: {e}")
            return False

    def check_empty_values(self) -> None:
        """Check for empty or null configuration values."""
        for key, value in self.config.items():
            if value is None:
                self.warnings.append(f"Key '{key}' has null value")
            elif isinstance(value, (list, dict, str)) and not value:
                self.warnings.append(f"Key '{key}' is empty")

    def check_unknown_keys(self) -> None:
        """Check for unknown configuration keys."""
        unknown_keys = []
        for key in self.config.keys():
            # Check if it's a valid top-level key
            if key in VALID_TOP_LEVEL_KEYS:
                continue

            # Check if it's a linter-specific config (matches pattern)
            is_linter_config = any(key.endswith(pattern) for pattern in LINTER_CONFIG_PATTERNS)
            if is_linter_config:
                continue

            unknown_keys.append(key)

        if unknown_keys:
            self.suggestions.append(
                f"Unknown config keys (may be valid linter configs): {', '.join(unknown_keys[:10])}"
            )
            if len(unknown_keys) > 10:
                self.suggestions.append(f"  ... and {len(unknown_keys) - 10} more")

    def check_disabled_linters(self) -> None:
        """Check for disabled linters and suggest reviewing them."""
        disabled = self.config.get("DISABLE_LINTERS", [])
        if disabled:
            self.info.append(f"Disabled linters ({len(disabled)}): {', '.join(disabled)}")
            self.suggestions.append(
                "Review disabled linters to ensure they're intentionally excluded"
            )

    def check_report_settings(self) -> None:
        """Check report-related settings for GitHub Actions compatibility."""
        apply_fixes = self.config.get("APPLY_FIXES")
        if apply_fixes is not None and apply_fixes != "none":
            self.warnings.append(
                f"APPLY_FIXES is set to '{apply_fixes}'. For report-only mode, should be 'none'"
            )

        disable_errors = self.config.get("DISABLE_ERRORS")
        if not disable_errors:
            self.suggestions.append(
                "DISABLE_ERRORS is false. Set to true for report-only mode in CI"
            )

        fail_if_updated = self.config.get("FAIL_IF_UPDATED_SOURCES")
        if fail_if_updated:
            self.warnings.append(
                "FAIL_IF_UPDATED_SOURCES is true. This may cause CI failures in report-only mode"
            )

    def check_parallel_settings(self) -> None:
        """Check parallel processing settings."""
        parallel = self.config.get("PARALLEL", True)
        if parallel:
            process_count = self.config.get("PARALLEL_PROCESS_NUMBER", 0)
            if process_count > 8:
                self.suggestions.append(
                    f"PARALLEL_PROCESS_NUMBER is {process_count}. "
                    "Consider reducing for GitHub Actions runners (recommended: 2-4)"
                )

    def check_excluded_directories(self) -> None:
        """Check excluded directories configuration."""
        excluded = self.config.get("EXCLUDED_DIRECTORIES", [])
        standard_exclusions = {
            "node_modules",
            ".git",
            "dist",
            "build",
            "venv",
            ".venv",
            "__pycache__",
        }

        missing_standard = standard_exclusions - set(excluded)
        if missing_standard:
            self.suggestions.append(
                f"Consider excluding common directories: {', '.join(missing_standard)}"
            )

    def check_github_integration(self) -> None:
        """Check GitHub-specific integration settings."""
        github_comment = self.config.get("GITHUB_COMMENT_REPORTER", False)
        github_status = self.config.get("GITHUB_STATUS_REPORTER", False)

        if github_comment or github_status:
            self.info.append("GitHub integration is enabled (comment/status reporters)")
            self.suggestions.append(
                "Ensure GITHUB_TOKEN is available in workflow for GitHub reporters"
            )

    def check_reporter_conflicts(self) -> None:
        """Check for potential reporter configuration conflicts."""
        email_enabled = self.config.get("EMAIL_REPORTER", False)
        if email_enabled:
            required_email_settings = [
                "EMAIL_REPORTER_EMAIL",
                "EMAIL_REPORTER_SMTP_HOST",
                "EMAIL_REPORTER_SMTP_PORT",
            ]
            missing = [key for key in required_email_settings if not self.config.get(key)]
            if missing:
                self.warnings.append(
                    f"EMAIL_REPORTER enabled but missing settings: {', '.join(missing)}"
                )

    def audit(self) -> bool:
        """Run all audit checks."""
        if not self.load_config():
            return False

        self.check_empty_values()
        self.check_unknown_keys()
        self.check_disabled_linters()
        self.check_report_settings()
        self.check_parallel_settings()
        self.check_excluded_directories()
        self.check_github_integration()
        self.check_reporter_conflicts()

        return True

    def generate_report(self) -> str:
        """Generate a formatted audit report."""
        lines = [
            "=" * 80,
            "MegaLinter Configuration Audit Report",
            "=" * 80,
            f"Config File: {self.config_path}",
            f"Audit Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
        ]

        if self.issues:
            lines.extend(["❌ ISSUES", "-" * 80])
            for issue in self.issues:
                lines.append(f"  • {issue}")
            lines.append("")

        if self.warnings:
            lines.extend(["⚠️  WARNINGS", "-" * 80])
            for warning in self.warnings:
                lines.append(f"  • {warning}")
            lines.append("")

        if self.suggestions:
            lines.extend(["💡 SUGGESTIONS", "-" * 80])
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")
            lines.append("")

        if self.info:
            lines.extend(["ℹ️  INFORMATION", "-" * 80])
            for info_item in self.info:
                lines.append(f"  • {info_item}")
            lines.append("")

        if not (self.issues or self.warnings or self.suggestions or self.info):
            lines.extend(
                [
                    "✅ No issues found!",
                    "",
                    "Your MegaLinter configuration looks good.",
                ]
            )

        lines.extend(
            [
                "=" * 80,
                "Summary",
                "=" * 80,
                f"Issues: {len(self.issues)}",
                f"Warnings: {len(self.warnings)}",
                f"Suggestions: {len(self.suggestions)}",
                f"Info Items: {len(self.info)}",
                "",
            ]
        )

        return "\n".join(lines)


def main() -> int:
    """Main entry point for the config auditor."""
    parser = argparse.ArgumentParser(
        description="Audit MegaLinter configuration file for issues and recommendations"
    )
    parser.add_argument("config_file", help="Path to .megalinter.yml configuration file")
    parser.add_argument("output_file", help="Path to write audit report")

    args = parser.parse_args()

    config_path = Path(args.config_file)
    output_path = Path(args.output_file)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Run audit
    auditor = MegaLinterConfigAuditor(config_path)
    success = auditor.audit()

    # Generate and save report
    report = auditor.generate_report()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Also print to stdout
    print(report)

    # Exit with 0 (success) even if issues found - this is report-only
    return 0


if __name__ == "__main__":
    sys.exit(main())
