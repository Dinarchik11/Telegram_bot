import dotenv

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

class Config:
    TOKEN = dotenv_values["TOKEN"]
    DB_PATH = dotenv_values["DB_PATH"]
