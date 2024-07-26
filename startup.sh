#!/bin/sh

# Export all environment variables safely
printenv | awk -F= '{ print "export " $1 "=\"" $2 "\"" }' > /etc/profile.d/env.sh

# Source the environment variables
. /etc/profile.d/env.sh

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8000
