#!/bin/sh

# Export all environment variables safely
printenv | while IFS= read -r line; do
    key=$(echo "$line" | cut -d '=' -f 1)
    value=$(echo "$line" | cut -d '=' -f 2-)
    # Ensure the key is valid and the value is quoted properly
    if [ -n "$key" ] && [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
        echo "export $key=\"$value\"" >> /etc/profile.d/env.sh
    fi
done

# Source the environment variables
. /etc/profile.d/env.sh

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000
