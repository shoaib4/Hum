#!/bin/bash
# Build script for Hum executable on Linux/macOS

echo ""
echo "=========================================="
echo "        Building Hum Executable"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please run this from the project root."
    exit 1
fi

# Install/upgrade build dependencies
echo "📦 Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

# Install UPX if available (optional, for compression)
if command -v apt-get &> /dev/null; then
    echo "📦 Installing UPX (optional compression)..."
    sudo apt-get update && sudo apt-get install -y upx-ucl
elif command -v brew &> /dev/null; then
    echo "📦 Installing UPX (optional compression)..."
    brew install upx
fi

# Run the build script
echo "🔨 Building executable..."
python3 build.py

# Check if build succeeded
if [ -f "dist/Hum" ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo ""
    echo "Generated files:"
    echo "📁 dist/Hum - Main executable"
    echo "📁 dist/Hum-Portable/ - Portable package"
    echo ""

    # Make executable
    chmod +x dist/Hum

    # Show file size
    if command -v du &> /dev/null; then
        SIZE=$(du -h dist/Hum | cut -f1)
        echo "📊 Executable size: $SIZE"
    fi

    echo ""
    echo "You can now run: ./dist/Hum"
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    echo ""
    exit 1
fi