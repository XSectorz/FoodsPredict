import tkinter
from tkinter import messagebox
import pandas as pd
import numpy as np
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import seaborn as sns
import math

from functools import partial
from tkinter import ttk

class ToggledFrame(tkinter.Frame):

    def __init__(self, parent, text="", *args, **options):
        tkinter.Frame.__init__(self, parent, *args, **options)

        self.show = tkinter.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)

        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")

        self.sub_frame = ttk.Frame(self, relief="sunken", borderwidth=5)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')


refImages = [None] * 11

def WarnBox(title, text):
    return tkinter.messagebox.showerror(title=title, message=text)

def clearResults(Frame):
   for widgets in Frame.winfo_children():
      widgets.destroy()

def _on_mousewheel(canvas, event):
    canvas.yview_scroll(-1*(event.delta/120), "units")

def showResult(Frame,sorted_data,listData):

    clearResults(Frame)

    objectFrame = tkinter.Frame(Frame)

    mainCanvas = tkinter.Canvas(objectFrame)
    mainCanvas.pack(side=tkinter.LEFT,fill=tkinter.BOTH,expand=1)

    scrollbar = tkinter.Scrollbar(objectFrame, orient=tkinter.VERTICAL,command=mainCanvas.yview)
    scrollbar.pack(side=tkinter.LEFT,fill=tkinter.Y,anchor=tkinter.W)

    secondFrame = tkinter.Frame(mainCanvas)
    mainCanvas.configure(yscrollcommand=scrollbar.set)
    secondFrame.bind('<Configure>', lambda e: mainCanvas.configure(scrollregion=mainCanvas.bbox('all')))
    mainCanvas.bind("<MouseWheel>", _on_mousewheel)
    mainCanvas.configure(scrollregion=mainCanvas.bbox("all"))

    mainCanvas.columnconfigure(0,weight=1)

    secondFrameID = mainCanvas.create_window((0,0),window=secondFrame,anchor='nw')
    mainCanvas.bind('<Configure>', lambda e: mainCanvas.itemconfigure(secondFrameID, width=e.width))

    objectFrame.pack(side=tkinter.LEFT,expand=True,fill=tkinter.BOTH)


    for i in range(10):

        t = ToggledFrame(secondFrame,text=sorted_data.iloc[i]['Food and Description Thai'], relief="raised", borderwidth=2,bg="#9AFFAA")
        t.pack(fill="x", expand=1, pady=5, padx=5, anchor="n")

        ttk.Label(t.sub_frame, text='ความคล้ายคลึงทางโภชนาการ ' + str(listData[len(listData)-1-i])).pack()

        canvas = tkinter.Canvas(t.sub_frame, width=200, height=200)
        canvas.pack()
        img = Image.open("images/" + sorted_data.iloc[i]['Food and Description Thai'] + ".jpg")
        #img = Image.open("output/heatmap.jpg")
        resized_img = img.resize((200,200), Image.Resampling.LANCZOS)
        refImages[i] = ImageTk.PhotoImage(resized_img)

        canvas.create_image(0,0,image=refImages[i],anchor='nw')

        ttk.Label(t.sub_frame, text='พลังงาน ' + str(sorted_data.iloc[i]['Energy(kcal)']) + " แคลลอรี่").pack()
        ttk.Label(t.sub_frame, text='โปรตีน ' + str(sorted_data.iloc[i]['Protein(g)']) + " กรัม").pack()
        ttk.Label(t.sub_frame, text='ไขมัน ' + str(sorted_data.iloc[i]['Fat(g)']) + " กรัม").pack()
        ttk.Label(t.sub_frame, text='คาร์โบไฮเดรต ' + str(sorted_data.iloc[i]['Carbohydrate, available\n(carbohydrate, total)(g)']) + " กรัม").pack()

def cosinSimilarity(dataCleaned,lstInput,listdata):
    for i in range(233):
        data = np.array([dataCleaned['Energy(kcal)'][i], dataCleaned['Protein(g)'][i], dataCleaned['Fat(g)'][i],
                         dataCleaned['Carbohydrate, available\n(carbohydrate, total)(g)'][i]], dtype=float)
        dot = np.dot(lstInput, data)
        magData = np.linalg.norm(data)
        magLstInput = np.linalg.norm(lstInput)
        cosine = dot / (magData * magLstInput)
        degree = float("{0:.3f}".format((math.acos(cosine) * 180 / math.pi)))

        strCosine = "{0:.6f}".format(cosine)
        listdata.append(strCosine)
        dataCleaned.loc[i, 'Cosine Similarity'] = "{0:.6f}".format(cosine)
        dataCleaned.loc[i, 'Degree Cosine Similarity'] = degree

def checkInput(input):

    try:
        int(input)
        return True
    except ValueError:
        try:
            float(input)
            return True
        except ValueError:
            return False


def checkCanCalCulate():
    if not checkInput(EnergyInput.get()):
        return False
    if not checkInput(ProteinInput.get()):
        return False
    if not checkInput(FatInput.get()):
        return False
    if not checkInput(CarbohydrateInput.get()):
        return False

    if float(EnergyInput.get()) <= 0:
        return False
    if float(ProteinInput.get()) <= 0:
        return False
    if float(FatInput.get()) <= 0:
        return False
    if float(CarbohydrateInput.get()) <= 0:
        return False

    return True

