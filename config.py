import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

"""
    This will contain global variables that need to be shared from all files
"""
bio_temp = """في مثل هذا اليوم عام {0} ولد {1}، {2}"""
