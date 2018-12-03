
import pygame

INACTIVE_COLOR = pygame.Color( 'white' )
ACTIVE_COLOR   = pygame.Color( 'gray' )
PADDING        = 5

class Chat_In:

	def __init__( self, x, y, w = 200, text = 'Press Enter to Chat...', font_size = 30 ):

		self.FONT_COLOR  = pygame.Color( 'black' )

		# height of text box depends on font size
		self.textBox     = pygame.Rect( x, y-font_size , w, font_size )

		self.color       = INACTIVE_COLOR

		self.message     = text

		self.font        = pygame.font.Font( None, font_size )

		self.msg_surface = self.font.render( self.message, True, self.FONT_COLOR )

		self.chat_mode   = False

	def handle_event( self, event ):

		if event.type == pygame.KEYDOWN:

			if self.chat_mode:
		
				if event.key == pygame.K_RETURN:
		
					print( "PRINT MODE" )
					''' INTEGRATION OF TCP
					> assign text to var
					> clear input buffer
					> send message to server
					( > receiver receives mesage and prints into chat display )
					'''
					# if message not empty
					if self.message:
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
						print( "Message >> {}".format( self.message ) )
						self.message = 'Press Enter to Chat...'

					self.color     = INACTIVE_COLOR
					self.chat_mode = False


				elif event.key == pygame.K_BACKSPACE:
					self.message = self.message[ :-1 ]


				else:
					# adds incoming keypresses 
					# NOT TESTED OTHER KEYPRESSES (eg. F1-12, sys-related keys)
					self.message += event.unicode


				self.msg_surface = self.font.render( self.message, True, self.FONT_COLOR )


			else:

				if event.key == pygame.K_RETURN:

					print( "CHAT MODE" )
					self.message = ''
					self.msg_surface = self.font.render( self.message, True, self.FONT_COLOR )

					self.color     = ACTIVE_COLOR
					self.chat_mode = True

				# ignore all other key presses
				else:
					pass


	def update_width( self ):

		# Resize the input box if the text is too long
		width = max( 200, self.msg_surface.get_width() + 10 )
		self.textBox.w = width

	def draw_chat_input( self, screen ):

		# Blit the input box
		pygame.draw.rect( screen, self.color, self.textBox )

		# blit the text surface of the input box
		screen.blit( 
			
			# what text surface to blit on screen
			self.msg_surface, 

			# position of text in text box
			( self.textBox.x + PADDING, self.textBox.y + PADDING )
			
			)

class Chat_Display:

	def __init__( self ):
		pass
