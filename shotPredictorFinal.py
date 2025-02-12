#Author: Rhushil Vasavada
#Pool Shot Prediction
#Description: This computer vision algorithm won 3rd place in votes in Murtaza Hassan's CVZone competition 
#View entry here: https://www.computervision.zone/pool-shot-predictor/?contest=video-detail&video_id=104532
#Used OpenCV, HSV filtering, contour detection, and linear algebra to predict and trace the path of 10 pool shots 
#fed via video footage.

import numpy as np
import cv2

#store video containing 10 pool shots
cap = cv2.VideoCapture('videos/Shot-Predictor-Video.mp4')
width = int(cap.get(3))
height = int(cap.get(4))

#to be used to store processed footage with predicted shots
capProcessed = cv2.VideoWriter('ProcessedPool/processedShotsVideo.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))

#below are all variables to store important details about coordinate locations, RGB colors, and shot outcomes
pockets = [[194, 163], [906, 128], [1655, 170], [1617, 780], [904, 830], [270, 770]]

pocketColors = [[[0, 179, 0, 118, 54, 200], "pocket"]]

colorArray =
    [
        [[38, 78, 1, 65, 146, 241], "a"],
        [[92, 179, 195, 255, 4, 255], "b"],
        [[6, 51, 116, 255, 137, 255], "c"],
        [[40, 72, 179, 206, 51, 82], "d"],
        [[67.0, 79.0, 189.585, 201.585, 84.015, 96.015], "e"]
    ]

count = 0
lineColor = (235, 0, 0)
collideColor = (255, 217, 4)
impactColor = (255, 217, 4)

collideColor = lineColor
impactColor = lineColor

inColor = (10, 240, 10)
outColor = (0, 69, 255)

lineWidth = 13
circleWidth = 30

numDetections = 0
change = 50
cueBallPts = []
coloredBallPts = []
collisionPt = []
collided = False
touchingWall = False
wallPoint = []
outcome = ""
color = []
extraCenters = []

#define function to detect key elements of a given frame read from the video
def detectObjects(image):
    #to be used to keep track of shot changes
    global change
    global extraCenters

    #convert frame to HSV color format (gives us more valuable data for computer vision tasks)
    imgHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #iterate through all the colors we want to filter
    for range in colorArray:
        h_min, h_max, s_min, s_max, v_min, v_max = range[0][0], range[0][1], range[0][2], range[0][3], range[0][4], range[0][5]

        #create a low and high range of HSV values
        lowRange = np.array([h_min, s_min, v_min])
        upRange = np.array([h_max, s_max, v_max])
        
        #values in between this range will be detected via a mask
        mask = cv2.inRange(imgHSV, lowRange, upRange)
        #blur mask to remove extraneous noise
        mask = cv2.GaussianBlur(mask, (3, 3), 3)

        #find contours in filtered frame
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #iterate through each contour found
        for cnt in contours:
            #make a bounding rectangle around the countour to analyze the size
            (x, y, w, h) = cv2.boundingRect(cnt)

            #if the contour is within the range of the table, we want to analyze it further
            if 200 < y < 760 and 270 < x < 1660:
                #create a circular encolusre around the contour and save the center and radius
                (a, b), radius = cv2.minEnclosingCircle(cnt)
                a, b = int(a), int(b)
                center = (a, b)
                radius = int(radius)

                #specific case, when we want to shift the center due to alterations in camera footage
                if range[1] == "d":
                    center = (a - 20, b + 5)

                #if radius is between this range and the width of the bounding rectangle is above 30,
                #we know the contour is either a pool ball or part of the cue
                if 22.5 < radius < 30 and w > 30:

                    #to account for variations in camera footage
                    if range[1] == "c":
                        change = 35

                    #check if the contour falls within a certain color range (determining cue ball vs pool ball)
                    if colorArray.index(range) == 0:

                        #if we haven't found the cue yet, this contour must be it; save its location and radius
                        if len(cueBallPts) == 0:
                            cueBallPts.append([center, radius])

                        #otherwise, if the cue ball has been found, we have drawn a contour that is slightly after 
                        #the first sighting of the cue ball - add this contour to be used later on in calculating the 
                        #movement of the cue ball over a short period of time
                        if len(cueBallPts) < 2 and (abs(center[0] - cueBallPts[0][0][0]) ** 2 + abs(
                                center[1] - cueBallPts[0][0][1]) ** 2) ** 0.5 > change:
                            center = (a, b)
                            cueBallPts.append([center, radius])

                        #we only want to save 2 "snapshots" of the cue ball's movement, hence we can save this contour 
                        #asextra
                        if len(cueBallPts) == 2:
                            extraCenters.append([center, radius])

                        #if we are here, this means that the pool shot has finished and the footage is transitioning
                        #to another pool shot; call clear() to reset all important variables
                        if len(extraCenters) > 2 and (
                                abs(center[0] - extraCenters[len(extraCenters) - 2][0][0]) ** 2 + abs(
                            center[1] - extraCenters[len(extraCenters) - 2][0][1]) ** 2) ** 0.5 > 100:
                            clear()
                                
                    #if we are here, this means the contour was actually a pool ball; save its location, radius, and color
                    elif len(coloredBallPts) < 1:
                        coloredBallPts.append([center, radius])
                        color.append([range[1]])

#function to predict the path of the cue ball
def predictCuePath(image):
    #to check whether the cue ball and another ball have touched or not
    global collided

    #check if we have found more than two snapshots of the cue ball and we have detected at least one pool ball
    if len(cueBallPts) == 2 and len(coloredBallPts) > 0:

        #store the first and second cue ball snapshots, as well its radius
        xPt0, yPt0 = cueBallPts[0][0][0], cueBallPts[0][0][1]
        xPt1, yPt1 = cueBallPts[1][0][0], cueBallPts[1][0][1]
        cueRadius = cueBallPts[1][1]
        colorCtrX, colorCtrY = coloredBallPts[0][0][0], coloredBallPts[0][0][1]
        colorRadius = coloredBallPts[0][1]

        #this represents the change in distance over the two snapshots of the cue ball's x and y position
        xS = xPt1 - xPt0
        yS = yPt1 - yPt0

        #check if the cue ball hasn't yet collided with any other ball
        if collided == False:
            for i in range(1, 100):
                #essentially, we are using linear algebra to "extend" the predicted path of the cue ball bit-by-bit based on
                #the change in position over the two snapshots we have recorded (calculating equation of 2D line and extending 
                #it beyond what we have seen)
                
                i = i / 10
                ePX = int(xPt1 + (xS * i))
                ePY = int(yPt1 + (yS * i))

                #fine tune parameters to account for footage variance
                if color[0][0] == "e":
                    param = 20
                elif color[0][0] == "c":
                    param = 6
                else:
                    param = 10

                #check if, when we have extended the line by a bit on this iteration, the cue ball is predicted to have touched 
                #a pool ball (if so, we draw the predicted path on the video and exit)
                if checkTouching(ePX, ePY, colorCtrX, colorCtrY, cueRadius, colorRadius, param):
                    cv2.line(image, (ePX, ePY), (xPt0, yPt0), lineColor, lineWidth)
                    cv2.circle(image, (xPt0, yPt0), circleWidth, (impactColor), -1)
                    cv2.circle(image, (ePX, ePY), circleWidth, collideColor, -1)
                    collisionPt.append([ePX, ePY])
                    collided = True
                    break
        else:
            #if we have collided, then we continue to draw the path we calculated above for the rest of the shot
            cv2.line(image, (collisionPt[0]), (xPt0, yPt0), lineColor, lineWidth)
            cv2.circle(image, (xPt0, yPt0), circleWidth, (impactColor), -1)
            cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)

