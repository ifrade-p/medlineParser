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


with open("countries_males.txt", "r", encoding="utf8") as file2:
    male = file2.read()
# Read data from file 2
with open('countries_females.txt', "r", encoding="utf8") as file3:
    female = file3.read()

pairs1 = [list(map(str, pair.strip('][').strip('\"\"').split(','))) for pair in male.split('][')]
years1, totals1 = zip(*sorted(pairs1))

# Extract paired values from file 2
pairs2 = [list(map(str, pair.strip('][').strip('\"\"').split(','))) for pair in female.split('][')]
years2, totals2 = zip(*sorted(pairs2))

# Create bar chart
plt.bar(years2, totals2, label='female')
plt.bar(years1, totals1, label='male')
# Set labels and title
plt.xlabel('Country')
plt.ylabel('Total')
plt.title('Comparison of articles tagged "male" and "female"')
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
with open('countries_male_sorted_values.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Country', 'Total'])
    writer.writerows(zip(years1, totals1))
with open('countries_female_sorted_values.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Country', 'Total'])
    writer.writerows(zip(years2, totals2))