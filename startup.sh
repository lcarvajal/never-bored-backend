#!/bin/sh

apply_migrations() {
    echo "Applying database migrations..."
    if ! alembic upgrade head; then
        echo "Error applying migrations"
        exit 1
    fi
}

if [ "$ENV" = "dev" ]; then
    echo "Starting FastAPI in development mode with SSL..."
    SSL_KEYFILE="./certs/key.pem"
    SSL_CERTFILE="./certs/cert.pem"
    uvicorn app.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=$SSL_KEYFILE --ssl-certfile=$SSL_CERTFILE --log-config ./logging.conf
else
    # Export all environment variables safely for Azure
    eval $(printenv | sed -n "s/^\([^=]\+\)=\(.*\)$/export \1=\2/p" | sed 's/"/\\\"/g' | sed '/=/s//="/' | sed 's/$/"/' >> /etc/profile)

    # Set the default environment to production if not specified
    ENV=${ENV:-production}

    # Apply database migrations
    apply_migrations
    
    echo "Starting FastAPI in production mode..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-config ./logging.conf
fi
