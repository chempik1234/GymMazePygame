import math
from random import randint

import pygame

from functions import quick_text, image_max_size
from hero import Hero
from sprite import load_image, CustomSprite

SCREEN_SIZE = (648, 864)
FPS = 60


class Game:
    def __init__(self, screen_size=SCREEN_SIZE, fps=FPS, hero_max_size=100):
        self.screen_size = screen_size
        pygame.init()
        pygame.display.set_caption('G-Y-M')
        self.screen = pygame.display.set_mode(self.screen_size)
        self.display = pygame.display

        self.fps = fps
        self.clock = pygame.time.Clock()

        self.background_group = pygame.sprite.Group()
        self.heroes_group = pygame.sprite.Group()
        self.pickups_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.game_mode = None

        self.win_image = pygame.transform.scale(load_image("screen.png"), self.screen_size)
        self.background_image = pygame.transform.scale(load_image("background.png"), self.screen_size)

        self.hero_max_size = hero_max_size

        self.bulat_image = image_max_size(load_image("bulat.png"), self.hero_max_size)
        self.enemy_image = image_max_size(load_image("enemy.png"), self.hero_max_size)
        self.pickup_image = image_max_size(load_image("pickup.png"), self.hero_max_size * 0.8)
        self.portal_image = image_max_size(load_image("portal.png"), self.hero_max_size * 0.8)

        self.score = None

        self.loading_screen()

        self.mixer = pygame.mixer
        self.mixer.init()
        self.music = self.mixer.Sound("sounds/music.mp3")

    def loading_screen(self):
        self.screen.blit(self.win_image, (0, 0))
        quick_text(["загрузка", "музыки..."], self.screen_size[0] // 2 - self.screen_size[0] // 3,
                   self.screen_size[1] * 2 // 3, self.screen)
        quick_text(["загрузка", "музыки..."], self.screen_size[0] // 2 - self.screen_size[0] // 3,
                   self.screen_size[1] * 2 // 3 + 5, self.screen, color=pygame.Color("white"))
        self.display.flip()

    def run(self):
        self.game_mode = 0
        running = True
        while running:
            for sprite in self.all_sprites:
                sprite.kill()
            self.all_sprites.empty()
            if self.game_mode == 0:
                self.run_gameplay()
            elif self.game_mode == 1:
                self.run_win_screen()
            elif self.game_mode == 2:
                running = False

    def run_gameplay(self):
        self.music.stop()
        self.music.play()
        running = True
        bulat = Hero(CustomSprite(self.bulat_image, (self.all_sprites, self.heroes_group),
                                  0, self.screen_size[1] - self.hero_max_size),
                     self.background_group, power=0, bounds=self.screen_size,
                     pickups_group=self.pickups_group, heroes_group=self.heroes_group)
        self.generate_walls()
        enemies = self.generate_enemies()
        pickups = self.generate_pickups()
        seconds = 0
        portal = CustomSprite(self.portal_image, (), self.screen_size[0] - self.hero_max_size * 0.9,
                              self.screen_size[1] - self.hero_max_size * 0.9)
        while running:
            seconds += self.clock.tick(self.fps) / 1000
            if not any(i.alive() for i in pickups):
                self.all_sprites.add(portal)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.game_mode = 2
                if event.type == pygame.KEYDOWN:
                    if not bulat.alive:
                        running = False
                    if event.key == pygame.K_UP:
                        bulat.set_y_acceleration(-1)
                    if event.key == pygame.K_DOWN:
                        bulat.set_y_acceleration(1)
                    if event.key == pygame.K_LEFT:
                        bulat.set_x_acceleration(-1)
                    if event.key == pygame.K_RIGHT:
                        bulat.set_x_acceleration(1)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        bulat.set_y_acceleration(0)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        bulat.set_x_acceleration(0)
            if seconds > .5:
                seconds = 0
                for enemy in enemies:
                    enemy.set_x_acceleration(randint(-1, 1))
                    enemy.set_y_acceleration(randint(-1, 1))
            # bulat.update()
            for hero_sprite in self.heroes_group:
                if not hero_sprite.parent:
                    continue
                hero_sprite.parent.update()
            self.screen.blit(self.background_image, (0, 0))
            # self.background_group.draw(self.screen)
            # self.heroes_group.draw(self.screen)
            # self.pickups_group.draw(self.screen)
            self.all_sprites.draw(self.screen)
            if pygame.sprite.collide_rect(bulat.sprite, portal):
                running = False
                self.score = bulat.power
                self.game_mode = 1
            if not bulat.alive:
                quick_text(['ВЫ ПРОИГРАЛИ!', 'ОЧКИ: ' + str(bulat.power)], 0,
                           self.screen_size[1] * 0.2, self.screen)
                quick_text(['ВЫ ПРОИГРАЛИ!', 'ОЧКИ: ' + str(bulat.power)], 0,
                           self.screen_size[1] * 0.2 - 2, self.screen, color=pygame.Color("white"))
                quick_text(["нажмите любую кнопку"], 0,
                           self.screen_size[1] * 0.2 + 130, self.screen, color=pygame.Color("white"),
                           font_size=36)

            self.display.flip()

    def run_win_screen(self):
        self.music.stop()
        self.screen.blit(self.win_image, (0, 0))
        quick_text(['ВЫ ВЫИГРАЛИ!', 'ОЧКИ: ' + str(self.score)], 0,
                   self.screen_size[1] * 0.2, self.screen)
        quick_text(['ВЫ ВЫИГРАЛИ!', 'ОЧКИ: ' + str(self.score)], 0,
                   self.screen_size[1] * 0.2 - 2, self.screen, color=pygame.Color("white"))
        quick_text(["нажмите любую кнопку"], 0,
                   self.screen_size[1] * 0.5, self.screen, color=pygame.Color("white"),
                   font_size=36)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.game_mode = 2
                if event.type == pygame.KEYDOWN:
                    running = False
                    self.game_mode = 0
            self.display.flip()

    def generate_enemies(self):
        res = []
        for i in range(4):
            hero = Hero(CustomSprite(self.enemy_image, (self.heroes_group, self.all_sprites),
                                     0, 0), self.background_group, bounds=self.screen_size, power=i + 2,
                        speed=3)
            good = False
            while not good:
                good = True
                for sprite in self.all_sprites:
                    if sprite == hero.sprite:
                        continue
                    if pygame.sprite.collide_rect(hero.sprite, sprite):
                        good = False
                        hero.sprite.rect.left = randint(0, self.screen_size[0] - hero.sprite.rect.w)
                        hero.sprite.rect.top = randint(0, self.screen_size[1] - hero.sprite.rect.h)
                        break
            res.append(hero)
        return res

    def generate_pickups(self):
        res = []
        for i in range(4):
            pickup = (CustomSprite(self.pickup_image, (self.pickups_group, self.all_sprites),
                                   0, 0))
            good = False
            while not good:
                good = True
                for sprite in self.all_sprites:
                    if sprite == pickup:
                        continue
                    if pygame.sprite.collide_rect(pickup, sprite):
                        good = False
                        pickup.rect.left = randint(0, self.screen_size[0] - pickup.rect.w)
                        pickup.rect.top = randint(0, self.screen_size[1] - pickup.rect.h)
                        break
            res.append(pickup)
        return res

    def generate_walls(self):
        walls = [
            CustomSprite(pygame.transform.scale(load_image("wall1.png"),
                                                (self.screen_size[0] * 0.15,
                                                 self.screen_size[1] * 0.05)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size, self.hero_max_size),
            CustomSprite(pygame.transform.scale(load_image("wall2.png"),
                                                (self.screen_size[0] * 0.28,
                                                 self.screen_size[1] * 0.08)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size + self.screen_size[0] * 0.15, self.hero_max_size),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.1,
                                                 self.hero_max_size * 1.5)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size, self.hero_max_size + self.screen_size[1] * 0.05),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.1,
                                                 self.screen_size[1] * 0.2)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size, self.screen_size[1] * 0.8),
            CustomSprite(pygame.transform.scale(load_image("wall1.png"),
                                                (self.screen_size[0] * 0.15,
                                                 self.screen_size[1] * 0.05)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size + self.screen_size[0] * 0.1, self.screen_size[1] * 0.8),
            CustomSprite(pygame.transform.scale(load_image("wall3.png"),
                                                (self.screen_size[0] * 0.1,
                                                 self.hero_max_size * .7)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.5, 0),
            CustomSprite(pygame.transform.scale(load_image("wall3.png"),
                                                (self.screen_size[0] * 0.1,
                                                 self.hero_max_size)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size + self.screen_size[0] * 0.25, self.screen_size[1] * 0.75),

            CustomSprite(pygame.transform.scale(load_image("wall1.png"),
                                                (self.screen_size[0] * 0.2,
                                                 self.screen_size[1] * 0.07)),
                         (self.background_group, self.all_sprites),
                         self.hero_max_size * 2.5, self.hero_max_size * 2.8),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.05,
                                                 self.screen_size[1] * 0.2)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.95 - self.hero_max_size, self.screen_size[1] * 0.8),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.05,
                                                 self.screen_size[1] * 0.2)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.95 - self.hero_max_size, self.screen_size[1] * 0.6),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.05,
                                                 self.screen_size[1] * 0.15)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.77 - self.hero_max_size, self.screen_size[1] * 0.6),
            CustomSprite(pygame.transform.scale(load_image("wall2.png"),
                                                (self.screen_size[0] * 0.2,
                                                 self.screen_size[1] * 0.1)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.8, self.hero_max_size),
            CustomSprite(pygame.transform.scale(load_image("wall2.png"),
                                                (self.screen_size[0] * 0.25,
                                                 self.screen_size[1] * 0.07)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.75 - self.hero_max_size, self.hero_max_size * 2.8),
            CustomSprite(pygame.transform.scale(load_image("wall4.png"),
                                                (self.screen_size[0] * 0.05,
                                                 self.screen_size[1] * 0.15)),
                         (self.background_group, self.all_sprites),
                         self.screen_size[0] * 0.8, self.screen_size[1] * 0.2),
        ]
        return walls


if __name__ == '__main__':
    game = Game()
    game.run()
