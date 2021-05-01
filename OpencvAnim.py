import bpy
import cv2
import time
import numpy
import mediapipe as mp
import mathutils

class OpenCVAnimOperator(bpy.types.Operator):
    bl_idname = "wm.opencv_operator"
    bl_label = "OpenCV Animation Operator"
    
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    
    _timer = None
    _cap  = None
    stop = False
    
    width = 640
    height = 480
    
    thumb = bpy.data.objects["thumb"]
    fourth = bpy.data.objects["fourth"]
    middle = bpy.data.objects["middle"]
    midright = bpy.data.objects["midright"]
    index1 = bpy.data.objects["index"]
    
    def modal(self, context, event):
        if (event.type in {'RIGHTMOUSE', 'ESC'}) or self.stop == True:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.init_camera()
            _, img = self._cap.read()
            
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
            #print(results.multi_hand_landmarks)
            x4, x8 = 0, 0
            
            data = [0,0,0,0,0]
         
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    i = 0
                    for id, lm in enumerate(handLms.landmark):
                        # print(id, lm)
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        #print(id, cx, cy)
                        if id == 4 or id == 8 or id == 12 or id == 16 or id == 20:
                            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                            if id % 4 == 0:
                                data[i] = (((cx/600)*100, ((400 - cy)/400)*100))
                                i = i + 1
                                
#            center = abs((x8-x4)/2) + x8
#            leftf = abs(x4 - center)
#            rightf = abs(center - x8)
            
                
                self.thumb.location[1] = data[0][0]
                self.thumb.location[2] = data[0][1]
                self.index1.location[1] = data[1][0]
                self.index1.location[2] = data[1][1] 
                self.middle.location[1] = data[2][0]
                self.middle.location[2] = data[2][1] 
                self.midright.location[1] = data[3][0]
                self.midright.location[2] = data[3][1]
                self.fourth.location[1] = data[4][0]
                self.fourth.location[2] = data[4][1]  
                self.index1.keyframe_insert(data_path="location", index=1)
            
            cv2.imshow("Output", img)
            cv2.waitKey(1)

        return {'PASS_THROUGH'}
    
    def init_camera(self):
        if self._cap == None:
            self._cap = cv2.VideoCapture(0)
            
    def stop_playback(self, scene):
        print(format(scene.frame_current) + " / " + format(scene.frame_end))
        if scene.frame_current == scene.frame_end:
            bpy.ops.screen.animation_cancel(restore_frame=False)
        
    def execute(self, context):
        bpy.app.handlers.frame_change_pre.append(self.stop_playback)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        cv2.destroyAllWindows()
        self._cap.release()
        self._cap = None

def register():
    bpy.utils.register_class(OpenCVAnimOperator)

def unregister():
    bpy.utils.unregister_class(OpenCVAnimOperator)

if __name__ == "__main__":
    register()