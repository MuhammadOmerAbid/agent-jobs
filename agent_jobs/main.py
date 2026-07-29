import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent_jobs", description="Agent 3 - Remote Job Hunter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="Create your profile (optionally parsed from a CV)")
    setup_parser.add_argument("--cv", default=None, help="Path to a CV/resume file (PDF or text)")

    subparsers.add_parser("run", help="Fetch + score jobs once, right now")
    subparsers.add_parser("schedule", help="Run once, then repeat daily on a schedule")

    cover_parser = subparsers.add_parser("cover", help="Draft a cover note for a saved job (deferred feature)")
    cover_parser.add_argument("--job-id", required=True)

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "setup":
        from agent_jobs.cli.setup_cmd import setup
        setup(args.cv)
    elif args.command == "run":
        from agent_jobs.cli.run_cmd import run, show_top
        run()
        show_top()
    elif args.command == "schedule":
        from agent_jobs.cli.schedule_cmd import schedule
        schedule()
    elif args.command == "cover":
        from agent_jobs.cli.cover_cmd import cover
        cover(args.job_id)


if __name__ == "__main__":
    sys.exit(main())
