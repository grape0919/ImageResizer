import configparser
from tkinter import *
# from tkmacosx import Button
from tkinter import filedialog, messagebox
from tkinter import font
from tkinter.ttk import Progressbar

from configparser import ConfigParser
import os

from PIL import Image, ImageDraw
import cv2

import time

DEFAULT_BGCOLOR = "white"
DEFAULT_BUTTON_COLOR = "ghost white"
POINT_BUTTON_COLOR = "#0f4c81"

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300

GRID_MAX_COL = 2

IMAGE_EXT_LIST = ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi",
                     "png", "webp", "bmp", "dib", "jp2", "j2k", 
                     "jpf", "jpx", "jpm", "mj2", "JPG", "JPEG", 
                     "JPE", "JIF", "JFIF", "JFI", "PNG", "WEBP", 
                     "BMP", "DIB", "JP2", "J2K", "JPF", "JPX", 
                     "JPM", "MJ2"
                    ]

TITLE = "Resizer"

class MainWindow(Frame):

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.loadConf()
        self.initUI()

    def initUI(self):
        self.master.title(TITLE)
        self.pack(fill=BOTH, expand=1)
        self.configure(bg=DEFAULT_BGCOLOR)
        self.centerWindow(self.master, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.title = Label(self, text=TITLE, background=DEFAULT_BGCOLOR, font=font.Font(size=12, weight=font.BOLD), pady="10px")
        self.title.grid(row=0, column=0, columnspan=GRID_MAX_COL, sticky="nw")

        listFrame = Frame(self, background=DEFAULT_BGCOLOR,
                            highlightbackground=DEFAULT_BGCOLOR, padx="5px")
        scrollbarY = Scrollbar(listFrame)
        scrollbarY.pack(side="right", fill="y")

        scrollbarX = Scrollbar(listFrame, orient=HORIZONTAL)
        scrollbarX.pack(side="bottom", fill="x")

        #self.dirPath = StringVar()
        self.listBox = Listbox(listFrame, width=52, yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set)        
        self.listBox.pack(side='left', fill='both')

        scrollbarX.config(command=self.listBox.xview)
        scrollbarY.config(command=self.listBox.yview)

        listFrame.grid(row = 1, column=0)
    
        self.v_outputDirPath = StringVar()
        try :
            savedDirPath = self.config.get('output', 'outputDirPath')

        except :
            savedDirPath = ""
            
        self.v_outputDirPath.set(savedDirPath)

        self.outputPath = Entry(self, width=52, state="readonly", textvariable=self.v_outputDirPath)
        self.outputPath.grid(row=2, column=0)

        outputDirButton = Button(self, text="저장 폴더", command=self.selectOutputDirDlg, width=10)
        outputDirButton.grid(row = 2, column=1)

        selectButtonFrame = Frame(self, background=DEFAULT_BGCOLOR,
                            highlightbackground=DEFAULT_BGCOLOR, padx="5px")

        selectFile = Button(selectButtonFrame, text="파일 추가", command=self.selectFilesDlg)
        selectFile.pack(pady=2)

        delList = Button(selectButtonFrame, text="선택 삭제", command=self.deleteList)
        delList.pack(pady=2)

        allDelList = Button(selectButtonFrame, text="전체 삭제", command=self.allDeleteList)
        allDelList.pack(pady=2)


        selectButtonFrame.grid(row = 1, column = 1, sticky="n")

        processFrame = Frame(self, background=DEFAULT_BGCOLOR,
                            highlightbackground=DEFAULT_BGCOLOR, pady="5px")
        runBtn = Button(processFrame, text="변환", command=self.runProcess, width=10, 
                             background=POINT_BUTTON_COLOR, fg=DEFAULT_BGCOLOR, highlightbackground=DEFAULT_BGCOLOR)
        runBtn.grid(row = 0, column=0)

        processFrame.grid(row = 3, column=0, columnspan=2, sticky="n")

        self.place(x=10, y=5)

    def centerWindow(self, view, w, h):

        sw = view.winfo_screenwidth()
        sh = view.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2

        view.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def selectFilesDlg(self):
        print("click openDlg")

        filenames = filedialog.askopenfilenames(parent=self,
            initialdir=os.getcwd(), title="Select files")

        file_list = self.tk.splitlist(filenames)
        for file in file_list:
            if self.checkExt(file):
                self.listBox.insert(END, file)

    def selectOutputDirDlg(self):
        print("click openDirDlg")

        dirPath = filedialog.askdirectory(parent=self,
            initialdir=os.getcwd(), title="Select directory")

        self.v_outputDirPath.set(dirPath)
        self.saveConf()

    def checkExt(self, file:str):
        ext = file.split(".")[-1]
        if ext in IMAGE_EXT_LIST:
            return True
        else :
            return False

    def deleteList(self):
        selectedIndex = self.listBox.curselection()
        if selectedIndex:
            self.listBox.delete(selectedIndex)

    def allDeleteList(self):
        self.listBox.delete(0, END)

    def runProcess(self):
        self.master.grab_set()
        popup = Toplevel(self.root)
        popup.overrideredirect(1)
        self.root.eval(f'tk::PlaceWindow {str(popup)} center')
        Label(popup, text="이미지 변환중..", width=50, height=2).grid(row=0,column=0)

        progress_step = self.listBox.size()

        progress_var = IntVar()
        progress_bar = Progressbar(popup, variable=progress_var, maximum=progress_step, length=300)
        progress_bar.grid(row=1, column=0)#.pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        # popup.pack_slaves()

        image_list = self.listBox.get(0, END)
        
        for i, image in enumerate(image_list):
            popup.update()
            time.sleep(0.5)
            progress_var.set(i)
            self.resizing(image)

        popup.destroy()
        messagebox.showinfo("메세지", "변환이 완료되었습니다.")

    def resizing(self, imgFilePath : str):
        print("proc : ", imgFilePath)
        file, ext = os.path.splitext(imgFilePath)
        img_pic = Image.open(imgFilePath)
        maxLegth = max(img_pic.width, img_pic.height)
        img = Image.new('RGB', (maxLegth, maxLegth), color='white')
        
        wh = img_pic.width > img_pic.height
        point = (0, int((img_pic.width - img_pic.height)/2)) if wh else (int((img_pic.height - img_pic.width)/2), 0) 
        img.paste(img_pic, point)
        img.save(os.path.join(self.v_outputDirPath.get(), file.split("/")[-1]+"_resized.png"))

    def loadConf(self):
        self.config = ConfigParser()
        self.config.read('resizer.ini')
        print("load Configuration")

    def saveConf(self):
        print("save conf")
        try:
            self.config.add_section('output')
        except configparser.DuplicateSectionError:
            print("output 옵션이 정상적으로 등록되어있습니다.")

        self.config.set('output', 'outputDirPath', self.v_outputDirPath.get())

        with open('resizer.ini', 'w') as f:
            self.config.write(f)

    
        
    

def main():
    root = Tk()
    root.resizable(False, False)
    root.configure(bg=DEFAULT_BGCOLOR)
    ex = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()


# root = Tk()
# root.title('Unziper')
# root.geometry('300x300+100+100')
# root.mainloop()
