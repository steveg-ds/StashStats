"""Playwright E2E test configuration and fixtures."""
import os
import time
import socket
import threading
import pytest
from playwright.sync_api import sync_playwright


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def browser_context():
    """Launch Chromium browser with configured context for the test session."""
    # Default HEADED=true for popup window
    is_headed = os.getenv("HEADED", "true").lower() == "true"
    if os.getenv("HEADLESS", "false").lower() == "true":
        is_headed = False

    slow_mo_env = int(os.getenv("SLOW_MO", "800"))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not is_headed, slow_mo=slow_mo_env)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="session")
def app_server_url():
    """Get the URL where the Dash app server runs, launching background server once for the session if needed."""
    if is_port_open('127.0.0.1', 8050):
        return 'http://127.0.0.1:8050'
    if is_port_open('127.0.0.1', 8099):
        return 'http://127.0.0.1:8099'
    
    # Launch in thread if local server is down
    from app import app
    server_thread = threading.Thread(target=lambda: app.run(host="127.0.0.1", port=8099, debug=False))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2)
    return 'http://127.0.0.1:8099'