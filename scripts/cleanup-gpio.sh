#!/bin/bash
# Cleanup GPIO pins that may be stuck in use

echo "GPIO Cleanup Script"
echo "==================="
echo ""

# Kill any Python processes that might be using GPIO
echo "Checking for running Python processes..."
PYTHON_PIDS=$(pgrep -f "python.*test-display\|python.*main.py\|python.*lumy")
if [ -n "$PYTHON_PIDS" ]; then
    echo "Found Python processes using GPIO:"
    ps -p $PYTHON_PIDS -o pid,cmd
    echo ""
    echo "Killing processes..."
    sudo kill -9 $PYTHON_PIDS 2>/dev/null || true
    sleep 1
    echo "✓ Processes killed"
else
    echo "No Python processes found"
fi

# Try to release GPIO using chip command if available
echo ""
echo "Releasing GPIO pins..."
if command -v gpioinfo &> /dev/null; then
    # Use modern GPIO tools if available
    for chip in /dev/gpiochip*; do
        if [ -e "$chip" ]; then
            sudo gpioset --mode=exit $(basename $chip) 17=0 2>/dev/null || true
        fi
    done
fi

echo "✓ GPIO cleanup complete"
echo ""
echo "You can now run:"
echo "  python3 scripts/test-display.py"
