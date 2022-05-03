#! /bin/bash

# Create Virtual Environment
virtualenv env --python=python3.9

# Activate Virtual Environment
source env/bin/activate

# Install dependencies
python3 -m pip install -r requirements.txt

# Init PostgreSQL DB
python3 -c "import database; database.activate()"

# Launch app
uvicorn main:app