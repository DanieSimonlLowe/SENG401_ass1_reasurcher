from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ['TOKEN'] # create a file called '.env' and put token there. Needs python-dotenv package

BASE_URL = "https://api.github.com/"

FILEPATH = 'holder'