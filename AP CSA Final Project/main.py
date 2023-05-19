import pygame
import os
import math

class Tank:
    def __init__(self, midbottom_position, direction, name, color, right_key, 
                 left_key, up_key, down_key, shoot_key):
        # initialize tank sufaces
        self.surf =  pygame.image.load(os.path.join("tank.png"))
        self.surf = pygame.transform.scale(
            self.surf, (self.surf.get_width()*game.tank_scale, self.surf.get_height()*game.tank_scale) )
        self.rect = self.surf.get_rect(midbottom = midbottom_position)
        self.default_shooter_surf = pygame.image.load(os.path.join("tank_shooter.png"))
        self.direction = direction
        # flips tank if its facing left
        if direction == "left":
            self.surf = pygame.transform.flip(self.surf, True, False)
            self.default_shooter_surf = pygame.transform.flip(self.default_shooter_surf, True, False)
        self.right_key = right_key
        self.left_key = left_key
        self.up_key = up_key
        self.down_key = down_key
        self.shoot_key = shoot_key
        self.angle = 0
        self.score = 0
        self.name = name
        self.win_text = game.font.render(name + " Wins!", True, "black")
        self.color = color
        self.score_text = ""
        self.update_score_text()
        self.update_shootersurf()
        self.explosion_surfs = [
            pygame.image.load(os.path.join("explosion_1.png")),
            pygame.image.load(os.path.join("explosion_2.png")),
            pygame.image.load(os.path.join("explosion_3.png")),
            pygame.image.load(os.path.join("explosion_4.png"))
        ]
        self.current_explosion_frame = -1
        
    def update_tank(self):
        keys = pygame.key.get_pressed()
        # update tank x position
        if keys[getattr(pygame, self.left_key)]:
            self.rect.x -= game.tank_speed
            self.update_shootersurf()
        if keys[getattr(pygame, self.right_key)]:
            self.rect.x += game.tank_speed
            self.update_shootersurf()
        # make sure tank cant go off the screen
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > game.width: self.rect.right = game.width
        # update tank shooter angle
        if keys[getattr(pygame, self.up_key)] and self.angle < 90:
            self.angle +=1
            self.update_shootersurf()
        if keys[getattr(pygame, self.down_key)] and self.angle > 0:
            self.angle -=1
            self.update_shootersurf()

    def display(self):
        # display the tank surface and shooter
        game.screen.blit(self.surf, self.rect)
        game.screen.blit(self.shooter_surf, self.shooter_rect)

        #display explosion if applicable
        if self.current_explosion_frame != -1:
            animation_surf = self.explosion_surfs[int(self.current_explosion_frame/(game.explosion_duration/4))]
            animation_surf = pygame.transform.scale(
                animation_surf, (animation_surf.get_width()*game.tank_scale, animation_surf.get_height()*game.tank_scale))
            animation_rect = animation_surf.get_rect(center = self.rect.center)
            game.screen.blit(animation_surf, animation_rect)
            self.current_explosion_frame += 1
            if self.current_explosion_frame == game.explosion_duration:
                self.current_explosion_frame = -1

    def update_shootersurf(self):
        # updates the appropriate shooter surface depending on the angle and direction facing
        if self.direction == "left":
            self.shooter_surf = pygame.transform.rotate(self.default_shooter_surf, -self.angle)
            self.shooter_rect = self.shooter_surf.get_rect(bottomright = (self.rect.centerx, self.rect.centery-self.rect.height*0.3))
        else:
            self.shooter_surf = pygame.transform.rotate(self.default_shooter_surf, self.angle)
            self.shooter_rect = self.shooter_surf.get_rect(bottomleft = (self.rect.centerx, self.rect.centery-self.rect.height*0.3))

    def update_score_text(self):
        self.score_text = game.font.render(str(self.score), True, self.color)

