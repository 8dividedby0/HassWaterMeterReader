# HassWaterMeterReader
My digital water reader script for home assistant.

This script extracts pixels from a display, compares them against a font, and then uploads the number to an mqtt broker.

## config.json

debug           | saves processed images to a folder and prints recognized values to console
poolingRate     | the amount of time (in seconds) between checks, set to 0 to disable
MQTT:
    broker      | the ip address to the broker
    port        | the port to the broker
    topic       | the topic to send messages to
CAMERA:    
    url         | the url of the camera stream
    contrast    | the contrast to adjust the stream to
    brightness  | the brightness to adjust the stream to
DIGITS:
    digit1CropX | the x crop of the first digit
    digit2CropX | the x crop of the second digit
    digit1CropY | the y crop of the first digit
    digit2CropY | the y crop of the second digit
