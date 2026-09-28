"""
CLI Application Entrypoint for AI Computer Activity Intelligence Platform.
"""
import argparse
import sys
import uvicorn
from computer_activity.collectors.common.synthetic import SyntheticEventGenerator
from computer_activity.storage.sqlite.database import Database
from computer_activity.storage.migrations.runner import MigrationRunner


def main():
    parser = argparse.ArgumentParser(description="AI Computer Activity Intelligence Platform CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Serve API
    serve_parser = subparsers.add_parser("serve", help="Start local FastAPI intelligence server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number")

    # Replay scenario
    replay_parser = subparsers.add_parser("replay", help="Run synthetic scenario replay")
    replay_parser.add_argument("--scenario", default="cpp_debugging_loop", choices=["cpp_debugging_loop", "context_switching"])

    # Migrate DB
    subparsers.add_parser("migrate", help="Run database schema migrations")

    args = parser.parse_args()

    if args.command == "serve":
        print(f"Starting Local Activity Intelligence API at http://{args.host}:{args.port}")
        uvicorn.run("computer_activity.api.app:app", host=args.host, port=args.port, reload=False)
    elif args.command == "replay":
        print(f"Executing synthetic scenario replay: {args.scenario}...")
        if args.scenario == "context_switching":
            events = SyntheticEventGenerator.generate_context_switching_scenario()
        else:
            events = SyntheticEventGenerator.generate_cpp_debugging_scenario()
        print(f"Successfully generated {len(events)} synthetic canonical events.")
    elif args.command == "migrate":
        print("Running database migrations...")
        db = Database("computer_activity.db")
        runner = MigrationRunner(db)
        runner.run_migrations()
        print("Migrations complete.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
