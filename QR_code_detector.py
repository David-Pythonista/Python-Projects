import cv2,tkinter, PIL.ImageTk
from tkinter import Tk, Button, RIGHT, LEFT, filedialog, messagebox
from math import sqrt

class Application():

    def __init__(self):
        "Make a window for the program."
        self.window = Tk()
        self.window.title("QR code detector")
        self.canvas = tkinter.Canvas(self.window, width=600, height=600, bg='white')
        self.canvas.pack()
        Button(self.window,text='Start',width=20,command=self.start).pack(side=RIGHT,padx=10,pady=10)
        Button(self.window,text='Load a file',width=20,command=self.load).pack(side=LEFT,padx=10,pady=10)
        self.window.mainloop()

    def start(self):
        "It runs the application methods."
        try:
            self.list_of_finding_patterns()
            self.draw_the_QR_code()
            self.show_image(self.image)
        except:
            messagebox.showinfo("Error", "Error!")

    def load(self):
        "It loads an image from the given path."
        path = filedialog.askopenfilename(filetypes=[("All","jpg")])
        self.image = cv2.imread(path)
        self.imagegray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
        self.ret, self.threshold = cv2.threshold(self.imagegray,127,255,0)
        self.contours, self.hierarchy = cv2.findContours(self.threshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        self.show_image(self.image)      

    def show_image(self,image):
        "Convert the loaded image to Tkinter handling and show it."
        self.canvas.delete("all")
        height, width, channels = image.shape
        ratio = max(height,width)/600
        image_resized = cv2.resize(image,(int(width/ratio),int(height/ratio)), interpolation = cv2.INTER_AREA)
        image_converted = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(image_resized))
        self.canvas.create_image(0, 0, image=image_converted, anchor=tkinter.NW)
        self.window.mainloop()
       
    def determine_area(self,shape_number):
        "Returns the area of the given contour or shape."
        return cv2.contourArea(self.contours[shape_number])
        
    def distance(self,x1,y1,x2,y2):
        "Calculate the distance between two points."
        return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

    def list_of_finding_patterns(self):
        "Determine the coordinates of the finding patterns."
        self.coords = []
        for item in self.hierarchy[0]:
            if item[2] == -1 and item[3] != 0:
                for cnt in self.contours:
                    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)

                    if len(approx) == 4:
                        inner_area = self.determine_area(item[3]+1)
                        mid_area = self.determine_area(item[3])
                        outer_area = self.determine_area(item[3]-1)
                        out_mid = float(outer_area)/mid_area
                        inn_mid = float(inner_area)/mid_area

                        if 0.8*1.96 < out_mid < 1.2*1.96:
                            if 0.8*0.36 < inn_mid < 1.2*0.36:
                                cv2.drawContours(self.image, self.contours, item[3]-1, (0,255,0), 2)

                                "Calculate the center of mass of the object."
                                M = cv2.moments(self.contours[item[3]+1])
                                x = int(M['m10']/M['m00'])
                                y = int(M['m01']/M['m00'])

                                if (x,y,self.determine_area(item[3])) not in self.coords:
                                    self.coords.append((x,y,self.determine_area(item[3])))
                                for i in self.coords:
                                    cv2.circle(self.image,(i[0],i[1]),20,(0,255,0),-1)

    def draw_the_QR_code(self):
        "Show the QR code(s) in the picture."
        for i in range(len(self.coords)):
            for j in range(len(self.coords)):
                for k in range(len(self.coords)):

                    if(i!=j and j!=k and i!=k):
                        if(0.96<self.coords[i][2]/self.coords[j][2]<1.04):
                            if(0.96<self.coords[i][2]/self.coords[k][2]<1.04):

                                distIJ = self.distance(self.coords[i][0],self.coords[i][1],self.coords[j][0],self.coords[j][1])
                                distIK = self.distance(self.coords[i][0],self.coords[i][1],self.coords[k][0],self.coords[k][1])
                                distJK = self.distance(self.coords[j][0],self.coords[j][1],self.coords[k][0],self.coords[k][1])

                                if(0.98 < distIJ/distJK<1.02) and sqrt(2)-0.05<distIK/distJK<sqrt(2)+0.05:

                                    cv2.line(self.image,(self.coords[i][0],self.coords[i][1]),(self.coords[j][0],self.coords[j][1]),(0,255,255),8)
                                    cv2.line(self.image,(self.coords[i][0],self.coords[i][1]),(self.coords[k][0],self.coords[k][1]),(255,0,0),8)
                                    cv2.line(self.image,(self.coords[k][0],self.coords[k][1]),(self.coords[j][0],self.coords[j][1]),(255,0,255),8)
if __name__ == '__main__':
    program = Application()