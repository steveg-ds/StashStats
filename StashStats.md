# StashStats

StashStats is a Dash-based web application to search and manage yarn data using the Ravelry API.

## Features
- **Yarn Search**: Query Ravelry's database to find yarns matching text input.
- **Detailed Specifications**: Displays product parameters including Yarn Name, Company Name, Weight (grams), Yardage, Discontinued status, and Machine Washability.
- **Colorways List**: Displays colorway names as tags/badges.
- **Add to Stash Form**: Allows users to quickly add a searched yarn to their Ravelry stash by configuring:
  - Skeins (float)
  - Colorway selector/text
  - Dye lot
  - Stash location
  - Custom notes

## Architecture
- **`app.py`**: Dash application entry point defining layouts and core callbacks (searching and adding yarn to stash).
- **`stashies/`**: Main package containing the controller, model, API client, and layout components.
  - **`app_controller.py`**: Intermediary controller coordinating search API calls and layout formatting.
  - **`model.py`**: Data Layer handling calls to Ravelry's `/yarns/search.json`, `/yarns/{id}.json`, and `/people/{username}/stash/create.json` endpoints.
  - **`base_req.py`**: Raw HTTP requests client wrapping HTTP Basic authentication and logging.
  - **`components/`**: Layout modules for the header, search filters, and search results view.
  - **`dataclasses/`**: Pydantic schemas validating API objects and POST requests payload structure.

## Setup and Running

1. **Virtual Environment**:
   Ensure dependencies are installed:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install dash dash-bootstrap-components pydantic pydantic-settings requests python-dotenv playwright pytest pytest-playwright
   ```
2. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   API_USERNAME=your_ravelry_api_username
   API_KEY=your_ravelry_api_key
   USERNAME=your_ravelry_username
   ```
3. **Start the Application**:
   ```bash
   .venv/bin/python app.py
   ```

## Automated Testing
Automated E2E integration tests are written in Playwright to simulate browser interactions. The tests mock the Ravelry API responses to prevent HTTP 403 authorization and rate-limit issues.

Run E2E test suite:
```bash
PYTHONPATH=. .venv/bin/pytest tests/test_e2e.py -v
```