#function to predict the path of a pool ball after it has been hit by the cue ball
def predictColoredBallPath(image):
    #to be used to see whether the pool ball is toucing the wall 
    global touchingWall
    #to be used to see whether the ball has been scored in the pocket or not
    global outcome

    #check if we have found a collision point
    if len(collisionPt) > 0:
        #the algorithm below is very similar to the one in predictCuePath() - same approach to "extend" predicted 
        #path of ball based on snapshots we have recorded previously
        colorCtrX, colorCtrY = coloredBallPts[0][0][0], coloredBallPts[0][0][1]
        colorRadius = coloredBallPts[0][1]

        xE = (colorCtrX - collisionPt[0][0])
        yE = (colorCtrY - collisionPt[0][1])

        for i in range(0, 100):
            #refer to predictCuePath() function
            i = i / 10
            ePX = int(colorCtrX + (xE * i))
            ePY = int(colorCtrY + (yE * i))

            #check if the pool ball has touched a wall or not; if so, we want to predict its bounce trajectory
            if touchesWall(ePX, ePY):
                cv2.line(image, (collisionPt[0]), (ePX, ePY), lineColor, lineWidth)
                cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)
                cv2.circle(image, (ePX, ePY), circleWidth, collideColor, -1)
                wallPoint.append([ePX, ePY])
                touchingWall = True
                getBounceLine(image, (collisionPt[0]), (ePX, ePY))
                break
            
            #otherwise, if it has been scored in a pocket, we should display the outcome
            elif inAnyPocket(ePX, ePY, colorRadius):
                cv2.line(image, (collisionPt[0]), (ePX, ePY), lineColor, lineWidth)
                cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)
                cv2.circle(image, (ePX, ePY), circleWidth, inColor, -1)
                showOutcome(image, "In!")
                break

