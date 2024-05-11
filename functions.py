import pygame


def quick_text(text, text_coord_x, text_coord_y, screen, font_size=100, color=pygame.Color("black")):
    font = pygame.font.Font(None, font_size)
    for line_number in range(len(text)):
        line = text[line_number]
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


def image_max_size(image, max_size):
    delimiter = max(image.get_width(), image.get_height()) / max_size
    return pygame.transform.scale(image, (image.get_width() / delimiter,
                                          image.get_height() / delimiter))
