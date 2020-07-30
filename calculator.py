from tkinter import *
import tkinter as tk
from tkinter import ttk
import math

NINETY=1.64
NINETY_FIVE=1.96
NINETY_NINE=2.58
FONT = ("Arial", 11)

class App:
    def __init__(self, root, title, geometry):
        self.root = root
        self.root.title(title)
        self.root.geometry(geometry)

        self.paramOptions = ["Population Proportion (p)", "Population Mean (μ)"]
        self.parameter = self.paramOptions[0]
        
        self.confidenceLevel = tk.StringVar()
        self.confidenceLevel.set(NINETY)

        #self.inputFrame = None
        #self.outputFrame = None
        
        # Generate the 3 basic frames
        self.initUI()

    def initUI(self):
        self.generateParamFrame()
        self.generateConfidenceLevels()
        self.generateDefaultInput()
        self.generateOutputFrame()

    def generateParamFrame(self):
        # Frame to choose parameter
        paramFrame = LabelFrame(self.root, borderwidth=0, highlightthickness=0)
        paramFrame.pack()

        # Define the parameter
        paramType = Label(paramFrame, text="I want a confidence interval for the: ", font=FONT)
        paramType.grid(row=0, column=0)

        # Combobox
        self.options = ttk.Combobox(paramFrame, value=self.paramOptions, state="readonly", width=25, font=FONT)
        self.options.grid(row=0, column=1)
        self.options.current(0)
        self.options.bind("<<ComboboxSelected>>", self.generateInputFields)

    # Calculate interval
    def calculate(self):
        # Cleanup prev answer
        self.cleanupOutputFrame()
        if self.parameter == self.paramOptions[0]:
            inputs = self.parsePopulationProportionInput()
            if not inputs:
                return
            sampleProportion, sampleSize = inputs
            if sampleProportion < 0 or sampleProportion > 1 or sampleSize <= 0:
                self.invalidInput()
                return
            #print(sampleProportion, sampleSize)
            # Calculate sampleError
            error = self.computeSampleProportionError(sampleProportion, sampleSize)
            #print(error)
            result = self.computeInterval(sampleProportion, error)
            label = Label(self.outputFrame, text=str(result), font=FONT)
            label.grid(row=0, column=0)
        else:
            inputs = self.parsePopulationMeanInput()
            if not inputs:
                return
            sampleMean, sampleSize, sampleStdDev = inputs
            if sampleSize < 0 or sampleStdDev < 0:
                self.invalidInput()
                return
            error = self.computeSampleMeanError(sampleStdDev, sampleSize)
            result = self.computeInterval(sampleMean, error)
            label = Label(self.outputFrame, text=str(result), font=FONT)
            label.grid(row=0, column=0)
    
    def cleanupOutputFrame(self):
        #print('inside cleanupOutputFrame')
        for widget in self.outputFrame.winfo_children():
            widget.destroy()
    

    def generateProportionInput(self):
        sampleProportion = Label(self.inputFrame, text="Sample Proportion (p-hat):", font=FONT)
        sampleProportion.grid(row=0, column=0)
        sampleSize = Label(self.inputFrame, text="Sample Size (n):", font=FONT)
        sampleSize.grid(row=1, column=0)
        calculateButton = Button(self.inputFrame, text="Calculate", command=self.calculate, font=FONT)
        calculateButton.grid(row=2, column=0)

        # Entry Widgets
        self.enterSampleProportion = Entry(self.inputFrame, width=10)
        self.enterSampleProportion.grid(row=0, column=1)
        self.enterSampleSize = Entry(self.inputFrame, width=10)
        self.enterSampleSize.grid(row=1, column=1)
    
    def generateMeanInput(self):
        sampleProportion = Label(self.inputFrame, text="Sample Mean (x-bar):", font=FONT)
        sampleProportion.grid(row=0, column=0)
        sampleSize = Label(self.inputFrame, text="Sample Size (n):", font=FONT)
        sampleSize.grid(row=1, column=0)
        populationStdDev = Label(self.inputFrame, text="Population Std Dev (σ):", font=FONT)
        populationStdDev.grid(row=2, column=0)
        calculateButton = Button(self.inputFrame, text="Calculate", command=self.calculate, font=FONT)
        calculateButton.grid(row=3, column=0)
        
        # Entry Widgets
        self.enterSampleMean = Entry(self.inputFrame, width=10)
        self.enterSampleMean.grid(row=0, column=1)
        self.enterSampleSize = Entry(self.inputFrame, width=10)
        self.enterSampleSize.grid(row=1, column=1)
        self.enterPopulationStdDev = Entry(self.inputFrame, width=10)
        self.enterPopulationStdDev.grid(row=2, column=1)

       
    def generateDefaultInput(self):
        self.inputFrame = LabelFrame(self.root, borderwidth=0, highlightthickness=0)
        self.inputFrame.pack()
        self.generateProportionInput()
        #for widget in self.inputFrame.winfo_children():
            #print(widget['text'])

    def generateOutputFrame(self):
        self.outputFrame = LabelFrame(self.root, border=0, highlightthickness=0)
        self.outputFrame.pack()

    def cleanupInputFrame(self):
        for widget in self.inputFrame.winfo_children():
            widget.destroy()
        
    def generateInputFields(self, event):
        self.cleanupInputFrame()
        self.parameter = self.options.get()    
        # New frame for inputs
        if self.parameter == self.paramOptions[0]:
            self.generateProportionInput()
        else:
            self.generateMeanInput()
        self.cleanupOutputFrame()

    def generateConfidenceLevels(self):
        # Frame or confidence level
        confidenceLevelFrame = LabelFrame(self.root, borderwidth=0, highlightthickness=0)
        confidenceLevelFrame.pack()

        # Define the confidence level
        confidencePrompt = Label(confidenceLevelFrame, text="With a confidence level of: ", font=FONT)
        confidencePrompt.grid(row=0, column=0)

        rbOne = Radiobutton(confidenceLevelFrame, variable=self.confidenceLevel, value=NINETY, text="90%", font=FONT)
        rbTwo = Radiobutton(confidenceLevelFrame, variable=self.confidenceLevel, value=NINETY_FIVE, text="95%", font=FONT)
        rbThree = Radiobutton(confidenceLevelFrame, variable=self.confidenceLevel, value=NINETY_NINE, text="99%", font=FONT)

        rbOne.grid(row=0, column=1)
        rbTwo.grid(row=0, column=2)
        rbThree.grid(row=0, column=3)

    def invalidInput(self):
        # Paste a invalid input label
        label = Label(self.outputFrame, text="Invalid input", font=FONT)
        label.grid(row=0, column=0)
        
    # Validate Input
    def parsePopulationProportionInput(self):
        # Pull the inputs -- both are strings
        sampleProportion = self.enterSampleProportion.get()
        sampleSize = self.enterSampleSize.get()
        try:
            sampleProportion = float(sampleProportion)
            sampleSize = int(sampleSize)
            return (sampleProportion, sampleSize)
        except ValueError:
            self.invalidInput()

    def parsePopulationMeanInput(self):
        # Pull all inputs
        sampleMean = self.enterSampleMean.get()
        sampleSize = self.enterSampleSize.get()
        populationStdDev = self.enterPopulationStdDev.get()
        try:
            sampleMean = float(sampleMean)
            sampleSize = int(sampleSize)
            populationStdDev = float(populationStdDev)
            return (sampleMean, sampleSize, populationStdDev)
        except ValueError:
            self.invalidInput()
            
    # Computations
    def computeSampleProportionError(self, sampleProportion, sampleSize):
        return float(self.confidenceLevel.get()) * math.sqrt((sampleProportion * (1 - sampleProportion)) / sampleSize)

    def computeSampleMeanError(self, populationStdDev, sampleSize):
        return float(self.confidenceLevel.get()) * (populationStdDev / math.sqrt(sampleSize))
    
    def computeInterval(self, val, error):
        lower = val - error
        upper = val + error
        return (lower, upper)        
        
    
def main():
    root = Tk()
    app = App(root, "Confidence Interval Calculator", "500x200")
    return

main()
