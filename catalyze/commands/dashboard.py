from __future__ import absolute_import

import webbrowser

from catalyze import cli, config

@cli.command("dashboard")
def dashboard():
    """Open the Catalyze dashboard in your browser"""
    webbrowser.open(config.dashboard_url)
