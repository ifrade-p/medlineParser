from asyncio.windows_events import NULL
import json
import sys
import os
import json
import re
from datetime import datetime
import time
import collections
import csv
import matplotlib.pyplot as plt
import pickle

with open(os.path.join("medline\\totals","medlinemesh_male_100_totals_years.json"), "r", encoding="utf8") as file2:
    lst = []
    for line in file2:
       lst.append(line.strip())
print(lst)