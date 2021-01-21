"""Cell point annotation tools.

Author: Hongxiao Li.

Email: hongxiao-li@outlook.com"""


import tkinter as tk
import platform
import os
from pathlib import Path
from math import ceil

import matplotlib.pyplot as plt
from cv2 import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

import utils


PLATFORM = platform.system().upper()
ROOTDIR = os.path.abspath('./')
CELLCLASSFILE = os.path.join(ROOTDIR, 'cell_class_type.csv')


class App(object):
	def __init__(self):
		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
		# Framework
		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

		self.root = tk.Tk()
		self.root.geometry("1200x800")
		self.rootPanel = tk.Frame(self.root)
		self.rootPanel.pack(side="bottom", fill="both", expand="yes")

		self.imgPanel = tk.Frame(self.rootPanel, height=700)
		self.imgPanel.pack(side="top", fill="both", expand="yes")

		self.btnPanel = tk.Frame(self.rootPanel, height=100)
		self.btnPanel.pack(side='bottom', fill="both", expand="yes")

		self.clsPanel = tk.Frame(self.btnPanel, width=1000)
		self.clsPanel.pack(side='left', fill="both", expand="yes")

		self.ctrlPanel2 = tk.Frame(self.btnPanel, width=100)
		self.ctrlPanel2.pack(side='right', fill="both", expand="yes")

		self.ctrlPanel1 = tk.Frame(self.btnPanel, width=100)
		self.ctrlPanel1.pack(side='right', fill="both", expand="yes")

		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
		# Button
		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

		self.cellCount = ""
		self.labCellCountStrVar = tk.StringVar()
		self.set_cell_count_label()
		self.labCellCount = tk.Label(self.ctrlPanel1, textvariable=self.labCellCountStrVar, bg='yellow', width=20)
		self.labCellCount.grid(sticky='w', row=0, column=0, padx=3, pady=7)

		self.btnSelNext = tk.Button(self.ctrlPanel1, text="Select & Next", command=self.update_selection)
		self.btnSelNext.grid(sticky='w', row=2, column=0, padx=3, pady=14)

		self.btnOpen = tk.Button(self.ctrlPanel2, text="Open Image", command=self.open_image)
		self.btnOpen.grid(sticky='w', row=0, column=0, padx=3, pady=7)

		self.btnSave = tk.Button(self.ctrlPanel2, text="Save", command=self.save_ann)
		self.btnSave.grid(sticky='w', row=1, column=0, padx=3, pady=7)

		self.btnQuit = tk.Button(self.ctrlPanel2, text="Quit", command=self.quit)
		self.btnQuit.grid(sticky='w', row=2, column=0, padx=3, pady=7)

		self.clsStrVar = tk.StringVar()
		dfCls = pd.read_csv(CELLCLASSFILE)
		nCols = 3
		nRows = ceil(len(dfCls)/nCols)
		for i in range(nRows):
			for j in range(nCols):
				ind = i*nCols + j
				if ind>=len(dfCls):
					break
				options = {
					"text": dfCls.at[ind, 'ClassName'],
					"variable": self.clsStrVar,
					"value": dfCls.at[ind, 'ClassValue']
				}
				tk.Radiobutton(self.clsPanel, **options).grid(sticky='w', row=i, column=j)

		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
		# Figure
		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

		self.imgName = ""
		self.labImgNameStrVar = tk.StringVar()
		self.set_img_name_label()
		self.labImgName = tk.Label(self.imgPanel, textvariable=self.labImgNameStrVar, width=30)
		self.labImgName.pack(side='top', padx=3, pady=7)

		self.fig = Figure()
		ax = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.imgPanel)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
		self.canvas._tkcanvas.pack(side="top", fill="both", expand=1)

		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
		# Other properties
		#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

		if PLATFORM=='WINDOWS':
			self.initialDir = ROOTDIR
		else:
			self.initialDir = ROOTDIR
		self.imgFile = ''
		self.coordsFile = ''
		self.dfCoords = []  # DataFrame of coordinates
		self.coords = []    # generator of coordinates
		self.cellNum = 0
		self.popedNum = 0
		self.X = 0
		self.Y = 0
		self.imgBGR = None
		self.table = []
		self.annFile = ''
		self.reachEnd = False
		self.imageOK = False
		self.annOK = False

		self.root.title("Cell Center Annotator")
		self.clsStrVar.set('others')
		self.switch()
		self.root.mainloop()

	def clear_fig(self):
		self.fig.clf()
		self.canvas.draw()

	def re_init(self):
		self.cellCount = ""
		self.coordsFile = ''
		self.dfCoords = []  # DataFrame of coordinates
		self.coords = []    # generator of coordinates
		self.cellNum = 0
		self.popedNum = 0
		self.X = 0
		self.Y = 0
		self.imgBGR = None
		self.table = []
		self.annFile = ''
		self.reachEnd = False
		self.imageOK = False
		self.annOK = False
		self.clsStrVar.set('others')
		self.clear_fig()
		self.set_cell_count_label()
		self.set_img_name_label()

	def switch(self):
		if self.imageOK and self.annOK:
			self.btnSelNext['state'] = 'normal'
		else:
			self.btnSelNext['state'] = 'disabled'
		if self.reachEnd:
			self.btnSave['state'] = 'normal'
		else:
			self.btnSave['state'] = 'disabled'

	def set_cell_count_label(self):
		self.labCellCountStrVar.set(f"Cell count: {self.cellCount:10}")

	def set_img_name_label(self):
		self.labImgNameStrVar.set(self.imgName)

	def update_selection(self):
		"""Update the table and the figure."""
		value = self.clsStrVar.get()
		if value=='':
			tk.messagebox.showerror(
				"Value Error",
				"Must select a class type to continue."
			)
		elif self.reachEnd:
			tk.messagebox.showwarning(
				"Warning",
				"Have completed the annotation of the last available cell.\n"
				"Please save the annotations."
			)
		else:
			self.table.append(value)
			try:
				self.update_fig()
			except StopIteration:
				self.reachEnd = True
				tk.messagebox.showwarning(
					"Warning",
					"Have completed the annotation of the last available cell.\n"
					"Please save the annotations."
				)
			finally:
				self.switch()
		# print(self.clsStrVar.get())

	def save_ann(self):
		"""Save the annotation."""
		name = Path(self.coordsFile).name
		self.annFile = os.path.join(ROOTDIR, 'res', name)
		utils.make_sure_dir_exist(str(Path(self.annFile).parent))
		if len(self.table)!=len(self.dfCoords):
			tk.messagebox.showerror(
				"Value Error",
				"Must complete all the available cells' annotation before saving the annotation."
			)
		else:
			df = self.dfCoords.copy()
			df.insert(len(df.columns), 'Class', self.table)
			df.to_csv(self.annFile, index=False)
			tk.messagebox.showinfo(
				"Save",
				f"Successfully save file\n{self.annFile}"
			)

	def open_image(self):
		"""Open the figure."""
		self.re_init()
		self.imgFile = tk.filedialog.askopenfile(
			initialdir=self.initialDir, 
			title="Select file", 
			filetypes=(
				("png files", "*.png"),
				("jpeg files", "*.jpg"),
				("all files", "*.*")
			)
		).name
		self.imgName = Path(self.imgFile).name
		# print(self.imgFile)
		try:
			self.imgBGR = cv2.imread(self.imgFile)
		except:
			tk.messagebox.showerror(
				"Open file",
				f"Cannot open this file\n{self.imgFile}"
			)
		else:
			self.imageOK = True
			try:
				self.coords = self.read_coords()
			except:
				raise Exception("Failed to read coordinates.")
			else:
				self.set_img_name_label()
				self.update_fig()
		finally:
			self.switch()

	def read_coords(self):
		"""Read the coordinates."""
		if self.imgFile!='':
			self.coordsFile = str(Path(self.imgFile).with_suffix('.csv'))
		else:
			tk.messagebox.showerror(
				"",
				"Select image file first"
			)
		try:
			self.dfCoords = pd.read_csv(self.coordsFile)
		except:
			tk.messagebox.showerror(
				"Open file",
				f"Cannot open the coordinates file\n{self.coordsFile}"
			)
			raise Exception(f"Cannot open the coordinates file\n{self.coordsFile}")
		else:
			if len(self.dfCoords)==0:
				tk.messagebox.showerror(
					"Open file",
					f"There is no nuclei coordinates.\nPlease pass to the next file."
				)
			else:
				self.annOK = True
				self.cellNum = len(self.dfCoords)
				ind = 0
				while ind<len(self.dfCoords):
					yield tuple(self.dfCoords.loc[ind])
					ind += 1

	def update_fig(self):
		"""Update the figure display."""
		self.X, self.Y = next(self.coords)
		self.X, self.Y = int(self.X), int(self.Y)
		self.popedNum += 1
		imgBGRCopy = self.imgBGR.copy()
		cv2.circle(imgBGRCopy, (self.X, self.Y), radius=30, color=(0, 255, 0), thickness=2)
		cv2.circle(imgBGRCopy, (self.X, self.Y), radius=2, color=(0,255,0), thickness=-1)
		imgRGB = cv2.cvtColor(imgBGRCopy, cv2.COLOR_BGR2RGB)
		self.fig.clf()
		ax = self.fig.add_subplot(111)
		ax.imshow(imgRGB)
		# ax.set_axis_off()
		self.canvas.draw()
		self.cellCount = f"{self.popedNum}/{self.cellNum}"
		self.set_cell_count_label()
		self.root.update()

	def quit(self):
		self.root.destroy()


if __name__ == "__main__":
	app = App()












