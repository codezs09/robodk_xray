#!/usr/bin/env python3
"""
temporary usage. Generate a test example csv file with random duration in [ms] between 0 and 5000. 
The script is not supposed to use in the future. 
"""

import csv
import os 
import random

script_dir = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    example_csv_path = os.path.join(script_dir, "Example-XYZWPR-Duration.csv")
    print(f"Import and modify CSV file: {example_csv_path}")

    with open(example_csv_path, "r") as f:
        reader = csv.reader(f)
        data = list(reader)

        # replace the 7th column to the duration in [ms] generated randomly between 0 and 5000
        for i in range(len(data)):
            if len(data[i]) == 7:
                data[i][-1] = random.randint(0, 5000)
        
        with open(example_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print("Modified csv file saved.")