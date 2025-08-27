<p align="left">
<img width="600" alt="Pool Shot Demo Image 1" src="https://github.com/user-attachments/assets/2536375b-bea3-4a21-be91-11296d3f771d">
</p>

# Pool Shot Prediction

Pool shot prediction <a href="https://www.youtube.com/watch?v=LKSdxrvAYCc">program</a> that predicts the path and outcome (in or out) of 10 pool shots provided by CVZone. 

I used two libraries: OpenCV and NumPy. My process started with detecting the cue ball and colored balls using several different Hue/Saturation/Value (HSV) filters and contour detection. Only contours with a certain area and inside a certain boundary were marked as important. The location of the pockets and walls was marked with their coordinates. It was difficult to detect green balls, since they are the same color as the field and the shadows. Also, the positions of the pockets and walls shifted slightly after each shot, causing inaccuracies with the predictions. For these two issues, parameters were adjusted in order to achieve accurate results.

The impact point of the cue ball and the colored ball was calculated by finding a line that matches the initial motion of the cue ball (fraction of a second) and finding the location of a circle on the line that touches the colored ball. The path of the colored ball after collision was calculated in a similar way, but there were two possible outcomes: scored in a pocket or rebounded off a wall. For the first outcome, if the colored ball's path intersected with any of the 6 pockets, it was marked as "in". For the second outcome, if a point on the line of the colored ball's path intersected with the coordinates of a wall, a rebound path was calculated using the principle of reflected lines. Some balls did not exactly follow the reflected lines, so the exact reflection points were adjusted. Then, it was necessary to check if the rebounding ball would be in or out. This was done by extending the rebound line and redoing the same process as before.

## Results
Won 400+ votes for competition entry to CVZone, one of the most popular computer vision education platforms in the world.

Competition Entry: https://www.youtube.com/watch?v=LKSdxrvAYCc
