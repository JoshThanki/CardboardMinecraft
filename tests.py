import pygame

# Initialize pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Create a player character as a rectangle
player_rect = pygame.Rect(400, 500, 50, 50)

# Create a platform as a rectangle
platform_rect = pygame.Rect(300, 550, 200, 50)

# Set up the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move the player based on user input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player_rect.x += 5

    # Make the player fall
    player_rect.y += 5

    # Check for collision with the platform
    if player_rect.colliderect(platform_rect):
        player_rect.y = platform_rect.top - player_rect.height

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the player and platform
    pygame.draw.rect(screen, (255, 0, 0), player_rect)
    pygame.draw.rect(screen, (0, 255, 0), platform_rect)

    # Update the display
    pygame.display.flip()

# Clean up and exit
pygame.quit()
