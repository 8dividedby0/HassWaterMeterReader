import cv2
import time
import paho.mqtt.client as mqtt
import json
# import the font used by the display
from displayfont import font

# import the perspective transform matrix
from cameraMath import M

# parse the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)

poolingRate = config["poolingRate"]
debug = config["debug"]

cameraURL = config["camera"]["url"]
contrast = config["camera"]["contrast"]
brightness = config["camera"]["brightness"]

mqttBroker = config["MQTT"]["broker"]
mqttPort = config["MQTT"]["port"]
mqttTopic = config["MQTT"]["topic"]

digit1CropX = config["digits"]["digit1CropX"]
digit1CropY = config["digits"]["digit1CropY"]
digit2CropX = config["digits"]["digit2CropX"]
digit2CropY = config["digits"]["digit2CropY"]

# setup the camera stream
cap = cv2.VideoCapture(cameraURL) # camera stream URL

# setup the MQTT client
client = mqtt.Client()
client.connect(mqttBroker, mqttPort, 60)

# setup runtime variables
last_time = time.time() # initialize the last time variable to the current time
last_read = None # initialize the last read variable to None

while True:
    ret, frame = cap.read() # read a frame from the video stream
    if not ret:
        print("Ret is false! Exiting...")
        break
    
    if poolingRate != 0: # if pooling rate is set, check if enough time has passed since the last frame
        if not time.time() - last_time >= poolingRate: # check if enough time has passed
            continue # if not, skip
        else:
            last_time = time.time() # continue and update the last time variable
    
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert image from bgr to grayscale
    image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness) # adjust contrast and brightness
    (thresh, image) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # apply binary thresholding (Otsu's method)

    output_width = 227  # width of the warped output image
    output_height = 140 # height of the warped output image
    image = cv2.warpPerspective(image, M, (output_width, output_height)) # warp it to fix perspective issues
    
    # crop the digits from the image
    digit1 = image[digit1CropY[0]:digit1CropY[1], digit1CropX[0]:digit1CropX[1]]
    digit2 = image[digit2CropY[0]:digit2CropY[1], digit2CropX[0]:digit2CropX[1]]

    if debug: # if debug mode is enabled, save the images for debugging purposes
        cv2.imwrite('images/frame.{}.jpg'.format(time.time()), frame)
        cv2.imwrite('images/image.{}.jpg'.format(time.time()), image)
        cv2.imwrite('images/digit1.{}.jpg'.format(time.time()), digit1)
        cv2.imwrite('images/digit2.{}.jpg'.format(time.time()), digit2)

    # resize the cropped digits to 5x7 pixels (the size of the display digits)
    digit1 = cv2.resize(digit1, (5, 7))
    digit2 = cv2.resize(digit2, (5, 7))

    # invert the cropped digits to match the font dictionary (white on black)
    digit1 = cv2.bitwise_not(digit1)
    digit2 = cv2.bitwise_not(digit2)
    
    # flatten the digit images to 1D arrays
    flattened_digit1 = digit1.flatten()
    flattened_digit2 = digit2.flatten()

    # convert the flattened digit images to binary tuples
    flattened_digit1 = tuple(1 if pixel > 0 else 0 for pixel in flattened_digit1)
    flattened_digit2 = tuple(1 if pixel > 0 else 0 for pixel in flattened_digit2)

    # now we compare the flattened digit images with the font dictionary
    digit1scores = {}
    digit2scores = {}
    for i in font: # generate scores for each digit in the font, higher score means better match
        digit1scores[i] = sum(1 if font[i][j] == flattened_digit1[j] else 0 for j in range(len(flattened_digit1)))
        digit2scores[i] = sum(1 if font[i][j] == flattened_digit2[j] else 0 for j in range(len(flattened_digit2)))

    # sort the scores in descending order
    digit1scores = sorted(digit1scores.items(), key=lambda x: x[1], reverse=True)
    digit2scores = sorted(digit2scores.items(), key=lambda x: x[1], reverse=True)    
    
    # get the digits with the highest score
    digit1 = digit1scores[0][0]
    digit2 = digit2scores[0][0]

    finalNumber = float(f"{digit1}.{digit2}")

    if debug: 
        print(f"Final number: {finalNumber}") # print the final number to the console for debugging

    if finalNumber != last_read: # check if the number is different from the last read number, if so we publish it
        last_read = finalNumber
        client.publish(mqttTopic, finalNumber)  # publish the final number to the MQTT topic
