# pyright: strict

import os
from utils.utilities import *
from dotenv import load_dotenv
from model import MainModel
from datetime import datetime
from view_tmnl import ViewTmnl
from controller import MainController

if __name__ == "__main__":
    time_start = datetime.now()
    # print(time_start)

    load_dotenv()
    
    ORS_API_KEY = os.getenv("ORS_API_KEY")
    if ORS_API_KEY is None:
        raise ValueError("API Key does not exist!")
    
    m = MainModel(ORS_API_KEY, time_start)
    v = ViewTmnl()
    c = MainController(m, v)
    
    c.run()

    