#function to calculate the trajectory of a pool ball after it has rebounded against a wall
def getBounceLine(image, pt1, pt2):
    #basically here, we are trying to use linear algebra to "reflect" the predicted path against the wall
    rad = coloredBallPts[0][1]
    bouncePt = pt2[0], pt2[1]
    refPoint = int((pt2[0] - pt1[0]) * 0.7) + pt2[0], pt1[1]
    xE = (refPoint[0] - bouncePt[0])
    yE = (refPoint[1] - bouncePt[1])

    #fine tuning parameters based on angle calculations specific to each shot
    if xE <= 15:
        refPoint = int((pt2[0] - pt1[0]) * 6) + pt2[0], pt1[1]

    for i in range(0, 80):
        #again, this uses similar logic to the previous two functions
        i = i / 10
        ePX = int(refPoint[0] + (xE * i))
        ePY = int(refPoint[1] + (yE * i))

        #if it touches the wall, we know it is certainly not going to be scored (not enough momentum); display 
        #the outcome of fail
        if touchesWall(ePX, ePY):
            cv2.circle(image, (bouncePt), circleWidth, outColor, -1)
            showOutcome(image, "Out!")
            break
            
        #if it has been scored after the rebound, we want to show the outcome of scored
        elif inAnyPocket(ePX, ePY, rad):
            cv2.line(image, (ePX, ePY), (bouncePt), lineColor, lineWidth)
            cv2.circle(image, (bouncePt), circleWidth, collideColor, -1)
            cv2.circle(image, (ePX, ePY), circleWidth, inColor, -1)
            showOutcome(image, "In!")
            break

#function to check if a given coordinate is "touching" one of the pool table walls
def touchesWall(x1, y1):
    #depending on the variation in camera frames, we have slightly different coordinates; return 
    #true if either the x or y coordinate in within the specified range
    if color[0][0] == 'b' or color[0][0] == 'c':
        return x1 <= 240 or x1 >= 1700 or y1 <= 160 or y1 >= 760
    else:
        return x1 <= 240 or x1 >= 1700 or y1 <= 160 or y1 >= 810

#function to check if a given coordinate and radius is within any pocket
def inAnyPocket(x1, y1, radius):
    #iterate through each stored pocket location, and, if the coordinate/radius passed as a parameter 
    #is within any of them, return true
    for i in range(6):
        if checkTouching(x1, y1, pockets[i][0], pockets[i][1], radius, 35, 19):
            return True
            break

#function to display the outcome ("In"/"Out") of a pool shot
def showOutcome(image, result):
    #using cv2 library to display specific message depending on outcome
    #used simple font and simple RGB colors to convey an elegant design
    if result == "In!":
        cv2.rectangle(image, (30, 15), (380, 115), (inColor), -1)
        cv2.line(image, (455, 105), (425, 70), inColor, 13)
        cv2.line(image, (455, 105), (535, 40), inColor, 13)
        cv2.putText(image, str(result), (170, 87), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
    else:
        cv2.rectangle(image, (30, 15), (380, 115), (outColor), -1)
        cv2.line(image, (420, 35), (490, 105), outColor, 15)
        cv2.line(image, (420, 105), (490, 35), outColor, 15)
        cv2.putText(image, str(result), (150, 87), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

#check if two given coordinates and two radii (representing two circles) are touching
def checkTouching(x1, y1, x2, y2, r1, r2, tolerance):
    #tolerance is essentially the margin of error we are allowing in terms of defining what is "touching"
    d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    if d - tolerance <= r1 + r2 <= d + tolerance:
        #return true if they are touching; false otherwise
        return True
    else:
        return False

#function to "reset" all important variables used for calculations each time pool table is reset for a shot
def clear():
    global cueBallPts
    global coloredBallPts
    global collisionPt
    global wallPoint
    global collided
    global touchingWall
    global outcome
    global color
    global change
    global extraCenters
    cueBallPts = []
    coloredBallPts = []
    collisionPt = []
    wallPoint = []
    color = []
    collided = False
    touchingWall = False
    outcome = ""
    change = 50
    extraCenters = []

#this runs continuously to run our detection functions, display the outcomes, and save each frame to our writer
while cap.isOpened():
    ret, frame = cap.read()
    detectObjects(frame)
    predictCuePath(frame)
    predictColoredBallPath(frame)
    cv2.imshow("out", frame)
    capProcessed.write(frame)

#when the video finishes, we close all of our readers and windows
capProcessed.release()
cap.release()
cv2.destroyAllWindows()
