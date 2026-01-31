#!/bin/sh
set -e

# Start Ollama server in background
ollama serve &
PID=$!

# Wait until server is ready (ollama list talks to the API)
until ollama list 2>/dev/null; do
  sleep 2
done

# Pull Gemma model for ml_worker
ollama pull gemma3:1b

# Pre-load model (warm up) so first ml_worker request is fast
curl -s http://localhost:11434/api/generate -d '{"model": "gemma3:1b", "prompt": ".", "stream": false}' > /dev/null || true

# Keep container running: wait for the server process
wait $PID
