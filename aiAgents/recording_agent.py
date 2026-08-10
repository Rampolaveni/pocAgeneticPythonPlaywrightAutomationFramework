from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Final


class RecordingAgent:
    """
    Starts Playwright Codegen, saves the recorded flow and creates
    a run manifest for the planner and generator agents.
    """

    SUPPORTED_BROWSERS: Final[set[str]] = {
        "chromium",
        "firefox",
        "webkit",
    }

    def __init__(
        self,
        recording_name: str,
        base_url: str,
        browser: str = "chromium",
    ) -> None:
        self.project_root = Path(__file__).resolve().parent.parent

        self.recordings_directory = (
            self.project_root / "aiInputs" / "recordings"
        )
        self.runs_directory = (
            self.project_root / "aiInputs" / "runs"
        )

        self.recording_name = self._sanitize_name(recording_name)
        self.base_url = self._validate_url(base_url)
        self.browser = self._validate_browser(browser)

        self.run_id = f"{self.recording_name}"

        self.recording_file = (
            self.recordings_directory
            / f"{self.run_id}_recording.py"
        )

        self.manifest_file = (
            self.runs_directory / f"{self.run_id}.json"
        )

    def record(self) -> Path:
        """Launch Codegen and save the recorded Python flow."""

        self._create_directories()

        command = [
            sys.executable,
            "-m",
            "playwright",
            "codegen",
            "--target",
            "python-pytest",
            "--browser",
            self.browser,
            "--output",
            str(self.recording_file),
            self.base_url,
        ]

        print("\nStarting Playwright Codegen...")
        print(f"Run ID          : {self.run_id}")
        print(f"Application URL : {self.base_url}")
        print(f"Browser         : {self.browser}")
        print(f"Recording file  : {self.recording_file}")

        print("\nPerform the required test flow in the browser.")
        print("Close the browser and Playwright Inspector when finished.")

        try:
            completed_process = subprocess.run(
                command,
                cwd=self.project_root,
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                "Python or Playwright could not be started."
            ) from error
        except KeyboardInterrupt:
            print("\nRecording interrupted by the user.")
            self._create_manifest(status="interrupted")
            return self.recording_file

        if completed_process.returncode != 0:
            self._create_manifest(
                status="failed",
                error=(
                    "Playwright Codegen returned exit code "
                    f"{completed_process.returncode}."
                ),
            )

            raise RuntimeError(
                "Playwright Codegen failed with exit code "
                f"{completed_process.returncode}."
            )

        self._validate_recording_file()
        self._create_manifest(status="recorded")

        print("\nRecording completed successfully.")
        print(f"Recording saved : {self.recording_file}")
        print(f"Run manifest    : {self.manifest_file}")

        return self.recording_file

    def _create_directories(self) -> None:
        self.recordings_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.runs_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _validate_recording_file(self) -> None:
        if not self.recording_file.exists():
            raise RuntimeError(
                "Codegen closed, but the recording file was not created: "
                f"{self.recording_file}"
            )

        if self.recording_file.stat().st_size == 0:
            raise RuntimeError(
                f"The recording file is empty: {self.recording_file}"
            )

    def _create_manifest(
        self,
        status: str,
        error: str | None = None,
    ) -> None:
        """
        Store the exact recording path and future planner/generator
        output paths.
        """

        manifest = {
            "run_id": self.run_id,
            "flow_name": self.recording_name,
            "status": status,
            "created_at": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "application_url": self.base_url,
            "browser": self.browser,
            "recording_file": self._relative_path(
                self.recording_file
            ),
            "planner_prompt": (
                "aiInputs/prompts/recordedCodePlannerAgent.md"
            ),
            "generator_prompt": (
                "aiInputs/prompts/recordedCodeGeneratorAgent.md"
            ),
            "planner_output": (
                f"aiOutputs/plans/{self.run_id}_plan.md"
            ),
            "generator_output": (
                "aiOutputs/recommendations/"
                f"{self.run_id}_recommendations.md"
            ),
            "error": error,
        }

        self.manifest_file.write_text(
            json.dumps(manifest, indent=4),
            encoding="utf-8",
        )

    def _relative_path(self, path: Path) -> str:
        return path.relative_to(
            self.project_root
        ).as_posix()

    @staticmethod
    def _sanitize_name(value: str) -> str:
        sanitized_name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            value.strip(),
        ).strip("_").lower()

        if not sanitized_name:
            raise ValueError(
                "Recording name must contain letters or numbers."
            )

        return sanitized_name

    @staticmethod
    def _validate_url(value: str) -> str:
        url = value.strip()

        if not url.startswith(("http://", "https://")):
            raise ValueError(
                "Application URL must start with http:// or https://."
            )

        return url

    def _validate_browser(self, value: str) -> str:
        browser = value.strip().lower()

        if browser not in self.SUPPORTED_BROWSERS:
            supported = ", ".join(
                sorted(self.SUPPORTED_BROWSERS)
            )
            raise ValueError(
                f"Unsupported browser '{value}'. "
                f"Supported browsers: {supported}"
            )

        return browser