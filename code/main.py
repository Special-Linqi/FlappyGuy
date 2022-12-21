import pygame, sys, time
from settings import *
from sprites import BackGround, Ground, Plane, Obstacle, Prop
from button import Button


class Game:
    def __init__(self):

        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Guy")
        self.clock = pygame.time.Clock()
        self.active = True

        # sprites groups
        self.all_sprites = pygame.sprite.Group()
        self.obs_grp = pygame.sprite.Group()
        self.prop_grp = pygame.sprite.Group()

        # scale_factor
        self.scale_factor = 0.8

        # sprite setup
        BackGround(self.all_sprites)
        Ground(self.all_sprites, self.scale_factor)
        self.plane = Plane(self.all_sprites, self.scale_factor * 2)
        # self.prop = Prop(self.all_sprites,self.scale_factor)
        self.obstacle = Obstacle([self.all_sprites, self.obs_grp], self.scale_factor * 1.2)
        self.prop = Prop([self.all_sprites, self.prop_grp], self.scale_factor * 1.3)
        replay_img = pygame.image.load('FlappyBirds/graphics/buttons/replay.png').convert_alpha()
        self.replay_button = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.7, replay_img, 4)

        # timer
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)
        self.prop_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.prop_timer, 11000)  # 11200

        # timer

        # text
        self.font = pygame.font.Font('FlappyBirds/graphics/font/BD_Cartoon_Shout.ttf', 50)
        self.score = 0
        self.start_offset = 0

        # menu
        self.menu_surf = pygame.image.load('FlappyBirds/graphics/buttons/menu.png').convert_alpha()
        # self.menu_surf = pygame.transform.scale(self.menu_surf, pygame.math.Vector2(self.menu_surf.get_size()) * 1.8)
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # music
        self.music = pygame.mixer.Sound('FlappyBirds/music/piano1.wav')
        self.music.play(loops=-1)

        # prop
        self.immortal = False
        self.immortal_start = 0
        self.poison = False
        self.poison_start = 0

        self.count_start = 0


    def collisions(self):
        if pygame.sprite.spritecollide(self.plane, self.obs_grp, False, pygame.sprite.collide_mask) \
                or self.plane.rect.top <= 0 or self.plane.rect.bottom >= 470:
            for sprite in self.obs_grp.sprites():
                # print(sprite.sprite_type)
                if sprite.sprite_type == 'obstacle':
                    self.active = False
                    self.plane.kill()
                    sprite.kill()
                    for prop_sprite in self.prop_grp:
                        prop_sprite.kill()


        if pygame.sprite.spritecollide(self.plane, self.prop_grp, False, pygame.sprite.collide_mask):

            # for prop in self.prop_grp.sprites():
            prop = self.prop_grp.sprites()[0]
            if prop.sprite_type == 'prop':
                # print("===========333============")
                prop.kill()
                if prop.prop == "poison":
                    # self.poison_sound.set_volume(0.8)
                    if self.poison == False:
                        self.poison_sound = pygame.mixer.Sound('FlappyBirds/music/prop1.wav')
                        self.poison = True
                        self.poison_start = pygame.time.get_ticks()
                        self.poison_sound.play()
                        self.count_start = self.poison_start // 1000

                elif prop.prop == "magic_potion":
                    self.magic_potion = pygame.mixer.Sound('FlappyBirds/music/prop2.wav')
                    self.magic_potion.set_volume(0.8)
                    self.magic_potion.play()
                    self.immortal = True
                    self.immortal_start = pygame.time.get_ticks()
                    self.count_start = self.immortal_start // 1000
                    # print("self.immortal_start",self.immortal_start)

            # self.plane.kill()

    def display_score(self, game_end=False):
        if self.active:
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
        y = WINDOW_HEIGHT / 10
        # else:
        # y = WINDOW_HEIGHT / 2 + (self.menu_rect.height / 1.5)

        score_surf = self.font.render(str(self.score), True, 'brown')
        if game_end == True:
            self.font = pygame.font.Font('FlappyBirds/graphics/font/BD_Cartoon_Shout.ttf', 60)
            score_surf = self.font.render(str(self.score), True, 'brown')
            score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y * 4.7))
            self.replay_button.show(self.display_surface)

        else:
            score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def countdown(self, limit):
        y = WINDOW_HEIGHT / 10
        current_time = pygame.time.get_ticks() // 1000
        count = limit - (current_time - self.count_start)
        count_font = pygame.font.Font('FlappyBirds/graphics/font/BD_Cartoon_Shout.ttf', 100)
        count_surf = count_font.render(str(count), True, 'white')
        count_surf.set_alpha(100)
        count_rect = count_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y * 5))
        self.display_surface.blit(count_surf, count_rect)

    def run(self):
        last_time = time.time()
        while True:

            delta_time = time.time() - last_time
            last_time = time.time()

            # event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # keys = pygame.key.get_pressed()
                # if keys[pygame.K_SPACE]:
                if event.type == pygame.KEYDOWN:
                    if pygame.K_SPACE:
                        if self.active:
                            self.plane.jump()
                        # else:
                        #     self.plane = Plane(self.all_sprites, self.scale_factor * 2)
                        #     self.active = True
                        #     self.start_offset = pygame.time.get_ticks()

                if event.type == self.obstacle_timer and self.active:
                    self.obstacle = Obstacle([self.all_sprites, self.obs_grp], self.scale_factor * 1.1)

                if event.type == self.prop_timer and self.active:
                    self.prop = Prop([self.all_sprites, self.prop_grp], self.scale_factor * 1.1)

            if self.replay_button.show(self.display_surface) and not self.active:
                self.plane = Plane(self.all_sprites, self.scale_factor * 2)
                self.active = True
                self.start_offset = pygame.time.get_ticks()

            # game logic
            self.display_surface.fill('black')

            # control game speed
            if self.score >= 30:
                self.plane.update(delta_time * 1.3)

                self.all_sprites.update(delta_time * 2)

            elif 20 <= self.score < 30:
                self.plane.update(delta_time * 1.2)
                self.all_sprites.update(delta_time * 1.5)

            elif 10 < self.score < 20:
                self.plane.update(delta_time * 1.1)
                self.all_sprites.update(delta_time * 1.3)

            else:
                self.plane.update(delta_time)
                self.all_sprites.update(delta_time)

            self.all_sprites.draw(self.display_surface)
            # print("pygame.time.get_ticks()",pygame.time.get_ticks())

            if self.immortal and (pygame.time.get_ticks() - self.immortal_start) > 5000:
                self.immortal = False

            if self.active:
                if self.immortal:
                    self.plane.activate_magic(self.immortal)
                    self.plane.update(delta_time * 2)
                    self.all_sprites.update(delta_time * 2)
                    self.countdown(5)

                else:
                    self.plane.activate_magic(self.immortal)
                    self.collisions()

                if self.poison:
                    self.plane.activate_poison(self.poison)
                    self.countdown(7)

                if self.poison and (pygame.time.get_ticks() - self.poison_start) > 7000 or not self.active:
                    self.poison = False
                    self.plane.activate_poison(self.poison)

                self.display_score()



            else:
                self.display_surface.blit(self.menu_surf, self.menu_rect)
                self.display_score(game_end=True)

            pygame.display.update()
            # self.clock.tick(FRAMERATE)


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.fill((202, 228, 241))
    pygame.display.set_caption('Menu')
    game_name_img = pygame.image.load('FlappyBirds/graphics/buttons/game-name.png').convert_alpha()
    start_img = pygame.image.load('FlappyBirds/graphics/buttons/start.png').convert_alpha()
    start_img_button = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.7, start_img, 5)
    game_name = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 9, game_name_img, 7)
    start_img_button.show(screen)
    game_name.show(screen)
    run = True
    while run:

        if start_img_button.show(screen):
            game = Game()
            game.start_offset = pygame.time.get_ticks()
            game.run()

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()