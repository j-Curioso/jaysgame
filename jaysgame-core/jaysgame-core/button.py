import pygame

class MyButton(pygame.sprite.Sprite):
  def __init__(self, color, height, width):
    super().__init__()
    self.image = pygame.Surface([width, height]) 
    self.image.fill((255, 0, 255))
    # self.image.set_colorkey(COLOR)

    pygame.draw.rect(self.image,color,pygame.Rect(0, 0, width, height))

    self.rect = self.image.get_rect()