# 2S Module pattern recognition 

A repository where we can gather our tools for pattern recognition in the 2S Module Assembly.
In images there is a number of pictures of dummy and glass sensors.

We can start by tuning the algorithms to smoothly detect these edges.
The edge_finder.py contains a function called edge_find that uses the Canny algorithm to do edge detection.

still_images.py runs this functions on still images, which we can use to optimize the algorithm on the sensor images.

real_time.py runs on a video feed, or on a video file.

It then has two methods for extracting the edge coordinates. One method relies on finding contours with OpenCV, the other fits a line using a hough transform.

# Dependencies
Python, OpenCV and NumPy
