
from tkinter import *
import chat_module as ChatModule
from threading import Thread

class App:

	def __init__( self ):
		self.root = Tk()
		self.root.geometry( "415x500" )
		self.root.resizable( 0,0 )

		self.root.protocol()

		self.frame = Frame( self.root )
		self.frame.pack()
		self.initialize_join_widgets()
		self.initialize_chat_widgets()

		self.root.mainloop()

	def initialize_join_widgets( self ):

		join_frame = Frame( self.frame )

		self.name   = StringVar()
		self.id     = StringVar()
		self.status = StringVar()
		#############################
		self.username   = Label( 
			join_frame, 
			text = "Name",
			)
		self.lobbyid     = Label( 
			join_frame, 
			text = "Lobby ID",
			)
		self.name_input  = Entry( 
			join_frame, 
			textvariable = self.name,
			)
		self.id_input    = Entry( 
			join_frame, 
			textvariable = self.id,
			)
		self.statusLabel = Label( 
			join_frame,
			textvariable = self.status
			)
		self.connect     = Button( 
			join_frame, 
			text = "Connect", 
			command = self.attemptConnection,
			)
		self.create     = Button( 
			join_frame, 
			text = "Create Lobby",
			command = self.createAndConnect,
			)
		#############################

		#############################
		self.username.grid(
			row = 0,
			column = 0,
			)
		self.name_input.grid( 
			row = 0,
			column = 1,
			)
		self.lobbyid.grid( 
			row = 1,
			column = 0,
			)
		self.id_input.grid( 
			row = 1,
			column = 1,
			)
		self.statusLabel.grid(
			row = 2,
			column = 1,
			)
		self.connect.grid(
			row = 3,
			column = 0,
			)
		self.create.grid(
			row = 3,
			column = 1,
			)

		self.name_input.focus_set()
		join_frame.pack()

	def initialize_chat_widgets( self ):

		self.curr_id = StringVar()

		self.messages_frame = Frame( self.frame )
		self.chatInput      = Frame( self.frame, )

		self.spacer         = Label( 
			self.frame, 
			text = "",
			)
		self.lobbyIdLabel   = Label( 
			self.frame, 
			textvariable = self.curr_id,
			)
		
		# variable for chat message
		self.message   = StringVar()
		self.scrollbar = Scrollbar( self.messages_frame )

		# Following will contain the messages.
		self.chatMessages = Listbox( 
			self.messages_frame, 
			height = 15, 
			width  = 50, 
			yscrollcommand=self.scrollbar.set,
			state = 'disabled',	
			)

		self.chatLabel = Label( 
			self.chatInput, 
			text="<user>",
			)

		self.chatField = Entry( 
			self.chatInput, 
			textvariable = self.message,
			state = 'disabled',
			)

		self.chatField.bind( 
			'<Return>', 
			self.enterMessage, 
			)

		self.leave = Button( 
			self.frame, 
			text = "Leave Lobby",
			command = self.leaveLobby,
			state = 'disabled',
			)

		self.scrollbar.pack( 
			side = RIGHT, 
			fill = Y,
			)

		self.chatMessages.pack( 
			side = LEFT, 
			fill = BOTH, 
			)

		self.spacer.pack()
		self.lobbyIdLabel.pack()

		self.messages_frame.pack()
		self.chatMessages.pack()
		
		self.chatInput.pack()
		self.chatLabel.pack( side=LEFT, )

		self.chatField.pack( side=RIGHT, )

		self.leave.pack()


	def enterMessage( self, event ):
		msg = self.message.get()
		
		# filters out empty messages
		if msg == '':
			return

		else:
			# clears message in the input via the textvariable 'message'
			ChatModule.send( msg )
			self.message.set( '' )

	def displayMessage( self ):
		while not ChatModule.IS_DISCONNECTED:
			inputs = [ ChatModule.client_socket ]

			try:
				read, write, err = ChatModule.select.select( inputs, [], [], 1 )

				for sock in read:
					# input came from server
					if sock == ChatModule.client_socket: 
							msg = ''
							try:
								msg = ChatModule.receive( sock )

								# prints message into the chat
								self.chatMessages.insert( END, msg )

								# focuses on the last sent message
								self.chatMessages.see( 'end' )
							except OSError:
								return

			except ValueError:
				return


				# input came from client
				# else:
				# 	send(message)

	def attemptConnection( self ):
		if self.name.get() == '' or self.id.get() == '':
			self.status.set( "Fill in the missing details" )

		else:
			self.status.set( "Joining..." )

			try:
				ChatModule.client_socket = ChatModule.initializeClient()
				ChatModule.client_socket.connect( ChatModule.server_address )
				_STATUS = ChatModule.joinLobby( self.id.get(), self.name.get() )

				if _STATUS == ChatModule.SUCCESSFUL:
					self.curr_id.set( "Lobby {}".format( self.id.get() ) )

					self.switch_chat_state_widgets()

					self.chatMessages.insert( 
						END, 
						"Successfully connected to Lobby {} ".format( self.id.get() ),
						)

					self.display_thread = Thread( target = self.displayMessage )
					self.display_thread.start()

			except OSError:
				self.status.set( "Server is unreachable." )
				self.id.set( '' )

	def createAndConnect( self ):
		if self.name.get() == '':
			self.status.set( "Enter your user name" )

		else:
			self.status.set( "Creating Lobby..." )
			try:
				ChatModule.client_socket = ChatModule.initializeClient()
				ChatModule.client_socket.connect( ChatModule.server_address )
				_STATUS, _ID = ChatModule.createLobby( self.name.get() )
				if _STATUS == ChatModule.SUCCESSFUL:
					self.curr_id.set( "Lobby {}".format( _ID ) )

					self.switch_chat_state_widgets()

				self.chatMessages.insert( 
					END, 
					"Successfully connected to Lobby {} ".format( _ID ),
					)

				self.display_thread = Thread( target = self.displayMessage )
				self.display_thread.start()

			except OSError:
				self.status.set( "Server is unreachable." )
				self.id.set( '' )

	def leaveLobby( self ):
		ChatModule.quitLobby()
		ChatModule.client_socket.shutdown( ChatModule.Socket.SHUT_RDWR )
		ChatModule.client_socket.close()

		self.switch_join_state_widgets()

		self.curr_id.set( 'Leaving lobby...' )
		self.status.set( '' )

		# print( "joining" )
		self.display_thread.join()
		self.curr_id.set( '' )

	def switch_join_state_widgets( self ):
		self.chatMessages.config( state = 'disabled' )
		self.chatField.config( state = 'disabled' )
		self.leave.config( state = 'disabled' )

		self.id_input.config( state = 'normal' )
		self.connect.config( state = 'normal' )
		self.create.config( state = 'normal' )

	def switch_chat_state_widgets( self ):
		self.name_input.config( state = 'disabled' )
		self.id_input.config( state = 'disabled' )
		self.connect.config( state = 'disabled' )
		self.create.config( state = 'disabled' )

		self.chatMessages.config( state = 'normal' )
		self.chatField.config( state = 'normal' )
		self.leave.config( state = 'normal' )

	def nothing( self ):
		pass


def main():
	app = App()

if __name__ == "__main__":
	main()