class Bullet:
    def __init__(self, tank):
        self.tank = tank
        # initialize y velocity
        self.y_vel = -game.bullet_speed * math.sin(self.tank.angle * math.pi/180)
        # initialize x velosity based on tank direction
        if self.tank.direction == "left":
            self.x = self.tank.shooter_rect.left
            self.y = self.tank.shooter_rect.top
            self.x_vel = -game.bullet_speed * math.cos(self.tank.angle * math.pi/180)
        else:
            self.x = self.tank.shooter_rect.right
            self.y = self.tank.shooter_rect.top
            self.x_vel = game.bullet_speed * math.cos(self.tank.angle * math.pi/180)
        #adjust x velocity based on how tank is moving
        if pygame.key.get_pressed()[getattr(pygame, self.tank.left_key)]:
            self.x_vel -= game.tank_speed
        if pygame.key.get_pressed()[getattr(pygame, self.tank.right_key)]:
            self.x_vel += game.tank_speed

        self.display()

    def display(self):
        self.rect = pygame.draw.circle(game.screen, self.tank.color, (self.x, self.y), game.bullet_size, 0)

    def update(self):
        # moves bullet in x and y directions
        self.x += self.x_vel
        self.y_vel += game.gravity
        self.y += self.y_vel
        # checks if the bullet hit with any of the tanks
        for tank in game.tanks:
            if self.rect.colliderect(tank.rect) and self.tank != tank:
                game.bullets.remove(self)
                tank.score += 1
                if tank.score == game.ending_score: 
                    game.winner = tank
                tank.update_score_text()
                if tank.current_explosion_frame == -1:
                    tank.current_explosion_frame = 0
        #check if bullet lands on the ground
        if self.y > game.ground_rect.top:
            if self in game.bullets: game.bullets.remove(self)

class Game:
    def __init__ (self):
        pygame.init()
        info = pygame.display.Info()
        pygame.display.set_caption("tanks")
        self.width = info.current_w * .9
        self.height = info.current_h * .9
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.bullets = []
        self.tanks = []
        self.winner = "none"

        # settings
        self.sky_color = (36, 141, 227)
        self.ground_color = (13, 97, 24)
        self.red = (110, 2, 11)
        self.blue = (19, 0, 158)
        self.tick_speed = 120
        self.gravity = 0.1
        self.tank_speed = 5
        self.bullet_size = 8
        self.bullet_speed = 8
        self.tank_scale = 0.7
        self.explosion_duration = 30
        self.ending_score = 20
        self.font = pygame.font.SysFont('yugothicuisemibold',  60)
        self.winner_font = pygame.font.SysFont('yugothicuisemibold',  60)

    def update(self):
        """
        run one update cycle
        """
        # update tank postion
        for tank in game.tanks:
            tank.update_tank()

        # increase clock 
        self.clock.tick(self.tick_speed)

        # update display
        pygame.display.update()

        #update bullets
        for bullet in self.bullets:
            bullet.update()

    def run(self):
        """
        run update at the specified tick_speed, until exit.
        """
        # creating the objects
        self.ground_surf = pygame.Surface((self.width, 150))
        self.ground_surf.fill(self.ground_color)
        self.ground_rect = self.ground_surf.get_rect(bottomleft = (0, self.height))
        self.left_tank = Tank((self.ground_rect.right*0.25, self.ground_rect.top), 
                              "right", "Red Tank", self.red, "K_d", "K_a", "K_w", "K_s", "K_e")
        self.right_tank = Tank((self.ground_rect.right*0.75, self.ground_rect.top), 
                               "left", "Blue Tank", self.blue, "K_RIGHT", "K_LEFT", "K_UP", "K_DOWN", "K_RSHIFT")
        self.tanks.append(self.right_tank)
        self.tanks.append(self.left_tank)

        # game loop
        while self.running:
            # checking for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == getattr(pygame, self.right_tank.shoot_key):
                        self.bullets.append(Bullet(self.right_tank))
                    if event.key == getattr(pygame, self.left_tank.shoot_key):
                        self.bullets.append(Bullet(self.left_tank))

            #updates objects
            self.update()

            # display objects
            self.screen.fill(self.sky_color)
            self.screen.blit(self.ground_surf, self.ground_rect)
            for i, tank in enumerate(self.tanks):
                tank.display()
                self.screen.blit(tank.score_text, (self.width/(len(self.tanks)+1) * (i+1), 100))
            for bullet in self.bullets:
                bullet.display()
            # displayer winner text if a tank if scored in winner attribute
            if self.winner != "none":
                self.screen.blit(self.winner.win_text, 
                                 (self.width/2-self.winner.win_text.get_width()/2, self.height/2 - self.winner.win_text.get_height()))
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()