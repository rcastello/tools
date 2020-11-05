import cv2
import numpy as np
import sys
import shutil
import os

class Crop():

    def __init__(self, image_name):

        self.image_name = image_name
        self.lpnts = np.empty((1,0,2), dtype=np.int32)
        self.rpnts = []

        self.image = cv2.imread(self.image_name,-1)
        self.copied_image = self.image.copy()

    def crop_for_mouse(self,event,x,y,flags= None,parameters = None):

        self.event = event
        self.x = x
        self.y = y
        self.flags = flags
        self.parameters = parameters

        if self.event == cv2.EVENT_LBUTTONDOWN:
       	    self.lpnts = np.append(self.lpnts, np.array([[[self.x, self.y]]]), axis=1)
       	    cv2.polylines(self.image, [self.lpnts], False, (0, 0, 255))

        elif self.event == cv2.EVENT_MBUTTONDOWN:
       	    self.lpnts = np.append(self.lpnts, np.array([[[self.x, self.y]]]), axis=1)
       	    cv2.polylines(self.image, [self.lpnts], True, (0, 0, 255))
            self.rpnts.append(self.lpnts)
            self.lpnts = np.empty((1,0,2), dtype=np.int32)
            self.copied_image = self.image.copy()

        elif self.event == cv2.EVENT_RBUTTONDOWN: ## LBUTTONDBLCLK RBUTTONDOWN 
            self.lpnts = np.empty((1,0,2), dtype=np.int32)
            self.image = self.copied_image.copy()

    def do_crop(self):

        cv2.namedWindow("CROP", cv2.WINDOW_NORMAL) ## Magnifying the window for more precise labelling 
        cv2.resizeWindow("CROP", 1000, 1000) ## 1250
        cv2.setMouseCallback("CROP",self.crop_for_mouse)
        self.skip = False

        while True:

            cv2.imshow("CROP",self.image)
            cv2.setMouseCallback("CROP",self.crop_for_mouse)
            keypress = cv2.waitKey(1)

            if keypress == ord('r'):
                self.image = self.copied_image.copy() ## RC -- this command doesn't really work in practice
                self.lpnts = np.empty((1,0,2), dtype=np.int32)

            if keypress == ord('b'):
                self.image = cv2.imread(self.image_name,-1)
                self.copied_image = self.image.copy()
                self.lpnts = np.empty((1,0,2), dtype=np.int32)
                self.rpnts = []

            if keypress == ord('n'):
               #move to the next file 
               self.skip = True
               break
   
            if keypress == ord('c'):
               self.skip = False
               break
        
        if self.skip is False:
          
            image_path = self.image_name.split(os.path.sep)
            image_orig_path = os.sep.join(image_path[:-1]) + '/PV/' + image_path[-1]
            print("Saving original image to ", image_orig_path)
            shutil.move(self.image_name, image_orig_path) ## RC comment: once final it should become  --> shutil.move(self.image_name, image_path) ## shutil.copyfile

            mask  = np.zeros(self.image.shape, dtype=np.uint8)
            channel_count = self.image.shape[2]
            ignore_mask_color = (255,)*channel_count
            
            for point in self.rpnts:
                cv2.fillPoly(mask, point, ignore_mask_color)

            masked_image = cv2.bitwise_and(self.image,mask)

            image_path = os.sep.join(image_path[:-1]) + '/PV/labels/'\
                         + image_path[-1][:-4] + '_label' + \
                         image_path[-1][-4:] 
             
            print("Saving labelled image to ", image_path) 
            cv2.imshow("ROI", masked_image)
            cv2.imwrite(image_path, mask) ## Writing the B&W mask (instead of masked_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()	
        else:
            image_path = self.image_name.split(os.path.sep)
            image_path = os.sep.join(image_path[:-1]) + '/noPV/' + image_path[-1]
            print("Saving original image to ", image_path)
            shutil.move(self.image_name, image_path) ## RC comment: once final it should become  --> shutil.move(self.image_name, image_path)
