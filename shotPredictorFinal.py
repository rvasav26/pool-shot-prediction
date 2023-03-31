import numpy as np
import cv2

cap = cv2.VideoCapture('videos/Shot-Predictor-Video.mp4')
width = int(cap.get(3))
height = int(cap.get(4))
capProcessed = cv2.VideoWriter('ProcessedPool/processedShotsVideo.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))

pockets = [[194, 163], [906, 128], [1655, 170], [1617, 780], [904, 830], [270, 770]]

pocketColors = [[[0, 179, 0, 118, 54, 200], "pocket"]]

colorArray = \
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

def detectObjects(image):
    global change
    global extraCenters

    imgHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for range in colorArray:
        h_min, h_max, s_min, s_max, v_min, v_max = range[0][0], range[0][1], range[0][2], range[0][3], range[0][4], \
                                                   range[0][5]
        lowRange = np.array([h_min, s_min, v_min])
        upRange = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(imgHSV, lowRange, upRange)
        mask = cv2.GaussianBlur(mask, (3, 3), 3)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)
            if 200 < y < 760 and 270 < x < 1660:
                (a, b), radius = cv2.minEnclosingCircle(cnt)
                a, b = int(a), int(b)
                center = (a, b)
                radius = int(radius)

                if range[1] == "d":
                    center = (a - 20, b + 5)

                if 22.5 < radius < 30 and w > 30:

                    if range[1] == "c":
                        change = 35

                    if colorArray.index(range) == 0:

                        if len(cueBallPts) == 0:
                            cueBallPts.append([center, radius])

                        if len(cueBallPts) < 2 and (abs(center[0] - cueBallPts[0][0][0]) ** 2 + abs(
                                center[1] - cueBallPts[0][0][1]) ** 2) ** 0.5 > change:
                            center = (a, b)
                            cueBallPts.append([center, radius])

                        if len(cueBallPts) == 2:
                            extraCenters.append([center, radius])

                        if len(extraCenters) > 2 and (
                                abs(center[0] - extraCenters[len(extraCenters) - 2][0][0]) ** 2 + abs(
                            center[1] - extraCenters[len(extraCenters) - 2][0][1]) ** 2) ** 0.5 > 100:
                            clear()
                    elif len(coloredBallPts) < 1:
                        coloredBallPts.append([center, radius])
                        color.append([range[1]])


def predictCuePath(image):
    global collided
    if len(cueBallPts) == 2 and len(coloredBallPts) > 0:

        xPt0, yPt0 = cueBallPts[0][0][0], cueBallPts[0][0][1]
        xPt1, yPt1 = cueBallPts[1][0][0], cueBallPts[1][0][1]
        cueRadius = cueBallPts[1][1]
        colorCtrX, colorCtrY = coloredBallPts[0][0][0], coloredBallPts[0][0][1]
        colorRadius = coloredBallPts[0][1]

        xS = xPt1 - xPt0
        yS = yPt1 - yPt0
        if collided == False:
            for i in range(1, 100):
                i = i / 10
                ePX = int(xPt1 + (xS * i))
                ePY = int(yPt1 + (yS * i))

                if color[0][0] == "e":
                    param = 20
                elif color[0][0] == "c":
                    param = 6
                else:
                    param = 10
                if checkTouching(ePX, ePY, colorCtrX, colorCtrY, cueRadius, colorRadius, param):
                    cv2.line(image, (ePX, ePY), (xPt0, yPt0), lineColor, lineWidth)
                    cv2.circle(image, (xPt0, yPt0), circleWidth, (impactColor), -1)
                    cv2.circle(image, (ePX, ePY), circleWidth, collideColor, -1)
                    collisionPt.append([ePX, ePY])
                    collided = True
                    break
        else:
            cv2.line(image, (collisionPt[0]), (xPt0, yPt0), lineColor, lineWidth)
            cv2.circle(image, (xPt0, yPt0), circleWidth, (impactColor), -1)
            cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)


def predictColoredBallPath(image):
    global touchingWall
    global outcome
    if len(collisionPt) > 0:
        colorCtrX, colorCtrY = coloredBallPts[0][0][0], coloredBallPts[0][0][1]
        colorRadius = coloredBallPts[0][1]

        xE = (colorCtrX - collisionPt[0][0])
        yE = (colorCtrY - collisionPt[0][1])

        for i in range(0, 100):
            i = i / 10
            ePX = int(colorCtrX + (xE * i))
            ePY = int(colorCtrY + (yE * i))

            if touchesWall(ePX, ePY):
                cv2.line(image, (collisionPt[0]), (ePX, ePY), lineColor, lineWidth)
                cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)
                cv2.circle(image, (ePX, ePY), circleWidth, collideColor, -1)
                wallPoint.append([ePX, ePY])
                touchingWall = True
                getBounceLine(image, (collisionPt[0]), (ePX, ePY))
                break
            elif inAnyPocket(ePX, ePY, colorRadius):
                cv2.line(image, (collisionPt[0]), (ePX, ePY), lineColor, lineWidth)
                cv2.circle(image, (collisionPt[0]), circleWidth, collideColor, -1)
                cv2.circle(image, (ePX, ePY), circleWidth, inColor, -1)
                showOutcome(image, "In!")
                break


def getBounceLine(image, pt1, pt2):
    rad = coloredBallPts[0][1]
    bouncePt = pt2[0], pt2[1]
    refPoint = int((pt2[0] - pt1[0]) * 0.7) + pt2[0], pt1[1]
    xE = (refPoint[0] - bouncePt[0])
    yE = (refPoint[1] - bouncePt[1])
    if xE <= 15:
        refPoint = int((pt2[0] - pt1[0]) * 6) + pt2[0], pt1[1]

    for i in range(0, 80):
        i = i / 10
        ePX = int(refPoint[0] + (xE * i))
        ePY = int(refPoint[1] + (yE * i))

        if touchesWall(ePX, ePY):
            cv2.circle(image, (bouncePt), circleWidth, outColor, -1)
            showOutcome(image, "Out!")
            break

        elif inAnyPocket(ePX, ePY, rad):
            cv2.line(image, (ePX, ePY), (bouncePt), lineColor, lineWidth)
            cv2.circle(image, (bouncePt), circleWidth, collideColor, -1)
            cv2.circle(image, (ePX, ePY), circleWidth, inColor, -1)
            showOutcome(image, "In!")
            break


def touchesWall(x1, y1):
    if color[0][0] == 'b' or color[0][0] == 'c':
        return x1 <= 240 or x1 >= 1700 or y1 <= 160 or y1 >= 760
    else:
        return x1 <= 240 or x1 >= 1700 or y1 <= 160 or y1 >= 810


def inAnyPocket(x1, y1, radius):
    for i in range(6):
        if checkTouching(x1, y1, pockets[i][0], pockets[i][1], radius, 35, 19):
            return True
            break


def showOutcome(image, result):
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


def checkTouching(x1, y1, x2, y2, r1, r2, tolerance):
    d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    if d - tolerance <= r1 + r2 <= d + tolerance:
        return True
    else:
        return False

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

while cap.isOpened():
    ret, frame = cap.read()
    detectObjects(frame)
    predictCuePath(frame)
    predictColoredBallPath(frame)
    cv2.imshow("out", frame)
    capProcessed.write(frame)

capProcessed.release()
cap.release()
cv2.destroyAllWindows()
