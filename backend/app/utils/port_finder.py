"""
Port Finder Utility
Finds available ports and manages port configuration
"""

import socket
import json
import os
from pathlib import Path


def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available for use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_available_port(host: str = "127.0.0.1", start_port: int = 8000, max_attempts: int = 100) -> int:
    """
    Find an available port starting from start_port

    Args:
        host: Host to bind to
        start_port: Starting port number
        max_attempts: Maximum number of ports to try

    Returns:
        Available port number

    Raises:
        RuntimeError: If no available port found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port

    raise RuntimeError(f"No available port found between {start_port} and {start_port + max_attempts}")


def save_port_config(port: int, host: str = "127.0.0.1"):
    """
    Save port configuration to a JSON file for frontend to read

    Creates/updates backend/.port-config.json
    """
    config_file = Path(__file__).parent.parent.parent / ".port-config.json"

    config = {
        "host": host,
        "port": port,
        "api_url": f"http://{host}:{port}/api"
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Port configuration saved to {config_file}")
    return config_file


def update_frontend_env(port: int, host: str = "127.0.0.1"):
    """
    Update frontend .env file with new backend port

    Updates REACT_APP_API_URL in frontend/.env
    """
    frontend_dir = Path(__file__).parent.parent.parent.parent / "frontend"
    env_file = frontend_dir / ".env"

    if not env_file.exists():
        # Create from .env.example if it exists
        example_file = frontend_dir / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)

    # Read existing .env
    env_lines = []
    api_url_found = False

    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_API_URL='):
                    env_lines.append(f'REACT_APP_API_URL=http://{host}:{port}/api\n')
                    api_url_found = True
                else:
                    env_lines.append(line)

    # Add API URL if not found
    if not api_url_found:
        env_lines.append(f'\nREACT_APP_API_URL=http://{host}:{port}/api\n')

    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(env_lines)

    print(f"✓ Frontend .env updated with API URL: http://{host}:{port}/api")
    return env_file


def get_configured_port(host: str = "127.0.0.1", preferred_port: int = 8000) -> int:
    """
    Get configured port, finding an available one if the preferred port is occupied

    Args:
        host: Host to bind to
        preferred_port: Preferred port number

    Returns:
        Available port number (preferred port if available, otherwise next available)
    """
    if is_port_available(host, preferred_port):
        print(f"✓ Port {preferred_port} is available")
        return preferred_port

    print(f"⚠ Port {preferred_port} is already in use, finding alternative...")
    alternative_port = find_available_port(host, preferred_port + 1)
    print(f"✓ Found available port: {alternative_port}")

    # Save port config for frontend
    save_port_config(alternative_port, host)

    # Update frontend .env
    try:
        update_frontend_env(alternative_port, host)
    except Exception as e:
        print(f"⚠ Could not update frontend .env: {e}")
        print(f"  Please manually update REACT_APP_API_URL to: http://{host}:{alternative_port}/api")

    return alternative_port
