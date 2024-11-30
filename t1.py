#!/usr/bin/env python
import math
import sys

import pygame

import logo
from logo import Path

size = 384, 384

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    logo_img = pygame.image.load("deep-cyber-logo.svg").convert()
    path_img = pygame.image.load("deep-cyber-path-384.png").convert()
    path_img.set_colorkey(path_img.get_at((0, 0)))
    node_img = pygame.image.load("deep-cyber-top.svg").convert()
    node_img.set_colorkey(node_img.get_at((0, 0)))
    spark_img = pygame.image.load("spark-01.svg").convert()
    spark_img.set_colorkey(spark_img.get_at((0, 0)))
    dc = logo.Logo()
    dt = 0.0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    dc.go()
#        screen.fill((0,0,0))
        screen.blit(logo_img, (0, 0))
        for sp in dc.sparks:
            p = sp.get_position()
            screen.blit(spark_img, (int(p[0] - spark_img.get_size()[0] / 2), int(p[1] - spark_img.get_size()[0] / 2)))
#        screen.blit(node_img, (0, 0))
        pygame.display.update()
        dt = clock.tick(60) / 1000.0
        dc.move(dt)
#        for sp in sparks:
#            sp.move(dt)
