#!/bin/bash

PROJECT_NAME="Dash-DWBRA's Container"

# Sets script to fail if any command fails.
set -e

run_app() {
	python etl.py
}

print_usage() {
echo "
$PROJECT_NAME

Usage:	$0 COMMAND

Options:
  help		        Print this help
  run			Run Dash server
"
}

case "$1" in
    help)
        print_usage
        ;;
    run)
      	shift 1
        run_app
        ;;
    *)
        exec "$@"
esac
