# Development & Testing Guide

## Running Tests

Run the test suite using pytest:

```bash
$env:Path = "C:\Users\Aaditya\.local\bin;$env:Path"
.venv\Scripts\python.exe -m pytest computer_activity/tests
```

## Running Synthetic Scenarios

```bash
.venv\Scripts\python.exe -m computer_activity.apps.cli.main replay --scenario cpp_debugging_loop
.venv\Scripts\python.exe -m computer_activity.apps.cli.main replay --scenario context_switching
```

## Running API & Dashboard

```bash
.venv\Scripts\python.exe -m computer_activity.apps.cli.main serve
```
Then visit `http://127.0.0.1:8000` in your browser.
