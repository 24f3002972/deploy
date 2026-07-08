import os
from typing import List

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="12-Factor Config Precedence Service")

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows the grader/browser to access the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load .env
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Default configuration (Lowest precedence)
# --------------------------------------------------
DEFAULT_CONFIG = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def to_bool(value):
    """Convert various truthy values to bool."""
    return str(value).strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def coerce_types(config):
    """Convert values to required types."""
    if "port" in config:
        config["port"] = int(config["port"])

    if "workers" in config:
        config["workers"] = int(config["workers"])

    if "debug" in config:
        config["debug"] = to_bool(config["debug"])

    if "log_level" in config:
        config["log_level"] = str(config["log_level"])

    if "api_key" in config:
        config["api_key"] = str(config["api_key"])

    return config


# --------------------------------------------------
# Read YAML configuration
# --------------------------------------------------
def load_yaml():
    filename = "config.development.yaml"

    if not os.path.exists(filename):
        return {}

    with open(filename, "r") as f:
        data = yaml.safe_load(f)

    return data or {}


# --------------------------------------------------
# Read .env configuration
# Alias:
# NUM_WORKERS -> workers
# --------------------------------------------------
def load_dotenv_config():
    config = {}

    num_workers = os.getenv("NUM_WORKERS")
    if num_workers is not None:
        config["workers"] = num_workers

    return config


# --------------------------------------------------
# Read APP_* environment variables
# --------------------------------------------------
def load_os_config():
    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    config = {}

    for env_name, key in mapping.items():
        value = os.getenv(env_name)
        if value is not None:
            config[key] = value

    return config


# --------------------------------------------------
# Build effective configuration
# --------------------------------------------------
def build_config(cli_overrides):
    # Lowest precedence
    config = DEFAULT_CONFIG.copy()

    # YAML
    config.update(load_yaml())

    # .env
    config.update(load_dotenv_config())

    # APP_* environment variables
    config.update(load_os_config())

    # CLI overrides (Highest precedence)
    for item in cli_overrides:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)
        config[key] = value

    # Convert values to required types
    config = coerce_types(config)

    # Mask secret
    config["api_key"] = "****"

    return config


# --------------------------------------------------
# Endpoint
# --------------------------------------------------
@app.get("/effective-config")
def effective_config(
    set: List[str] = Query(default=[])
):
    return build_config(set)


# --------------------------------------------------
# Optional root endpoint
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "FastAPI Config Precedence Service",
        "endpoint": "/effective-config",
    }


# --------------------------------------------------
# Local development
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
