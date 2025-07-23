import cv2
import numpy as np

# calculates the perspective transform matrix
src_pts = np.array([
    [261, 140],   # top-left
    [563, 137],   # top-right
    [676, 887],   # bottom-right
    [366, 893]    # bottom-left
], dtype=np.float32)

""" original unmodified source points
src_pts = np.array([
    [280, 178],   # top-left
    [585, 175],   # top-right
    [699, 927],   # bottom-right
    [391, 931]    # bottom-left
], dtype=np.float32)
"""
digit_width = 100  # width in pixels of one digit
digit_height = 140 # height in pixels of one digit

dst_pts = np.array([ # calculate destination points for the perspective transform
    [0, 0],
    [digit_width - 1, 0],
    [digit_width - 1, digit_height - 1],
    [0, digit_height - 1]
], dtype=np.float32)

M = cv2.getPerspectiveTransform(src_pts, dst_pts)
