# Booking.com Automation Scenarios

This repository contains an automated test suite written in Python using Playwright and Pytest for Booking.com based on 4 specific scenarios.

## Prerequisites
- Python 3.8+
- pip (Python package installer)

## Setup Instructions

1. **Extract the ZIP file** (if you haven't already).
2. **Open a terminal/command prompt** and navigate to the extracted folder.
3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Running the Tests

To run the automated scenarios in headless mode (default):
```bash
python -m pytest tests/test_scenarios.py -v
```

If you wish to view the browser executing the actions (headed mode), run:
```bash
python -m pytest tests/test_scenarios.py -v --headed
```

To slow down the test execution so you can visually follow the steps, use the `--slowmo` flag (time is in milliseconds):
```bash
python -m pytest tests/test_scenarios.py -v --headed --slowmo 1000
```
