#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get directory paths
SCRIPT_DIR=$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
PYTHON_DIR="$(dirname "$SCRIPT_DIR")/python"
VENV_DIR=${PYTHON_DIR}/.venv
# echo "SCRIPT_DIR=${SCRIPT_DIR}"
# echo "PYTHON_DIR=${PYTHON_DIR}"
# echo "VENV_DIR=${VENV_DIR}"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to create and activate virtual environment
setup_venv() {
    print_message $YELLOW "Creating virtual environment in ${VENV_DIR}..."
    python3.13 -m venv ${VENV_DIR}

    # Activate virtual environment
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        source ${VENV_DIR}/bin/activate
    else
        source ${VENV_DIR}/Scripts/activate
    fi

    print_message $GREEN "Virtual environment activated!"
}

# Function to install dependencies
install_deps() {
    print_message $YELLOW "Installing dependencies from ${PYTHON_DIR}/requirements.txt..."
    pip install --upgrade pip
    pip install -r ${PYTHON_DIR}/requirements.txt
    print_message $GREEN "Dependencies installed successfully!"
}

# Function to clean everything and start fresh
clean_setup() {
    print_message $YELLOW "Removing existing virtual environment..."
    deactivate 2>/dev/null || true
    rm -rf ${VENV_DIR}
    setup_venv
    install_deps
}

# Main script
case "$1" in
    "clean")
        clean_setup
        ;;
    "install")
        if [ ! -d "${VENV_DIR}" ]; then
            setup_venv
        else
            if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
                source ${VENV_DIR}/bin/activate
            else
                source ${VENV_DIR}/Scripts/activate
            fi
        fi
        install_deps
        ;;
    *)
        print_message $RED "Usage: ./setup.sh [clean|install]"
        print_message $YELLOW "  clean   - Remove existing venv and create fresh setup"
        print_message $YELLOW "  install - Install or update dependencies in existing venv"
        exit 1
        ;;
esac
