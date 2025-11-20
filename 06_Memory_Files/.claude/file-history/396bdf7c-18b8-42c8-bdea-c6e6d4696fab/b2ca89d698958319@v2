#!/bin/bash
# Build all custom AVR provider Docker images

set -e

echo "🔨 Building custom AVR provider images..."
echo ""

# Build Groq LLM Provider
echo "Building avr-llm-groq..."
cd avr-llm-groq
docker build -t avr-llm-groq:latest .
echo "✅ avr-llm-groq built"
echo ""

# Build Cerebras LLM Provider
echo "Building avr-llm-cerebras..."
cd ../avr-llm-cerebras
docker build -t avr-llm-cerebras:latest .
echo "✅ avr-llm-cerebras built"
echo ""

# Build Edge TTS Provider
echo "Building avr-tts-edge..."
cd ../avr-tts-edge
docker build -t avr-tts-edge:latest .
echo "✅ avr-tts-edge built"
echo ""

cd ..

echo "🎉 All images built successfully!"
echo ""
echo "Available images:"
docker images | grep "avr-llm-groq\|avr-llm-cerebras\|avr-tts-edge"
echo ""
echo "Next steps:"
echo "1. Update providers in AVR dashboard to use these images:"
echo "   - avr-llm-groq:latest"
echo "   - avr-llm-cerebras:latest"
echo "   - avr-tts-edge:latest"
echo ""
echo "2. Or run: ./update-providers.sh to do it automatically"
