from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aiAgents.recording_agent import RecordingAgent


DEFAULT_URL = "https://tutorialsninja.com/demo/"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Record any browser flow using Playwright Codegen "
            "and prepare it for the planner and generator agents."
        )
    )

    parser.add_argument(
        "--name",
        required=True,
        help=(
            "Descriptive flow name, such as valid_login, "
            "product_search or customer_registration."
        ),
    )

    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"Starting application URL. Default: {DEFAULT_URL}",
    )

    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser used for recording. Default: chromium",
    )

    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()

    try:
        recording_agent = RecordingAgent(
            recording_name=arguments.name,
            base_url=arguments.url,
            browser=arguments.browser,
        )

        saved_recording = recording_agent.record()

        print("\nThe recording is ready for analysis.")
        print(f"Recorded flow: {saved_recording}")
        print(f"Run ID       : {recording_agent.run_id}")

        return 0

    except (ValueError, RuntimeError) as error:
        print(f"\nRecording failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())