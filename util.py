from tkinter     import *
from tkinter.ttk import *

class Slider:
	'''Good for setting bounded floating point variables'''
	def __init__(self, master, initvalue=1, minval=0, maxval=10, label=''):
		self.master= master
		self.value=       DoubleVar(value=initvalue)
		self.frame=       Frame(self.master)#frame to contain element parts
		self.label_name=  Label(self.frame, justify=LEFT,  text=label)
		self.label_value= Label(self.frame, justify=RIGHT, text=f'{self.value.get():.3f}')
		self.slider=      Scale(self.frame, from_=minval, to=maxval, orient='horizontal', variable=self.value)
		self.slider.bind('<B1-Motion>', lambda e: self.label_value.config(text=f'{self.value.get():.3f}'))

	def pack(self):
		'''packs and renders UI element'''
		self.frame.pack(anchor=E, fill=X)
		self.label_name.pack(side=LEFT, anchor=E, fill=X)
		self.label_value.pack(side=RIGHT, anchor=W, fill=X)
		self.slider.pack(side=RIGHT)
		# self.slider.pack(side=RIGHT, fill=BOTH, expand=1)
	
	def pack_forget(self):
		'''hides UI element'''
		self.frame.pack_forget()
		self.label_name.pack_forget()
		self.label_value.pack_forget()
		self.slider.pack_forget()
		# self.slider.pack_forget()


	def get(self):
		return self.value.get()

class IntEntry:
	'''A Textbox that strictly takes positive integers as input'''
	def __init__(self, master, initvalue=1, label='', includes_buttons=True, width=5):
		self.master=            master
		self.value=             initvalue if initvalue>=1 else 1
		self._includes_buttons= includes_buttons

		self.frame=   Frame(self.master)#frame to hold the entry and buttons
		self.label=   Label(self.frame, text=label, justify=LEFT)
		self.entry=   Entry(self.frame, textvariable=str(initvalue), width=width)
		if includes_buttons:
			self.btn_up= Button(self.frame, width=4, text='▲', command=self.increment)
			self.btn_dn= Button(self.frame, width=4, text='▼', command=self.decrement)
		self.entry.insert(0, str(self.value))

		# Bind the entry widget to validate input
		self.entry.bind('<FocusOut>',   self._update_value)#update value when textbox out of focus
		self.entry.bind('<MouseWheel>', self._mouse_wheel)

	def pack(self):
		'''packs and renders UI element'''
		self.frame.pack(anchor=E, fill=X)
		self.label.pack(side=LEFT, anchor=W, fill=X)
		if self._includes_buttons:
			self.btn_dn.pack(side=RIGHT, anchor=N)
			self.btn_up.pack(side=RIGHT, anchor=S)
		self.entry.pack(side=RIGHT)
		# self.label.grid(row=0,  column=0)
		# self.entry.grid(row=0,  column=1)
		# self.btn_up.grid(row=0, column=2)
		# self.btn_dn.grid(row=0, column=3)

	def pack_forget(self):
		'''hides UI element'''
		self.frame.pack_forget()
		self.label.pack_forget()
		if self._includes_buttons:
			self.btn_dn.pack_forget()
			self.btn_up.pack_forget()
		self.entry.pack_forget()

	def get(self):
		'''Get current textbox value'''
		return self.value
	
	def set(self, value:int):
		self.value= value
	
	def increment(self):
		'''Increment the value and update the entry.'''
		self.value+= 1
		self._update_entry()

	def decrement(self):
		'''Decrement the value and update the entry.'''
		if self.value>1:
			self.value-= 1
			self._update_entry()
	
	def _update_entry(self):
		'''Update the entry widget with the current value.'''
		self.entry.delete(0, END)
		self.entry.insert(0, str(self.value))

	def _update_value(self, event):
		'''Update the value from the entry widget.'''
		text= self.entry.get()
		if text.isdigit():
			if int(text)>0:
				self.value= int(text)
		self._update_entry()

	def _mouse_wheel(self, event):
		'''Handle mouse wheel scrolling to increment or decrement the value.'''
		if event.delta>0: self.increment()#Scroll up
		else:             self.decrement()#Scroll down
