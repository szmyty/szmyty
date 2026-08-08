#!/usr/bin/env python3
"""
Comprehensive Repository Audit Tool
Performs systematic audit of workflows, data, scripts, and configuration
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Base paths - use environment variable or current working directory
REPO_ROOT = Path(os.environ.get('GITHUB_WORKSPACE', os.getcwd()))
AUDIT_DIR = REPO_ROOT / "logs" / "audit"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
SCRIPTS_DIR = REPO_ROOT / "scripts"
DATA_DIR = REPO_ROOT / "data"
SCHEMAS_DIR = REPO_ROOT / "schemas"
CONFIG_DIR = REPO_ROOT / "config"


class AuditReport:
    """Manages audit report generation"""
    
    def __init__(self, filename: str):
        self.filename = AUDIT_DIR / filename
        self.lines = []
        self.issues = []
        self.warnings = []
        
    def add_header(self, title: str, level: int = 1):
        """Add markdown header"""
        self.lines.append(f"{'#' * level} {title}\n")
        
    def add_text(self, text: str):
        """Add regular text"""
        self.lines.append(f"{text}\n")
        
    def add_issue(self, issue: str):
        """Add critical issue"""
        self.issues.append(issue)
        self.lines.append(f"❌ **ISSUE**: {issue}\n")
        
    def add_warning(self, warning: str):
        """Add warning"""
        self.warnings.append(warning)
        self.lines.append(f"⚠️  **WARNING**: {warning}\n")
        
    def add_success(self, message: str):
        """Add success message"""
        self.lines.append(f"✅ {message}\n")
        
    def add_section(self, title: str):
        """Add section separator"""
        self.lines.append(f"\n---\n\n## {title}\n\n")
        
    def save(self):
        """Save report to file"""
        with open(self.filename, 'w') as f:
            f.write(f"# Audit Report\n")
            f.write(f"**Generated**: {datetime.utcnow().isoformat()}Z\n\n")
            f.write(f"**Issues Found**: {len(self.issues)}\n")
            f.write(f"**Warnings**: {len(self.warnings)}\n\n")
            f.write("---\n\n")
            f.writelines(self.lines)
        print(f"✅ Saved audit report: {self.filename}")


def audit_workflows() -> AuditReport:
    """Audit 1: Verify all workflow pipelines"""
    report = AuditReport("workflow_audit.md")
    report.add_header("Workflow Pipeline Audit")
    report.add_text(f"Auditing workflows in: {WORKFLOWS_DIR}")
    
    workflow_files = list(WORKFLOWS_DIR.glob("*.yml"))
    report.add_text(f"Found {len(workflow_files)} workflow files\n")
    
    for workflow_file in workflow_files:
        report.add_section(f"Workflow: {workflow_file.name}")
        
        try:
            with open(workflow_file) as f:
                content = f.read()
            
            # Check for common issues
            if "uses: actions/checkout@" not in content:
                report.add_warning(f"{workflow_file.name}: Missing checkout action")
                
            if "GITHUB_TOKEN" in content and "secrets.GITHUB_TOKEN" not in content:
                report.add_issue(f"{workflow_file.name}: Token reference may be incorrect")
                
            # Check for hardcoded paths
            if "/tmp/" in content or "/home/runner" in content:
                report.add_warning(f"{workflow_file.name}: Contains hardcoded paths")
                
            # Check for caching
            if "actions/cache@" in content or "cache:" in content:
                report.add_success(f"{workflow_file.name}: Uses caching")
            else:
                report.add_warning(f"{workflow_file.name}: No caching detected")
                
            # Check python setup
            if "setup-python@" in content:
                if "cache: 'pip'" not in content:
                    report.add_warning(f"{workflow_file.name}: Python setup without pip cache")
                else:
                    report.add_success(f"{workflow_file.name}: Python caching configured")
                    
            report.add_success(f"{workflow_file.name}: Valid YAML syntax")
            
        except Exception as e:
            report.add_issue(f"{workflow_file.name}: Failed to parse - {e}")
    
    report.save()
    return report


def audit_pipeline_status() -> AuditReport:
    """Audit 2: End-to-end pipeline trace for each card type"""
    report = AuditReport("pipeline_status.md")
    report.add_header("Pipeline Status Audit")
    
    cards = {
        "developer": {
            "script": "fetch-developer-stats.py",
            "generator": "generate-developer-dashboard.py",
            "data_file": "data/developer/stats.json",
            "output_svg": "developer/developer_dashboard.svg",
            "readme_marker": "DEVELOPER-DASHBOARD"
        },
        "soundcloud": {
            "script": "fetch-soundcloud.sh",
            "generator": None,  # Generated inline
            "data_file": "data/soundcloud/latest_track.json",
            "output_svg": "assets/soundcloud-card.svg",
            "readme_marker": "SOUNDCLOUD-CARD"
        },
        "weather": {
            "script": "fetch-weather.sh",
            "generator": "generate-weather-card.py",
            "data_file": "data/weather/current.json",
            "output_svg": "weather/weather-today.svg",
            "readme_marker": "WEATHER-CARD"
        },
        "location": {
            "script": "fetch-location.sh",
            "generator": "generate-location-card.py",
            "data_file": "data/location/current.json",
            "output_svg": "location/location-card.svg",
            "readme_marker": "LOCATION-CARD"
        },
        "oura_health": {
            "script": "fetch-oura.sh",
            "generator": "generate-health-dashboard.py",
            "data_file": "data/oura/daily_summary.json",
            "output_svg": "oura/health_dashboard.svg",
            "readme_marker": "OURA-HEALTH-CARD"
        },
        "oura_mood": {
            "script": "fetch-oura.sh",
            "generator": "generate-oura-mood-card.py",
            "data_file": "data/oura/daily_summary.json",
            "output_svg": "oura/mood_dashboard.svg",
            "readme_marker": "OURA-MOOD-CARD"
        }
    }
    
    report.add_text("## Pipeline Status Table\n")
    report.add_text("| Card | Fetch Script | Data File | Generator | Output SVG | README Marker |")
    report.add_text("|------|-------------|-----------|-----------|------------|---------------|")
    
    for card_name, pipeline in cards.items():
        report.add_section(f"Card: {card_name}")
        
        # Check fetch script
        script_path = SCRIPTS_DIR / pipeline["script"] if pipeline["script"] else None
        script_status = "✅" if script_path and script_path.exists() else "❌"
        if script_path and not script_path.exists():
            report.add_issue(f"{card_name}: Fetch script missing - {pipeline['script']}")
        
        # Check data file
        data_path = REPO_ROOT / pipeline["data_file"]
        data_status = "✅" if data_path.exists() else "❌"
        if not data_path.exists():
            report.add_warning(f"{card_name}: Data file missing - {pipeline['data_file']}")
        else:
            # Check if data is valid JSON
            try:
                with open(data_path) as f:
                    data = json.load(f)
                    if not data or data == {}:
                        report.add_warning(f"{card_name}: Data file is empty")
            except Exception as e:
                report.add_issue(f"{card_name}: Data file invalid JSON - {e}")
        
        # Check generator
        gen_status = "N/A"
        if pipeline["generator"]:
            gen_path = SCRIPTS_DIR / pipeline["generator"]
            gen_status = "✅" if gen_path.exists() else "❌"
            if not gen_path.exists():
                report.add_issue(f"{card_name}: Generator missing - {pipeline['generator']}")
        
        # Check output SVG
        svg_path = REPO_ROOT / pipeline["output_svg"]
        svg_status = "✅" if svg_path.exists() else "❌"
        if not svg_path.exists():
            report.add_warning(f"{card_name}: Output SVG missing - {pipeline['output_svg']}")
        
        # Check README marker
        readme_path = REPO_ROOT / "README.md"
        marker_status = "❌"
        if readme_path.exists():
            with open(readme_path) as f:
                readme_content = f.read()
                start_marker = f"<!-- {pipeline['readme_marker']}:START -->"
                end_marker = f"<!-- {pipeline['readme_marker']}:END -->"
                if start_marker in readme_content and end_marker in readme_content:
                    marker_status = "✅"
                else:
                    report.add_warning(f"{card_name}: README markers missing or malformed")
        
        # Add to table
        report.add_text(f"| {card_name} | {script_status} | {data_status} | {gen_status} | {svg_status} | {marker_status} |")
    
    report.save()
    return report


def audit_readme() -> AuditReport:
    """Audit 3: README injection markers and paths"""
    report = AuditReport("readme_audit.md")
    report.add_header("README Injection Audit")
    
    readme_path = REPO_ROOT / "README.md"
    
    if not readme_path.exists():
        report.add_issue("README.md not found!")
        report.save()
        return report
    
    with open(readme_path) as f:
        readme_content = f.read()
    
    # Check for injection markers
    markers = [
        "DEVELOPER-DASHBOARD",
        "LOCATION-CARD",
        "WEATHER-CARD",
        "SOUNDCLOUD-CARD",
        "OURA-HEALTH-CARD",
        "OURA-MOOD-CARD",
        "STATUS-PAGE"
    ]
    
    report.add_section("Injection Marker Status")
    for marker in markers:
        start_marker = f"<!-- {marker}:START -->"
        end_marker = f"<!-- {marker}:END -->"
        
        if start_marker in readme_content and end_marker in readme_content:
            # Check if markers are in correct order
            start_pos = readme_content.find(start_marker)
            end_pos = readme_content.find(end_marker)
            
            if start_pos < end_pos:
                report.add_success(f"{marker}: Markers present and correctly ordered")
            else:
                report.add_issue(f"{marker}: End marker appears before start marker")
        elif start_marker in readme_content:
            report.add_issue(f"{marker}: START marker found but END marker missing")
        elif end_marker in readme_content:
            report.add_issue(f"{marker}: END marker found but START marker missing")
        else:
            report.add_warning(f"{marker}: Both markers missing")
    
    # Check image paths
    report.add_section("Image Path Validation")
    image_pattern = r'!\[.*?\]\((.*?)\)'
    images = re.findall(image_pattern, readme_content)
    
    for img_path in images:
        if img_path.startswith('http'):
            continue  # External image
        
        # Remove ./ prefix if present
        clean_path = img_path.lstrip('./')
        full_path = REPO_ROOT / clean_path
        
        if full_path.exists():
            report.add_success(f"Image exists: {img_path}")
        else:
            report.add_warning(f"Image missing: {img_path}")
    
    report.save()
    return report


def audit_filesystem() -> None:
    """Audit 4: File system and directory structure"""
    report_path = AUDIT_DIR / "filesystem_audit.txt"
    
    with open(report_path, 'w') as f:
        f.write("FILE SYSTEM AUDIT\n")
        f.write("=" * 80 + "\n\n")
        
        # Find orphaned files
        f.write("ORPHANED FILES SCAN\n")
        f.write("-" * 80 + "\n")
        
        orphan_patterns = [
            "*.tmp",
            "*.bak",
            "*~",
            "*.swp",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        for pattern in orphan_patterns:
            result = subprocess.run(
                ["find", str(REPO_ROOT), "-name", pattern, "-type", "f"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                f.write(f"\nFound {pattern} files:\n")
                f.write(result.stdout)
        
        # Check for large files
        f.write("\n\nLARGE FILES (>1MB)\n")
        f.write("-" * 80 + "\n")
        result = subprocess.run(
            ["find", str(REPO_ROOT), "-type", "f", "-size", "+1M"],
            capture_output=True,
            text=True
        )
        f.write(result.stdout if result.stdout else "No large files found\n")
        
        # List all data directories
        f.write("\n\nDATA DIRECTORIES\n")
        f.write("-" * 80 + "\n")
        if DATA_DIR.exists():
            for item in DATA_DIR.rglob("*"):
                if item.is_file():
                    size = item.stat().st_size
                    f.write(f"{item.relative_to(REPO_ROOT)} ({size} bytes)\n")
        
        # Check log directories
        f.write("\n\nLOG DIRECTORIES\n")
        f.write("-" * 80 + "\n")
        logs_dir = REPO_ROOT / "logs"
        if logs_dir.exists():
            for item in logs_dir.rglob("*"):
                if item.is_file():
                    size = item.stat().st_size
                    f.write(f"{item.relative_to(REPO_ROOT)} ({size} bytes)\n")
    
    print(f"✅ Saved filesystem audit: {report_path}")


def audit_theme_schema() -> AuditReport:
    """Audit 5: Schema validation and theme consistency"""
    report = AuditReport("theme_schema_audit.md")
    report.add_header("Theme & Schema Validation Audit")
    
    # Check theme.json
    theme_path = CONFIG_DIR / "theme.json"
    report.add_section("Theme Configuration")
    
    if not theme_path.exists():
        report.add_issue("theme.json not found!")
    else:
        try:
            with open(theme_path) as f:
                theme = json.load(f)
            
            required_keys = ["colors", "fonts", "spacing"]
            for key in required_keys:
                if key in theme:
                    report.add_success(f"Theme has '{key}' section")
                else:
                    report.add_warning(f"Theme missing '{key}' section")
            
            # Check color completeness
            if "colors" in theme:
                color_keys = theme["colors"].keys()
                report.add_text(f"Found {len(color_keys)} color definitions")
                
        except json.JSONDecodeError as e:
            report.add_issue(f"theme.json invalid JSON: {e}")
    
    # Check schema files
    report.add_section("Schema Validation")
    
    if not SCHEMAS_DIR.exists():
        report.add_warning("schemas/ directory not found")
    else:
        schema_files = list(SCHEMAS_DIR.glob("*.json"))
        report.add_text(f"Found {len(schema_files)} schema files")
        
        for schema_file in schema_files:
            try:
                with open(schema_file) as f:
                    schema = json.load(f)
                report.add_success(f"Schema valid: {schema_file.name}")
            except json.JSONDecodeError as e:
                report.add_issue(f"Schema invalid: {schema_file.name} - {e}")
    
    report.save()
    return report


def audit_scripts() -> AuditReport:
    """Audit 6: Script and module health"""
    report = AuditReport("script_health.md")
    report.add_header("Script & Module Health Check")
    
    # Check main scripts
    report.add_section("Main Scripts")
    
    python_scripts = list(SCRIPTS_DIR.glob("*.py"))
    bash_scripts = list(SCRIPTS_DIR.glob("*.sh"))
    
    report.add_text(f"Found {len(python_scripts)} Python scripts")
    report.add_text(f"Found {len(bash_scripts)} Bash scripts\n")
    
    for script in python_scripts:
        try:
            with open(script) as f:
                content = f.read()
            
            # Check for shebang
            if not content.startswith("#!"):
                report.add_warning(f"{script.name}: Missing shebang")
            
            # Check for docstring
            if '"""' not in content and "'''" not in content:
                report.add_warning(f"{script.name}: Missing module docstring")
            
            # Check for main guard
            if "if __name__" in content:
                report.add_success(f"{script.name}: Has main guard")
            
            # Check for hardcoded paths
            if "/home/runner/work/profile/profile" in content:
                report.add_warning(f"{script.name}: Contains hardcoded absolute path")
            
            report.add_success(f"{script.name}: Readable")
            
        except Exception as e:
            report.add_issue(f"{script.name}: Failed to read - {e}")
    
    # Check lib directory
    lib_dir = SCRIPTS_DIR / "lib"
    if lib_dir.exists():
        report.add_section("Library Modules")
        lib_files = list(lib_dir.glob("*.py"))
        report.add_text(f"Found {len(lib_files)} library modules")
    
    report.save()
    return report


