
from tkinter import *

class App:

	def __init__( self, master ):
		self.frame = Frame( master )
		self.frame.grid( rowspan=3 )
		self.initializeWidgets()

	def enterMessage( self, event ):
		msg = self.message.get()
		
		# filters out empty messages
		if msg == '':
			return

		self.displayMessage( msg )
		
		# clears message in the input via the textvariable 'message'
		self.message.set( '' )

	def displayMessage( self, msg ):
		# prints message into the chat
		self.chatMessages.insert( END, msg )

		# highlights message
		# self.chatMessages.selection_set("end")

		# focuses on the last sent message
		self.chatMessages.see( 'end' )


	def initializeWidgets( self ):

		self.chatInput = Frame( self.frame, )
		 
		self.messages_frame = Frame( self.frame )

		# variable for chat message
		self.message   = StringVar()
		self.scrollbar = Scrollbar( self.messages_frame )

		# Following will contain the messages.
		self.chatMessages = Listbox( 
			self.messages_frame, 
			height=15, 
			width=50, 
			yscrollcommand=self.scrollbar.set,
		)

		self.chatLabel = Label( self.chatInput, text="<user>" )
		self.chatField = Entry( self.chatInput, textvariable=self.message )
		self.chatField.bind( '<Return>', self.enterMessage )

		self.scrollbar.pack( side=RIGHT, fill=Y )
		self.chatMessages.pack( side=LEFT, fill=BOTH )
		self.chatMessages.pack()
		self.messages_frame.pack()
		
		self.chatInput.pack()
		self.chatLabel.pack( side=LEFT, )
		self.chatField.pack( side=RIGHT, )
		self.chatField.focus_set()


root = Tk()
root.geometry("415x300")
root.resizable(0,0)

chatWindow = App( root )

root.mainloop()
# root.destroy()