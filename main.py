# pyright: strict

import os
from utils.utilities import *
from dotenv import load_dotenv
from controller import MainController
from datetime import datetime

if __name__ == "__main__":
    time_start = datetime.now()
    print(time_start)

    load_dotenv()
    
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if ORS_API_KEY is None:
        raise ValueError("API Key does not exist!")
    
    controller = MainController(ORS_API_KEY, time_start)
    controller.run()

    