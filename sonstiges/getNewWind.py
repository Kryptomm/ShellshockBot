from PIL import ImageGrab
from time import sleep
import cv2
import numpy as np
import csv
import os
import pygetwindow as gw
from pyautogui import click

WIND_FIELD = [946, 77, 973, 95]

def makeScreen():
    cap = ImageGrab.grab(bbox=(WIND_FIELD[0], WIND_FIELD[1], WIND_FIELD[2], WIND_FIELD[3]))

    # Convert PIL Image to OpenCV format (BGR)
    cap_np = cv2.cvtColor(np.array(cap), cv2.COLOR_RGB2BGR)

    # Convert image to grayscale
    gray_image = cv2.cvtColor(cap_np, cv2.COLOR_BGR2GRAY)

    # Flatten and normalize pixel values
    flattened_image = gray_image.flatten() / 255.0  # Flatten and normalize to [0, 1]

    return flattened_image

def saveToCSV(data, label):
    # Convert data to a NumPy array if it's not already
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    
    # Convert label to string if it's not already
    label = str(label)

    csv_filename = 'data/WindPixels.csv'

    # Check if the CSV file exists; create it if it doesn't
    if not os.path.isfile(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header row with feature names and label
            num_features = len(data)
            header = ['feature_' + str(i+1) for i in range(num_features)]
            header.insert(0, 'label')
            writer.writerow(header)

    # Check if label already exists in CSV
    with open(csv_filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        existing_labels = [row[0] for row in reader]
        needed = [str(i) for i in range(0,101)]
        print("Missing:", sorted([int(i) for i in list(set(needed) - set(existing_labels))]), len(set(needed) - set(existing_labels)))

    if label in existing_labels:
        print(f"Label '{label}' already exists in CSV. Skipping...")
        return

    # Append data and label to CSV file
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([label] + data.tolist())  # Convert numpy array to list for CSV writing

    print(f"Data with label '{label}' saved to image_data.csv")

def do_after():
    click(1230,1000)
    click(-800,1000)

if __name__ == "__main__":
    while True:
        for x in range(3,0,-1):
            print(x,"s")
            sleep(1)
        
        data = makeScreen()
        print("Taking Pic Finished")
        
        do_after()
        label = input("Enter label for the image: ").lower()
        click(-1040,1192)
        saveToCSV(data, label)
