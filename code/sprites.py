import pygame
from settings import *
from random import choice, randint

obs_scale_dict = {
    "Trap_Spike_up": 10,
    "Spear": 0.5,
    "Brick": 10,
    "Suriken": 0.8
}

props_list = ["magic_potion", "poison"]


class BackGround(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        background_im = pygame.image.load('FlappyBirds/graphics/background/parallax-mountain-bg.png').convert()
        self.image = pygame.transform.scale(background_im, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.rect = self.image.get_rect(topleft=(0, 0))


class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'ground'

        # image

        ground_surf = pygame.image.load('FlappyBirds/graphics/background/ground.png').convert_alpha()
        self.image = pygame.transform.scale(ground_surf, pygame.math.Vector2(ground_surf.get_size()) * scale_factor)
        #####
        # fixing frame prob
        full_height = ground_surf.get_height() * 0.7
        full_width = ground_surf.get_width() * 0.7
        full_sized_image = pygame.transform.scale(ground_surf, (full_width, full_height))

        self.image = pygame.Surface((full_width * 2, full_height)).convert_alpha()
        self.image.fill([0, 0, 0, 0])  # set the background colour as transparent
        self.image.blit(full_sized_image, (0, 0))
        self.image.blit(full_sized_image, (full_width, 0))

        # position
        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        self.pos.x -= 300 * delta_time  # change ground run speed
        if self.rect.centerx <= 0:
            self.pos.x = 0

        self.rect.x = round(self.pos.x)


class Plane(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        # image
        self.scale_factor = scale_factor
        self.import_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # rect
        self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 4, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # movement
        self.gravity = 300  # 800
        self.direction = 0

        # mask
        self.mask = pygame.mask.from_surface(self.image)

        #immortal
        self.immortal = False
        self.magic_state = False


        # sound
        self.jump_sound = pygame.mixer.Sound('FlappyBirds/music/Mokugyo.wav')
        self.jump_sound.set_volume(1.2)

    def import_frames(self):
        self.frames = []
        for i in range(4):
            surf = pygame.image.load(f'FlappyBirds/graphics/characters/angel-{i + 1}.png').convert_alpha()
            scaled_surface = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * self.scale_factor)
            self.frames.append(scaled_surface)
        # print(self.frames)

    def apply_gravity(self, dt):
        # print("==========",self.magic_state)
        if self.magic_state == False:
            self.direction += self.gravity * dt
            self.pos.y += self.direction * dt
            self.rect.y = round(self.pos.y)

    def jump(self): # magic_state
        if self.magic_state == False:
            self.jump_sound.play()
            self.direction = -250

    def animate(self, dt):
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def activate_poison(self,poison_state):
        # print("poison_state",poison_state)
        if poison_state:
            self.scale_factor = 2.1
        else:
            self.scale_factor = 1.6
        self.import_frames()
        self.mask = pygame.mask.from_surface(self.image)

    def activate_magic(self,magic_state):
        # print(magic_state)
        self.magic_state = magic_state
        if magic_state:
            self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 4, WINDOW_HEIGHT / 2))
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.jump_use = False
        else:
            self.jump_use = True


    def deactivate_poison(self):
        self.scale_factor = 1.4
        self.import_frames()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'obstacle'

        # accelerate the game

        self.orientation = choice(('up', 'down'))
        self.obs_name = choice(list(obs_scale_dict.keys()))
        # obs_name = "Spear-16"

        if self.obs_name == "Spear" or self.obs_name == "Suriken":
            self.import_frames(scale_factor)
            self.frame_index = 0
            self.image = self.frames[self.frame_index]
            x = WINDOW_WIDTH + randint(50, 110)
            if self.obs_name == "Suriken":
                if self.orientation == 'up':
                    y = WINDOW_HEIGHT + 100
                    self.rect = self.image.get_rect(midbottom=(x, y))
                else:
                    y = -100
                    self.image = pygame.transform.flip(self.image, False, True)
                    self.rect = self.image.get_rect(midtop=(x, y))
            else:
                y = WINDOW_HEIGHT + 50
                self.rect = self.image.get_rect(midbottom=(x, y))  #####


        else:
            surf = pygame.image.load(f'FlappyBirds/graphics/obstacles/{self.obs_name}.png').convert_alpha()
            self.image = pygame.transform.scale(surf,
                                                pygame.math.Vector2(surf.get_size()) * obs_scale_dict[self.obs_name])

            x = WINDOW_WIDTH + randint(50, 110)  # 40，100 #initial position of obstacles

            if self.orientation == 'up':
                y = WINDOW_HEIGHT + 50
                self.rect = self.image.get_rect(midbottom=(x, y))
            else:
                y = -50
                self.image = pygame.transform.flip(self.image, False, True)
                self.rect = self.image.get_rect(midtop=(x, y))

        self.pos = pygame.math.Vector2(self.rect.topleft)

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def import_frames(self, scale_factor):
        self.frames = []
        if self.obs_name == "Suriken":
            end_frame = 9
        if self.obs_name == "Spear":
            end_frame = 18
        for i in range(1, end_frame):
            surf = pygame.image.load(f'FlappyBirds/graphics/obstacles/{self.obs_name}-{i}.tiff').convert_alpha()
            scaled_surface = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * obs_scale_dict[
                self.obs_name])
            self.frames.append(scaled_surface)
        # print(self.frames)

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        # print(self.frame_index)
        self.mask = pygame.mask.from_surface(self.image)
        # print("========")
        # olist = self.mask.outline()

    def update(self, dt):
        if self.obs_name == "Spear" or self.obs_name == "Suriken":
            self.animate(dt)
        self.pos.x -= 300 * dt  # change obstacles run speed
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
            self.kill()


class Prop(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = "prop"

        self.prop = choice(props_list)

        surf = pygame.image.load(f'FlappyBirds/graphics/props/{self.prop}.png').convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * 1.5)

        x = WINDOW_WIDTH + randint(50, 110)  # 40，100 #initial position of obstacles

        self.rect = self.image.get_rect(midtop=(x, WINDOW_HEIGHT / 2))

        self.pos = pygame.math.Vector2(self.rect.topleft)

        # mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # if self.obs_name == "Spear" or self.obs_name == "Suriken":
        #     self.animate(dt)
        self.pos.x -= 300 * dt  # change obstacles run speed
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
            self.kill()