def resultCalculator(Frame,root):


    if checkCanCalCulate():
        clearResults(root)
        energy = float(EnergyInput.get())
        protein = float(ProteinInput.get())
        fat = float(FatInput.get())
        cabrohydrate = float(CarbohydrateInput.get())

        df = pd.read_excel('database.xlsx')
        Filter_df = df.filter(
            items=['Food and Description Thai', 'Food and Description English', 'Energy(kcal)', 'Protein(g)', 'Fat(g)',
                   'Carbohydrate, available\n(carbohydrate, total)(g)'])

        listData = []

        # print("DATA",energy,protein,fat,cabrohydrate)

        input = np.array([energy, protein, fat, cabrohydrate])

        cosinSimilarity(Filter_df, input, listData)
        Filter_df.sort_values(['Cosine Similarity'], ascending=0, inplace=True)
        Sort_df = Filter_df[['Food and Description Thai', 'Energy(kcal)', 'Protein(g)', 'Fat(g)',
                             'Carbohydrate, available\n(carbohydrate, total)(g)']]
        listData = sorted(listData)
        # print(Sort_df.head(10))
        # print("--------------")
        # print(Sort_df.iloc[0]['Food and Description Thai'])

        btn = tkinter.Button(root,text="Click to open HeatMap",bg="#9AFFAA")
        btn.bind("<Button>",lambda e: openHeatMapUI(Sort_df))

        btn.pack(pady=10)
        #openHeatMapUI(root, Sort_df)
        showResult(Frame, Sort_df, listData)
        #heatMap(root, Sort_df)
    else:
        WarnBox("Error", "ข้อมูลที่ใส่ผิดพลาดอาจจะมีปัญหาจาก\n1) ข้อมูลไม่ใช่ตัวเลข\n2) ข้อมูลมีค่าต้องมากกว่า 0")
        return

def openHeatMapUI(sortData):

    for k, v in window.children.copy().items():
        if isinstance(v, tkinter.Toplevel):
            v.destroy()

    newWindow = tkinter.Toplevel(window)
    newWindow.title("HeatMap UI")
    newWindow.iconbitmap("icon.ico")

    newWindow.resizable(False,False)
    newWindow.geometry("800x800")

    heatMap(newWindow, sortData)

def heatMap(frame,sortData):

    clearResults(frame)
    cor = sortData.iloc[:10, 1:].transpose().corr()
    fig, ax = plt.subplots(figsize=(20, 20))
    heatmap = sns.heatmap(data=cor, cmap='Greens', annot=True,
                annot_kws={
                    'fontsize': 16,
                    'fontweight': 'bold'
                }, fmt='.5g')
    heatmap_figure = heatmap.get_figure()
    heatmap_figure.savefig('output/heatmap.jpg')

    # HeatMap Graph Frame
    HeatMapGraphFrame = tkinter.LabelFrame(frame, text="HeatMapGraph")
    HeatMapGraphFrame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

    Newcanvas = tkinter.Canvas(HeatMapGraphFrame, width=800, height=650)
    Newcanvas.grid(row=0,column=0)
    Newcanvas.pack()
    img = Image.open("output/heatmap.jpg")
    resized_img = img.resize((800, 650), Image.Resampling.LANCZOS)
    refImages[10] = ImageTk.PhotoImage(resized_img)
    Newcanvas.create_image(0, 0, image=refImages[10], anchor='nw')

    index = 0

    for x in range(2):
        for y in range(5):
            framegrid = tkinter.Frame(master=frame,relief=tkinter.SUNKEN,borderwidth=1.5)
            framegrid.place(x=40+(y*135),y=700+(x*40),height=45,width=140)
            name = sortData.iloc[index]['Food and Description Thai']
            #print(name,index)
            labelGrid = tkinter.Label(master=framegrid,text="ID : " + str(sortData[sortData['Food and Description Thai'] == name].index[0])
                                      + "\n" + name)
            labelGrid.pack(padx=3,pady=3)
            index += 1

def createTempObject():

    for i in range(11):
        refImages[i] = ttk.Label()

window = tkinter.Tk()
window.title("Linear - ChooseFoods")
window.resizable(True,True)
window.iconbitmap("icon.ico")

frame = tkinter.Frame(window)
frame.pack()

Inputframe = tkinter.LabelFrame(frame, text="Nutritional Value")
Inputframe.grid(row=0, column=0, padx=20, pady=10)

EnergyLabel = tkinter.Label(Inputframe, text="Energy (kcal)")
EnergyLabel.grid(row=0, column=0)
ProteinLabel = tkinter.Label(Inputframe, text="Protein (g)")
ProteinLabel.grid(row=0, column=1)
FatLabel = tkinter.Label(Inputframe, text="Fat (g)")
FatLabel.grid(row=0, column=2)
CarbohydrateLabel = tkinter.Label(Inputframe, text="Carbohydrate (g)")
CarbohydrateLabel.grid(row=2, column=0)

EnergyInput = tkinter.Entry(Inputframe)
ProteinInput = tkinter.Entry(Inputframe)
FatInput = tkinter.Entry(Inputframe)
CarbohydrateInput = tkinter.Entry(Inputframe)
EnergyInput.grid(row=1, column=0)
ProteinInput.grid(row=1, column=1)
FatInput.grid(row=1, column=2)
CarbohydrateInput.grid(row=3,column=0)
for widget in Inputframe.winfo_children():
    widget.grid_configure(padx=10, pady=5)

# Results Frame
ResultsFrame = tkinter.LabelFrame(frame, text="Results")
ResultsFrame.grid(row=2, column=0, sticky="news", padx=20, pady=10)

# HeatMap Frame
HeatMapFrame = tkinter.LabelFrame(frame, text="HeatMap")
HeatMapFrame.grid(row=3, column=0, sticky="news", padx=20, pady=10)

button = tkinter.Button(frame, text="Enter data",command=partial(
    resultCalculator,ResultsFrame,HeatMapFrame),bg="#9AFFAA")
button.grid(row=4, column=0, sticky="news", padx=10, pady=10)

createTempObject()
window.mainloop()
