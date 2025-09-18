import cv2
import mediapipe as mp
import time
import pyautogui

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

mpHands =mp.solutions.hands
hands =mpHands.Hands()
mpDraw=mp.solutions.drawing_utils

pTime=0
cTime=0
click_start_time = 0
prev_scroll_y = 0
scroll_threshold = 5
clicking = False
has_clicked = False
mouse_active= False
prev_x, prev_y = 0, 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if lmList:

                fingers = []

                fingers.append(1 if lmList[8][2] < lmList[6][2] else 0)

                fingers.append(1 if lmList[12][2] < lmList[10][2] else 0)

                fingers.append(1 if lmList[16][2] < lmList[14][2] else 0)

                fingers.append(1 if lmList[20][2] < lmList[18][2] else 0)

                fingers.append(1 if lmList[4][1] < lmList[3][1] else 0)

                if fingers ==[1,1,0,0,0]:
                    cv2.putText(img, "Mouse operation", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                    mouse_active = True

                elif fingers ==[0,0,0,0,0]:
                    cv2.putText(img, "Close the mouse", (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
                    mouse_active = False

                if fingers ==[1,0,0,1,0]:
                    pyautogui.rightClick()
                    time.sleep(2)

                if fingers ==[1,1,1,1,1]:
                    current_scroll_y = lmList[8][2]
                    print("current_scroll_y:", current_scroll_y)

                    if prev_scroll_y != 0:
                        scroll_diff = current_scroll_y - prev_scroll_y
                        print("scroll_diff:", scroll_diff)

                        if abs(scroll_diff) > scroll_threshold:

                            if scroll_diff > 0:
                                pyautogui.scroll(-37)
                            else:
                                pyautogui.scroll(37)

                    prev_scroll_y = current_scroll_y

                else:
                    prev_scroll_y = 0

                if mouse_active:
                    x1 , y1 = lmList[8][1], lmList[8][2]
                    frame_margin = 100
                    screen_width, screen_height = pyautogui.size()
                    frame_width, frame_height = img.shape[1], img.shape[0]

                    active_area_x1 = frame_margin
                    active_area_y1 = frame_margin
                    active_area_x2 = frame_width - frame_margin
                    active_area_y2 = frame_height - frame_margin

                    x1 =max(active_area_x1, min(x1,active_area_x2))
                    y1 =max(active_area_y1, min(y1,active_area_y2))

                    norm_x = (x1 - active_area_x1) / (active_area_x2 - active_area_x1)
                    norm_y = (y1 - active_area_y1) / (active_area_y2 - active_area_y1)

                    sensitivity = 1.0

                    screen_x = int(norm_x * screen_width * sensitivity)
                    screen_y = int(norm_y * screen_height * sensitivity)

                    screen_x = max(10, min(screen_x, screen_width-10))
                    screen_y = max(10, min(screen_y, screen_height-10))

                    if abs(screen_x - prev_x) > 5 or abs(screen_y - prev_y) > 5:
                        smooth_factor = 0.2

                        smooth_x = prev_x + (screen_x - prev_x) * smooth_factor
                        smooth_y = prev_y + (screen_y - prev_y) * smooth_factor

                        pyautogui.moveTo(int(smooth_x), int(smooth_y))
                        prev_x, prev_y = smooth_x, smooth_y

                    thumb_tip=lmList[4][1],lmList[4][2]
                    index_tip=lmList[8][1],lmList[8][2]
                    distance= ((thumb_tip[0]-index_tip[0])**2 + (thumb_tip[1]-index_tip[1])**2)**0.5

                    if distance < 40:
                        if not clicking:
                            clicking = True
                            has_clicked = False
                            click_start_time = time.time()
                    else :
                        if clicking:
                            click_duration = time.time() - click_start_time
                            if not has_clicked:
                                if click_duration > 0.5:
                                    pyautogui.doubleClick()
                                else:
                                    pyautogui.click()
                                has_clicked = True
                        clicking = False

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img,str(int(fps)),(10,70),cv2.FONT_HERSHEY_SIMPLEX,3,(255,255,255),2)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break