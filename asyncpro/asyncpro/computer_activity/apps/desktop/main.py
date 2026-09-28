"""
Desktop Application Entrypoint.
Launches the local FastAPI server and embedded dashboard application.
"""
import sys
import webbrowser
import uvicorn


def launch_desktop():
    print("Launching AI Computer Activity Intelligence Platform Desktop Service...")
    port = 8000
    webbrowser.open(f"http://127.0.0.1:{port}")
    uvicorn.run("computer_activity.api.app:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    launch_desktop()
