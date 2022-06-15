import pygame
import os
import math
import sys
import neat
import time
from math import sqrt
pygame.init()
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
TRACK_NAME = "track3.png"
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FONT = pygame.font.SysFont('Consolas', 24)

TRACK = pygame.image.load(os.path.join("Assets", TRACK_NAME))


def calc_distance(p1, p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)


def hardcoded_track_setup(item):
    # kilkanascie generacji
    if(TRACK_NAME == "track4.png"):
        item.Velocity = 1.0
        item.Start = (650, 710)
    # ze 20 generacji
    if(TRACK_NAME == "track3.png"):
        item.Velocity = 1.05
        item.Start = (320, 710)
    if(TRACK_NAME == "track.2.png"):
        item.Velocity = 0.9
        item.Start = (150, 700)


class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(
            os.path.join("Assets", "car.png"))
        self.image = self.original_image
        hardcoded_track_setup(self)
        self.rect = self.image.get_rect(center=self.Start)
        self.vel_vector = pygame.math.Vector2(self.Velocity, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        self.started = False

    def update(self):
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)
        self.collision()
        self.data()

    def drive(self):
        self.rect.center += self.vel_vector * 6

    def collision(self):
        length = 36
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]
        collision_point_back_left = [int(self.rect.center[0] - math.cos(math.radians(self.angle + 18)) * length),
                                     int(self.rect.center[1] + math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_back_right = [int(self.rect.center[0] - math.cos(math.radians(self.angle - 18)) * length),
                                      int(self.rect.center[1] + math.sin(math.radians(self.angle - 18)) * length)]

        # Die on Collision
        try:
            if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                    or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_back_left) == pygame.Color(2, 105, 31, 255) \
                    or SCREEN.get_at(collision_point_back_right) == pygame.Color(2, 105, 31, 255):
                self.alive = False
        except:
            self.alive = False

        # Draw Collision Points
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(
            self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])
        try:
            while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200:
                length += 1
                x = int(
                    self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(
                    self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)
        except:
            self.alive = False
        # Draw Radar
        pygame.draw.line(SCREEN, (255, 255, 255, 255),
                         self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                             + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)


def play():
    car = pygame.sprite.GroupSingle(Car())
    started = False
    car.sprite.vel_vector = pygame.math.Vector2(0, 0)
    car.sprite.Velocity = 0
    start_ticks = pygame.time.get_ticks()
    timer_text = '00:00.0'
    best_time = sys.maxsize
    best_text = ''
    while True:
        SCREEN.blit(TRACK, (0, 0))
        if started and calc_distance(car.sprite.rect.center, car.sprite.Start) < 25.0:
            if pygame.time.get_ticks()-start_ticks < best_time:
                best_time = pygame.time.get_ticks()-start_ticks
                best_minutes = int((pygame.time.get_ticks()-start_ticks)/60000)
                best_seconds = int(
                    (pygame.time.get_ticks()-start_ticks)/1000) % 60
                best_millis = int(
                    (pygame.time.get_ticks()-start_ticks)/100) % 10
                best_text = str(best_minutes)+':' + \
                    str(best_seconds)+'.'+str(best_millis)
            start_ticks = pygame.time.get_ticks()
            started = False
        elif not started and calc_distance(car.sprite.rect.center, car.sprite.Start) > 100.0:
            started = True

        minutes = int((pygame.time.get_ticks()-start_ticks)/60000)
        seconds = int((pygame.time.get_ticks()-start_ticks)/1000) % 60
        millis = int((pygame.time.get_ticks()-start_ticks)/100) % 10
        timer_text = str(minutes)+':'+str(seconds)+'.'+str(millis)
        SCREEN.blit(FONT.render(timer_text, True, (0, 0, 0)), (32, 48))
        SCREEN.blit(FONT.render('Best time: ', True, (0, 0, 0)), (1150, 48))
        if best_text != '':
            SCREEN.blit(FONT.render(best_text,
                                    True, (0, 0, 0)), (1300, 48))
        if not car.sprite.alive:
            car = pygame.sprite.GroupSingle(Car())
            start_ticks = pygame.time.get_ticks()
            car.sprite.Velocity = 0
            car.sprite.vel_vector = pygame.math.Vector2(0, 0)
            started = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            if car.sprite.Velocity != 0:
                car.sprite.direction = -1
        if keys[pygame.K_d]:
            if car.sprite.Velocity != 0:
                car.sprite.direction = 1
        if keys[pygame.K_w]:
            car.sprite.direction = 0
            car.sprite.Velocity += 0.1
            if car.sprite.Velocity == 0.0:
                car.sprite.vel_vector = pygame.math.Vector2(0, 0)
            elif car.sprite.Velocity > 0.0 and car.sprite.Velocity <= 0.125:
                car.sprite.vel_vector = pygame.math.Vector2(
                    car.sprite.Velocity, 0)
                car.sprite.vel_vector.rotate_ip(-car.sprite.angle)
            else:
                car.sprite.vel_vector.scale_to_length(car.sprite.Velocity)
        if keys[pygame.K_s]:
            if car.sprite.Velocity > -0.3:
                car.sprite.direction = 0
                car.sprite.Velocity -= 0.1
                if car.sprite.Velocity == 0.0:
                    car.sprite.vel_vector = pygame.math.Vector2(0, 0)
                elif car.sprite.Velocity < 0.0 and car.sprite.Velocity >= -0.125:
                    car.sprite.vel_vector = pygame.math.Vector2(
                        car.sprite.Velocity, 0)
                    car.sprite.vel_vector.rotate_ip(-car.sprite.angle)
                else:
                    car.sprite.vel_vector.scale_to_length(car.sprite.Velocity)
        if keys[pygame.K_x]:
            break
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            car.sprite.direction = 0

        car.draw(SCREEN)
        car.update()
        pygame.display.update()
        pygame.event.pump()
        time.sleep(0.05)


def eval_genomes(genomes, config):
    global cars, ge, nets

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    start_ticks = pygame.time.get_ticks()
    timer_text = '00:00.0'
    best_time = sys.maxsize
    best_text = ''
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    cars = []
                    pygame.display.update()
                    play()
                    start_ticks = pygame.time.get_ticks()
                    timer_text = '00:00.0'
                    best_time = sys.maxsize
                    best_text = ''

        SCREEN.blit(TRACK, (0, 0))
        minutes = int((pygame.time.get_ticks()-start_ticks)/60000)
        seconds = int((pygame.time.get_ticks()-start_ticks)/1000) % 60
        millis = int((pygame.time.get_ticks()-start_ticks)/100) % 10
        timer_text = str(minutes)+':'+str(seconds)+'.'+str(millis)
        SCREEN.blit(FONT.render(timer_text, True, (0, 0, 0)), (32, 48))
        SCREEN.blit(FONT.render('Best time: ',
                    True, (0, 0, 0)), (1150, 48))
        if len(cars) == 0:
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0

        # Update
        for car in cars:
            car.draw(SCREEN)
            car.update()
            if car.sprite.started and calc_distance(car.sprite.rect.center, car.sprite.Start) < 25.0:
                if pygame.time.get_ticks()-start_ticks < best_time:
                    best_time = pygame.time.get_ticks()-start_ticks
                    best_minutes = int(
                        (pygame.time.get_ticks()-start_ticks)/60000)
                    best_seconds = int(
                        (pygame.time.get_ticks()-start_ticks)/1000) % 60
                    best_millis = int(
                        (pygame.time.get_ticks()-start_ticks)/100) % 10
                    best_text = str(best_minutes)+':' + \
                        str(best_seconds)+'.'+str(best_millis)
                start_ticks = pygame.time.get_ticks()
                car.sprite.started = False
            elif not car.sprite.started and calc_distance(car.sprite.rect.center, car.sprite.Start) > 100.0:
                car.sprite.started = True

            if best_text != '':
                SCREEN.blit(FONT.render(best_text,
                                        True, (0, 0, 0)), (1300, 48))
        pygame.display.update()


# Setup NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
