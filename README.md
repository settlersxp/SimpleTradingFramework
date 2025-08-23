A framework to link Tradingview to MetaTrader5 as a PoC. Not really usable at the moment.


# Setup
On macOS/Linux:
`export FLASK_APP=run.py`

On Windows (Command Prompt):
`set FLASK_APP=run.py`

On Windows (PowerShell):
`$env:FLASK_APP = "run.py"`

# Run the app
`flask run` 

# Migrate the database
`flask db migrate`
`flask db upgrade`

# setup virtual environment
`python3 -m venv venv`
`source venv/bin/activate`

# install dependencies
`pip install -r requirements.txt`


# testing
`set FLASK_APP=run.py && set FLASK_END=testing && flask db upgrade`

# dev
`set FLASK_APP=run.py && set FLASK_END=development && flask db upgrade`

# prod
`set FLASK_APP=run.py && set FLASK_END=production && flask db upgrade`