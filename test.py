
import pygame
import chat_box

input_name = input( "Enter name: " )

pygame.init()

screen = pygame.display.set_mode((500,500),pygame.HWSURFACE)
clock  = pygame.time.Clock()
w, h   = pygame.display.get_surface().get_size()

# for client box gui update
chat_box.PYGAME_SCREEN = screen

chat_display = chat_box.Chat_Display( font_size = chat_box.DEF_FONTSIZE )

chat_input   = chat_box.Chat_In( 0, h, input_name, chat_display, font_size = chat_box.DEF_FONTSIZE )

running      = True

while running:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
				break
			else:
				chat_input.handle_event( event )

	screen.fill( (255,255,255) )

	chat_input.update_width()
	chat_input.draw_chat_input()
	chat_display.print_buffer()
							
	pygame.display.flip()