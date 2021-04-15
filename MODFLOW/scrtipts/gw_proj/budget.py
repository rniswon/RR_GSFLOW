import os, sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import flopy
import h5py as h5


class Budget(object):
    def __init__(self, budget_files):
        self.budget_files = budget_files
        self.budget_components = {}

