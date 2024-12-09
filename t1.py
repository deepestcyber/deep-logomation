#!/usr/bin/env python
import io
import math
import sys

import pygame

import logo
from logo import Path

svg_size = 384, 384
size = 1024, 1024
scale = size[0] / svg_size[0], size[1] / svg_size[1]

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    with open ("deep-cyber-logo-x.svg", "r") as f:
        cont = f.read()
        cont = cont.replace(f'width="{svg_size[0]}"', f'width="{size[0]}"')
        cont = cont.replace(f'height="{svg_size[1]}"', f'height="{size[1]}"')
        stream = io.StringIO()
        stream.write(cont)
        stream.seek(0)
        mem = io.BytesIO()
        mem.write(stream.getvalue().encode())
        mem.seek(0)
        logo_img = pygame.image.load(mem, "logo.svg").convert()

    # logo_img = pygame.image.load("deep-cyber-logo.svg").convert()
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
            p_scaled = p[0] * scale[0], p[1] * scale[1]
            screen.blit(spark_img, (int(p_scaled[0] - spark_img.get_size()[0] / 2), int(p_scaled[1] - spark_img.get_size()[0] / 2)))
#        screen.blit(node_img, (0, 0))
        pygame.display.update()
        dt = clock.tick(60) / 1000.0
        dc.move(dt)
#        for sp in sparks:
#            sp.move(dt)
