import pygame
from os.path import join
from os import getcwd


def get_path(*path: str) -> str:
    return join(getcwd(), "assets", *path)


texture_storage: dict[str, pygame.Surface] = {}
text_storage: dict[str, pygame.Surface] = {}


def get_texture(path: str) -> pygame.Surface:
    if path not in texture_storage:
        texture_storage[path] = pygame.image.load(path)
    return texture_storage[path]


def fetch_text(font: pygame.font.Font, text: str) -> pygame.Surface:
    if text not in text_storage:
        text_storage[text] = font.render(text, True, (0, 0, 0))
    return text_storage[text]
