import pygame
import config

pygame.init()

class JaysGame:
  def __init__(self, screen):
    self.screen = screen
    self.running = True
    self.FPS = pygame.time.Clock()
    self.Paused = False

  def main(self, window_width, window_height):
    while self.running:
      self.handle_events()

  def handle_events(self):
    for self.event in pygame.event.get():
      if self.event.type == pygame.QUIT:
        self.running = False
      if self.event.type == pygame.MOUSEBUTTONDOWN:
        self.handle_click(self.event)

if __name__ == "__main__":
  screen = pygame.display.set_mode(config.window_size)
  pygame.display.set_caption("Jays Game")
  game = JaysGame(screen)
  game.main(config.window_width, config.window_height)