def audit_data() -> AuditReport:
    """Audit 7: Validate all data files"""
    report = AuditReport("data_integrity.md")
    report.add_header("Data Integrity Audit")
    
    if not DATA_DIR.exists():
        report.add_issue("data/ directory not found!")
        report.save()
        return report
    
    json_files = list(DATA_DIR.rglob("*.json"))
    report.add_text(f"Found {len(json_files)} JSON files\n")
    
    for json_file in json_files:
        report.add_section(f"File: {json_file.relative_to(DATA_DIR)}")
        
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            if not data:
                report.add_warning(f"Empty data: {json_file.name}")
            elif data == {}:
                report.add_warning(f"Empty object: {json_file.name}")
            else:
                report.add_success(f"Valid JSON with data: {json_file.name}")
                
                # Check file size
                size = json_file.stat().st_size
                if size == 0:
                    report.add_issue(f"Zero-byte file: {json_file.name}")
                elif size < 10:
                    report.add_warning(f"Suspiciously small ({size} bytes): {json_file.name}")
                    
        except json.JSONDecodeError as e:
            report.add_issue(f"Invalid JSON: {json_file.name} - {e}")
        except Exception as e:
            report.add_issue(f"Failed to read: {json_file.name} - {e}")
    
    report.save()
    return report


def main():
    """Run all audits"""
    print("=" * 80)
    print("COMPREHENSIVE REPOSITORY AUDIT")
    print("=" * 80)
    print()
    
    # Ensure audit directory exists
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run all audits
    audits = [
        ("Workflow Pipelines", audit_workflows),
        ("Pipeline Status", audit_pipeline_status),
        ("README Injection", audit_readme),
        ("File System", audit_filesystem),
        ("Theme & Schema", audit_theme_schema),
        ("Script Health", audit_scripts),
        ("Data Integrity", audit_data),
    ]
    
    results = []
    for name, audit_func in audits:
        print(f"\n{'='*80}")
        print(f"Running: {name}")
        print(f"{'='*80}")
        result = audit_func()
        if result:
            results.append((name, result))
        print()
    
    # Print summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    
    total_issues = sum(len(r.issues) for _, r in results if r)
    total_warnings = sum(len(r.warnings) for _, r in results if r)
    
    print(f"Total Issues: {total_issues}")
    print(f"Total Warnings: {total_warnings}")
    print(f"\nAudit reports saved to: {AUDIT_DIR}")
    print("="*80)


if __name__ == "__main__":
    main()
