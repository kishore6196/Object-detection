import numpy as np
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep
import cv2 as cv
import os

class WindowCapture:
    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception(f'Window not found: {window_name}')
        self.set_window_dimensions()

    def set_window_dimensions(self):
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        border_pixels = 8
        titlebar_pixels = 30
        self.w -= (border_pixels * 2)
        self.h -= (titlebar_pixels + border_pixels)
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # Debug: Print window dimensions
        print(f"Window dimensions: Width={self.w}, Height={self.h}")
    
    def resize_window(self, new_width, new_height):
        rect = win32gui.GetWindowRect(self.hwnd)
        x, y = rect[0], rect[1]
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, x, y, new_width, new_height, win32con.SWP_NOZORDER)
        self.set_window_dimensions()
    
        # Validate dimensions
        if self.w <= 0 or self.h <= 0:
            raise ValueError("Invalid window dimensions.")

    def get_screenshot(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # Cleanup
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[...,:3]
        img = np.ascontiguousarray(img)
        return img

    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while True:
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpeg")
            sleep(1)

    def get_window_size(self):
        return (self.w, self.h)


class ImageProcessor:
    W = 0
    H = 0
    net = None
    ln = None
    classes = {}
    colors = []

    def __init__(self, img_size, cfg_file, weights_file):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(cfg_file, weights_file)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.W = img_size[0]
        self.H = img_size[1]
        
        with open('yolov4-tiny/obj.names', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            self.classes[i] = line.strip()
        
        # If you plan to utilize more than six classes, please include additional colors in this list.
        self.colors = [
            (0, 0, 255), 
            (0, 255, 0), 
            (255, 0, 0), 
            (255, 255, 0), 
            (255, 0, 255), 
            (0, 255, 255)
        ]
        

    def proccess_image(self, img):

        blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)
        
        coordinates = self.get_coordinates(outputs, 0.5)

        self.draw_identified_objects(img, coordinates)

        return coordinates

    def get_coordinates(self, outputs, conf):

        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            scores = output[5:]
            
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[:4] * np.array([self.W, self.H, self.W, self.H])
                p0 = int(x - w//2), int(y - h//2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)

        if len(indices) == 0:
            return []

        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            coordinates.append({'x': x, 'y': y, 'w': w, 'h': h, 'class': classIDs[i], 'class_name': self.classes[classIDs[i]]})
        return coordinates

    def draw_identified_objects(self, img, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']
            
            color = self.colors[classID]
            
            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv.putText(img, self.classes[classID], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('window',  img)

# Usage example
window_name = "Minecraft 1.20.4 - Singleplayer"
cfg_file_name = "./yolov4-tiny/yolov4-tiny-custom.cfg"
weights_file_name = "yolov4-tiny-custom_last.weights"

try:
    wincap = WindowCapture(window_name)
    
    # Resize the window (example dimensions)
    new_width = 800
    new_height = 600
    wincap.resize_window(new_width, new_height)

    improc = ImageProcessor(wincap.get_window_size(), cfg_file_name, weights_file_name)

    while True:
        ss = wincap.get_screenshot()
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

        coordinates = improc.proccess_image(ss)
        for coordinate in coordinates:
            print(coordinate)
        print()
except Exception as e:
    print(f"An error occurred: {e}")




