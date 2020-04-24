# Metrology pattern recognition 

A repository where we can gather our tools for pattern recognition in the 2S Module Assembly.
In images there is a number of pictures of dummy and glass sensors.
We can start by tuning the algorithms to smoothly detect these edges.
In the edge_finder.py uses the Canny algorithm to do edge detection.
It then has two methods for extracting the edge coordinates. One method relies on finding contours with OpenCV, the other fits a line using a hough transform.

# Dependencies
Python, OpenCV and NumPy
