"""Environment/config loading shared by the agent modules."""

import logging
import os

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
