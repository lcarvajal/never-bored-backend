#!/bin/sh

# Export all environment variables safely
eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

# Source the environment variables
. /etc/profile.d/env.sh

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000
