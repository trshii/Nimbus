# pyright: strict

import os
from utils.utilities import *
from dotenv import load_dotenv
from controller import MainController

if __name__ == "__main__":
    load_dotenv()
    
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if ORS_API_KEY is None:
        raise ValueError("API Key does not exist!")
    
    controller = MainController(ORS_API_KEY)
    controller.get_route()