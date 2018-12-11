
import pygame
from chat import chat_module as ChatModule

from threading import Thread

import time

INACTIVE_COLOR = pygame.Color( 'white' )
ACTIVE_COLOR   = pygame.Color( 'gray' )
PADDING        = 5

PYGAME_SCREEN  = None
DEF_FONTSIZE   = 20

class Chat_In:

	def __init__( self, x, y, name, chat_display, 

		w         = 200, 
		text      = 'Press Enter to Chat...', 
		font_size = 30, # default value
		BUFR_SIZE = 10

		):

		self.FONT_COLOR   = pygame.Color( 'black' )

		self.player_name  = name

		self.chat_display = chat_display

		self.lobby_id     = ''


		self.chat_display.font_size = font_size

		self.chat_display.pos       = ( x, (y-font_size*2) )


		# height of text box depends on font size
		self.textBox     = pygame.Rect( x, y-font_size , w, font_size )

		self.color       = INACTIVE_COLOR

		self.message     = text

		self.font        = pygame.font.Font( None, font_size )

		self.msg_surface = self.font.render( self.message, False, self.FONT_COLOR )

		self.chat_mode   = False

	def handle_event( self, event ):

		if event.type == pygame.KEYDOWN:

			if self.chat_mode:
		
				if event.key == pygame.K_RETURN:
		
					# print( "PRINT MODE" )
					''' INTEGRATION OF TCP
					> assign text to var
					> clear input buffer
					> send message to server
					( > receiver receives mesage and prints into chat display )
					'''
					# if message not empty
					if self.message:
						
						isCommand = self.handle_command( self.message )

						if not isCommand:
							# attempt to send 
							try:
								ChatModule.send( self.message )
							
							# print the message client-side
							except:
								self.chat_display.add_to_buffer( "<{}> {}".format( self.player_name, self.message ) )

					self.message = 'Press Enter to Chat...'
					self.color     = INACTIVE_COLOR
					self.chat_mode = False


				elif event.key == pygame.K_BACKSPACE:
					self.message = self.message[ :-1 ]

				else:
					# adds incoming keypresses 
					# NOT TESTED OTHER KEYPRESSES (eg. F1-12, sys-related keys)
					self.message += event.unicode


				self.msg_surface = self.font.render( self.message, False, self.FONT_COLOR )


			else:

				if event.key == pygame.K_RETURN:

					# print( "CHAT MODE" )
					self.message = ''
					self.msg_surface = self.font.render( self.message, False, self.FONT_COLOR )

					self.color     = ACTIVE_COLOR
					self.chat_mode = True

				# ignore all other key presses
				else:
					pass

	def handle_command( self, msg ):

		'''
		> process message (if first character is a slash)
		> if "/join" command, 
			>> check number of number if valid (args == 1)
			>> if valid, initialize socket
			>> join lobby try using input arg
			>> if err, output error message
			>> else join!

		> elif in existing lobby and "/leave" command,
			>> inform server for disconnect
			>> leave lobby
			>> shutdown and quit socket
		'''
		command = msg.split()

		if command[0][0] != "/":
			return False

		else:
			if command[0] == "/create":
				if self.lobby_id:
					return False

				try:
					self.initSocket()
					_STATUS, _ID = ChatModule.createLobby( self.player_name )
					
					if _STATUS == ChatModule.SUCCESSFUL:
						self.chat_display.add_to_buffer( "<CLIENT> SUCCESSFULLY CREATED LOBBY {}!".format( _ID ) )
						self.lobby_id = _ID
						self.chat_display.thread.start()

					else:
						self.chat_display.add_to_buffer( "<CLIENT> UNKNOW ERROR OCCURRED..." )

						self.closeSocket()

				except OSError:
					self.chat_display.add_to_buffer( "<CLIENT> SERVER IS UNREACHABLE." )

				return True
			
			elif command[0] == "/join":
				try:
					self.initSocket()
					_STATUS = ChatModule.joinLobby( command[1], self.player_name )
					
					if _STATUS == ChatModule.SUCCESSFUL:
						self.chat_display.add_to_buffer( "<CLIENT> SUCCESSFULLY CONNECTED TO LOBBY {}!".format( command[1] ) )
						self.lobby_id = command[1]
						self.chat_display.thread.start()

					else:
						if _STATUS == ChatModule.UNSUCCESSFUL:
							self.chat_display.add_to_buffer( "<CLIENT> UNKNOW ERROR OCCURRED..." )

						elif _STATUS == ChatModule.LOBBY_DNE:
							self.chat_display.add_to_buffer( "<CLIENT> LOBBY DOES NOT EXIST!" )

						elif _STATUS == ChatModule.LOBBY_FULL:
							self.chat_display.add_to_buffer( "<CLIENT> LOBBY IS FULL..." )

						self.closeSocket()

				except OSError:
					self.chat_display.add_to_buffer( "<CLIENT> SERVER IS UNREACHABLE." )

				return True

			elif command[0] == "/leave":
				if self.lobby_id == '':
					self.chat_display.add_to_buffer( "<CLIENT> INVALID REQUEST" )

				else:
					self.lobby_id = ''

					ChatModule.quitLobby()
					self.closeSocket()
					
					print( "<INTERNAL> JOINING THREAD..." )
					self.chat_display.thread.join()

					print( "<INTERNAL> THREAD TERMINATED!" )

				return True

			else:
				# ignores "invalid" command; just prints it
				return False


	def initSocket( self ):
		print( "<CLIENT> INITIALIZING SOCKET..." )
		ChatModule.client_socket = ChatModule.initializeClient()

		print( "<CLIENT> ATTEMPTING SOCKET CONNECTION TO {}...".format( ChatModule.server_address ) )
		ChatModule.client_socket.connect( ChatModule.server_address )

		print( "<CLIENT> SOCKET CONNECTION SUCCESSFUL!" )
					
	def closeSocket( self ):
		print( "<CLIENT> CLOSING CONNECTION..." )
		ChatModule.client_socket.shutdown( ChatModule.Socket.SHUT_RDWR )
		ChatModule.client_socket.close()
		print( "<CLIENT> SOCKET CLOSED!" )

	def update_width( self ):

		# Resize the input box if the text is too long
		width = max( 200, self.msg_surface	.get_width() + 10 )
		self.textBox.w = width

	def draw_chat_input( self ):

		# Blit the input box
		pygame.draw.rect( PYGAME_SCREEN, self.color, self.textBox )

		# blit the text surface of the input box
		PYGAME_SCREEN.blit( 
			
			# what text surface to blit on screen
			self.msg_surface, 

			# position of text in text box
			( self.textBox.x + PADDING, self.textBox.y + PADDING )
			
			)

