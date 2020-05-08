#include <stdio.h>
#include <ctime>
#include <iostream>
#include <string>
#include <opencv2/opencv.hpp>
#include <raspicam/raspicam_cv.h>
#include <fstream>
using namespace std; 
using namespace cv;
int sharpness(Mat filtered,int *devR,int *gradient)
 {
  float sum_diff = 0, lastvalue = 0;
  double summation = 0;
  double NOPixels = 0;
  double Avg=10;
  double Rdev = 0;
  for (int y = 0; y < filtered.rows; y++) 
   {
    for (int x = 0; x < filtered.cols; x++) 
     {
      char pixel = filtered.at<char>(y, x);
      summation = summation + pixel;
      NOPixels++;
      sum_diff = sum_diff + abs(pixel - lastvalue);
      lastvalue = pixel;
      Rdev = Rdev + (filtered.at<char>(y, x) - Avg) * (filtered.at<char>(y, x) - Avg);
     }
    }
  Avg=summation/NOPixels;
  double dev = sqrt(Rdev / NOPixels);
  *devR=dev;
  *gradient=(sum_diff/1000);
  cout   << "DEV: " << dev <<  " gradient: " << sum_diff<< " "  <<  "\n"; 
  return 0;
 } 
int main ( int argc,char *argv[] ) 
 {
  ofstream myfile;
  myfile.open("data.txt");   
  myfile << "num RMS_canny gradient_canny\n"; 
  int x=0;
  Mat graph;
  graph.create(600,1000,CV_8UC3); 
  int number_of_picture=40;
  namedWindow("graph");
  resizeWindow("graph",300,300);//WINDOW_AUTOSIZE
  namedWindow("canny");resizeWindow("canny",300,300);//WINDOW_AUTOSIZE
  for(int j=0;j<number_of_picture;j++)    
   {    
    //-------------------- take picture--------------
    time_t timer_begin,timer_end;
    raspicam::RaspiCam_Cv Camera;
    cv::Mat image;
    int nCount=100;
    Camera.set( CV_CAP_PROP_FORMAT, CV_8UC3 );
    cout<<"Opening camera ..."<<endl;
    if(!Camera.open())
    time (&timer_begin);
    for(int i=0; i<nCount;i++)
     {
      Camera.grab();
      Camera.retrieve(image);
      if ( i%5==0 )  
       cout<<"\r captured "<<i<<" images"<<std::flush;
     }
    cout<<"Stop camera ..."<<endl;
    Camera.release();
    time (&timer_end);
    double secondsElapsed = difftime ( timer_end,timer_begin );
    cout<< secondsElapsed<<" seconds for "<< nCount<<"  frames : FPS = "<<  ( float ) ( ( float ) ( nCount ) /secondsElapsed ) <<endl;
    imshow("main",image);
    //-------------filter---------------------
    Mat canny;
    Canny(image,canny,20,60,3);
    imshow("canny",canny);
    //------------ Calculate sharpness ---------
    int RMS_canny,gradient_canny;
    sharpness(canny,&RMS_canny,&gradient_canny);
    myfile << j << " " << RMS_canny <<" "<<gradient_canny<<"\n";
    //------------Draw--------------------
	//------------move next z --------------------
    waitKey(10);
   }//for
  myfile.close();
  waitKey(0);
  return 0;
}//main
    
    
