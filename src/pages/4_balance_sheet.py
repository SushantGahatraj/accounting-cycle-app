mport os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#Path helper
APP_PATH = os.path.dirname(os.path.abspath(__file__))
def get_data_path(filename: str) -> str:
    '''Returns the path to a data file given its filename.'''
    return os.path.join(APP_PATH, "..", "data", filename)
