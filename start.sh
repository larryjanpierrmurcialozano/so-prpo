#!/usr/bin/env bash
# script helper para desarrollo local
export FLASK_APP=backend.app:create_app
export FLASK_ENV=development
flask run --host=0.0.0.0

