import cv2
from threading import Thread

class VideoFeedHandler(object):
    def __init__(self, video_file_name, src, processing_function):
        # Create a VideoCapture object
        self.frame = 0
        self.processed_frame = 0
        self.processed_objects = 0
        self.frame_name = 'cam_output'+str(src)
        self.processing_function = processing_function
        self.video_file = video_file_name
        self.video_file_name = video_file_name + '.avi'
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,2560);
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,2560);

        # Default resolutions of the frame are obtained (system dependent)
        #self.frame_width = int(self.capture.get(3))
        #print(self.frame_width)
        #self.frame_height = int(self.capture.get(4))
        #print(self.frame_height)
        self.frame_width = 1024
        print(self.frame_width)
        self.frame_height = 1024
        print(self.frame_height) 
        # Set up codec and output video settings
        #self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        #self.output_video = cv2.VideoWriter(self.video_file_name, self.codec, 30, (self.frame_width, self.frame_height))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        # Start another thread to show/save frames
        self.start_recording()
        print('initialized {}'.format(self.video_file))

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()


    def show_frame(self):
        # Display frames in main program
        if self.status:
            cv2.namedWindow(self.frame_name,cv2.WINDOW_NORMAL)
            cv2.imshow(self.frame_name, self.frame)
            cv2.resizeWindow(self.frame_name, self.frame_width,self.frame_height)
            
        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def show_processed_frame(self):
        # Display frames in main program
        if True:
            processed_frame, lines_img, _, _, _, distances = self.processing_function(self.frame)
            cv2.namedWindow("processed_frame",cv2.WINDOW_NORMAL)
            cv2.imshow("processed_frame", lines_img)
            cv2.resizeWindow("processed_frame", self.frame_width,self.frame_height)
            self.processed_objects = distances
            
    def save_frame(self):
        # Save obtained frame into video output file
        self.output_video.write(self.frame)

    def start_recording(self):
        # Create another thread to show/save frames
        def start_recording_thread():
            while True:
                try:
                    self.show_frame()
                    self.show_processed_frame()
                    #self.save_frame()
                except AttributeError:
                    pass
        self.recording_thread = Thread(target=start_recording_thread, args=())
        self.recording_thread.daemon = True
        self.recording_thread.start()
