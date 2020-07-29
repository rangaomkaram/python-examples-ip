#####################################################################

# Example : display individual YCrCb channels from an video file
# specified on the command line (e.g. python FILE.py video_file) or from an
# attached web camera (with optional chroma subsampling as used in JPEG
# image compression)

# Author : Toby Breckon, toby.breckon@durham.ac.uk

# Copyright (c) 2020 Dept Computer Science, Durham University, UK
# License : LGPL - http://www.gnu.org/licenses/lgpl.html

#####################################################################

import cv2
import argparse
import sys
import numpy as np
import math

#####################################################################

keep_processing = True

# parse command line arguments for camera ID or video file

parser = argparse.ArgumentParser(
    description='Perform ' +
    sys.argv[0] +
    ' example operation on incoming camera/video image')
parser.add_argument(
    "-c",
    "--camera_to_use",
    type=int,
    help="specify camera to use",
    default=0)
parser.add_argument(
    "-r",
    "--rescale",
    type=float,
    help="rescale image by this factor",
    default=1.0)
parser.add_argument(
    'video_file',
    metavar='video_file',
    type=str,
    nargs='?',
    help='specify optional video file')
args = parser.parse_args()


perform_chroma_subsampling = False

#####################################################################

# define video capture object

cap = cv2.VideoCapture()

# define display window name

windowName = "Live Camera Input"  # window name
windowNameY = "Y Channel"  # window name
windowNameCr = "Cr Channel"  # window name
windowNameCb = "Cb Channel"  # window name

# if command line arguments are provided try to read video_file
# otherwise default to capture from attached H/W camera

if (((args.video_file) and (cap.open(str(args.video_file))))
        or (cap.open(args.camera_to_use))):

    # create window by name (note flags for resizable or not)

    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

    # usage

    print("USAGE: press 's' to subsample the chroma")

    while (keep_processing):

        # if video file or camera successfully open then read frame from video

        if (cap.isOpened):
            ret, frame = cap.read()

            # when we reach the end of the video (file) exit cleanly

            if (ret == 0):
                keep_processing = False
                continue

            # rescale if specified

            if (args.rescale != 1.0):
                frame = cv2.resize(
                    frame, (0, 0), fx=args.rescale, fy=args.rescale)

        # start a timer (to see how long processing and display takes)

        start_t = cv2.getTickCount()

        img_YCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        # subsample the chroma information in the same way as it is done in
        # JPEG

        if (perform_chroma_subsampling):

            # "Next, the chrominance channels Cr and Cb are subsampled.
            # The constant SSH defines the subsampling factor in horicontal
            # direction, SSV defines the vertical subsampling factor. Before
            # subsampling the chrominance channels are filtered using a (2x2)
            # box filter (=average filter). ..." Code from:
            # https://www.hdm-stuttgart.de/~maucher/Python/MMCodecs/html/jpegUpToQuant.html

            SSV = 2
            SSH = 2
            crf = cv2.boxFilter(img_YCrCb[:, :, 1], ddepth=-1, ksize=(2, 2))
            cbf = cv2.boxFilter(img_YCrCb[:, :, 2], ddepth=-1, ksize=(2, 2))
            crsub = crf[::SSV, ::SSH]
            cbsub = cbf[::SSV, ::SSH]

        # display images

        cv2.imshow(windowName, frame)

        # colour channels are YCrCb ordering in OpenCV

        cv2.imshow(windowNameY, img_YCrCb[:, :, 0])  # Y
        if (perform_chroma_subsampling):
            cv2.imshow(windowNameCr, crsub)  # Cr
            cv2.imshow(windowNameCb, cbsub)  # Cb
        else:
            cv2.imshow(windowNameCr, img_YCrCb[:, :, 1])  # Cr
            cv2.imshow(windowNameCb, img_YCrCb[:, :, 2])  # Cb

        # stop the timer and convert to ms. (to see how long processing and
        # display takes)

        stop_t = ((cv2.getTickCount() - start_t) /
                  cv2.getTickFrequency()) * 1000

        # start the event loop - essential

        # cv2.waitKey() is a keyboard binding function (argument is the time in milliseconds).
        # It waits for specified milliseconds for any keyboard event.
        # If you press any key in that time, the program continues.
        # If 0 is passed, it waits indefinitely for a key stroke.
        # (bitwise and with 0xFF to extract least significant byte of multi-byte response)
        # here we use a wait time in ms. that takes account of processing time
        # already used in the loop

        # wait 40ms or less depending on processing time taken (i.e. 1000ms /
        # 25 fps = 40 ms)

        key = cv2.waitKey(max(2, 40 - int(math.ceil(stop_t)))) & 0xFF

        # It can also be set to detect specific key strokes by recording which
        # key is pressed

        # e.g. if user presses "x" then exit

        if (key == ord('x')):
            keep_processing = False
        elif (key == ord('s')):
            perform_chroma_subsampling = not(perform_chroma_subsampling)

    # close all windows

    cv2.destroyAllWindows()

else:
    print("No video file specified or camera connected.")

#####################################################################