class Chat_Display:

	def __init__( self, font_size = 30, max_messages = 10 ):

		# chat buffer starts at upper left corner of input box
		self.pos       = ()
		
		# default value
		self.font_size   = font_size

		self.FONT_COLOR  = pygame.Color( 'white' )

		self.font        = pygame.font.Font( None, self.font_size )

		self.msg_surface = self.font.render( '', False, self.FONT_COLOR )
		

		self.running = True

		self.thread  = Thread( target = self.display_message )


		self.MAX_BUF = max_messages

		self.buffer  = []

		self.PTR     = 0


	def add_to_buffer( self, msg ):

		if len( self.buffer ) != self.MAX_BUF:
			self.buffer.append( msg )
			self.PTR += 1


		else:
			self.PTR %= self.MAX_BUF

			self.buffer[ self.PTR ] = msg

			self.PTR += 1

	def print_buffer( self ):

		time.sleep( 0.0001 )
		if len( self.buffer ) == 0:
			return

		itr = self.PTR - 1

		x_pos, y_pos = self.pos

		pos_counter  = len( self.buffer )


		if len( self.buffer ) != self.MAX_BUF:
			
			while itr >= 0:

				self.msg_surface = self.font.render( 
					self.buffer[ itr ], 
					True, 
					self.FONT_COLOR 
					)

				PYGAME_SCREEN.blit(
					self.msg_surface, 
					( x_pos + PADDING, y_pos + PADDING )
					)

				y_pos = y_pos - self.font_size

				itr -= 1

		else:
			while True:

				if (itr-1) == self.PTR or (itr+len( self.buffer )-1) == self.PTR:
					break

				self.msg_surface = self.font.render( 
					self.buffer[ itr ], 
					True, 
					self.FONT_COLOR 
					)

				PYGAME_SCREEN.blit(
					self.msg_surface, 
					( x_pos + PADDING, y_pos + PADDING )
					)

				y_pos = y_pos - self.font_size

				if (itr-1) < 0:
					itr = len( self.buffer ) - 1
				else:
					itr -= 1


	def display_message( self ):
		self.add_to_buffer( "<CLIENT> YOU HAVE JOINED THE CHAT LOBBY" )
		while self.running:
			inputs = [ ChatModule.client_socket ]

			try:
				read, _, _ = ChatModule.select.select( inputs, [], [] )
				for sock in read:
					if sock == ChatModule.client_socket:
						
						msg = ''
						try:
							msg = ChatModule.receive( sock )
							self.add_to_buffer( msg )

						except OSError:
							self.add_to_buffer( "<CLIENT> YOU HAVE LEFT THE CHAT LOBBY." )
							self.handle_close()

			except ValueError:
				self.add_to_buffer( "<CLIENT> YOU HAVE LEFT THE CHAT LOBBY." )
				self.handle_close()
		
		self.add_to_buffer( "<CLIENT> YOU HAVE DISCONNECTED FROM THE CHAT LOBBY" )

	def handle_close( self ):
		self.running = False