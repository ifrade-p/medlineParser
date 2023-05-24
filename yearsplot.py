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


with open("years_male.txt", "r", encoding="utf8") as file2:
    male = file2.read()
# Read data from file 2
with open('years_female.txt', "r", encoding="utf8") as file3:
    female = file3.read()

pairs1 = [list(map(int, pair.strip('][').split(','))) for pair in male.split('][')]
years1, totals1 = zip(*sorted(pairs1))

# Extract paired values from file 2
pairs2 = [list(map(int, pair.strip('][').split(','))) for pair in female.split('][')]
years2, totals2 = zip(*sorted(pairs2))

# Create bar chart
plt.bar(years1, totals1, label='male')
plt.bar(years2, totals2, label='female')

# Set labels and title
plt.xlabel('Year')
plt.ylabel('Total')
plt.title('Comparison of articles tagged "male" and "female"')

min_year =(min(min(years1), min(years2)))
max_year =(max(max(years1), max(years2)))
plt.xlim(min_year, max_year)
# Add legend
plt.legend()

# Show the chart
plt.show()

for test in years1:
    if test not in years2:
        print(test, "male")
for test in years2:
    if test not in years1:
        print(test, "female")
    
# Write sorted values to CSV file
with open('male1_sorted_values.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Year', 'Total'])
    writer.writerows(zip(years1, totals1))
with open('female1_sorted_values.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Year', 'Total'])
    writer.writerows(zip(years2, totals2))