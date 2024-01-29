# FriendTrader

## Description
The FriendTrader backend will index and server via REST endpoints transaction data from the FriendTech smart contracts on the Base Layer 2 Blockchain. The smart contract is located here https://basescan.org/address/0xcf205808ed36593aa40a44f10c7f7c2f67d4a4d4. Financial Candlestick data is provided via REST Endpoint to allow a user to make informed trades based upon the data stored. Upon lauching the friend_trader_ws.py script, the script will listen to the blockchain for trades made to the contract. It will then dispatch celery tasks to process and store the data.

## Technology Stack
- **Python**: 3.8
- **Django**: 4.2.4
- **Celery**: 5.2.7
- **Blockchain**: Base
- **Database**: PostgreSQL
- **Other Dependencies**: djangorestframework, tweepy, web3, websockets

## Installation
Navigate to project directory.
```
python -m venv venv
source ./ven/bin/activate
pip install -e .
```

### Setup
cp exampleenv.txt .env

Need a BLAST_WSS_API key in order to read from the blockchain

# Run Django server
python manage.py runserver

# In a separate terminal, run Celery worker
celery -A friend_trader_async worker --loglevel=info