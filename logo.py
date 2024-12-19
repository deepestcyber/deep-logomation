import math
import random

import pygame
from typing import Iterable, Tuple

# deep cyber

class Spark:
    def __init__(self, path: "Path", velocity: float, backwards: bool = False):
        self.path = path
        if backwards:
            self.velocity = -velocity
            self.distance = path.length
        else:
            self.velocity = velocity
            self.distance = 0.0
        self.direction: str = "in"

    def get_position(self):
        return self.path.calculate_position(self.distance)

    def move(self, dt: float):
        self.distance += self.velocity * dt
        if self.distance <= 0.0 or self.distance >= self.path.length:
            return False
        return True


class Path:
    def __init__(self, start: "Node", end: "Node", points: Iterable[Tuple[float, float]]):
        self.start = start
        self.end = end
        self.points: [(float, float)] = tuple(points)
        self.length: float = 0.0
        self._calculate_length()

    def _calculate_length(self):
        last = None
        for p in self.points:
            if last:
                self.length += math.dist(last, p)
            last = p

    def calculate_position(self, distance):
        if distance < 0 or distance > self.length:
            return None
        l = 0
        last = None
        for p in self.points:
            if last:
                d = math.dist(last, p)
                if l + d >= distance:
                    return (
                        last[0] + (p[0] - last[0]) * (distance - l) / d,
                        last[1] + (p[1] - last[1]) * (distance - l) / d,
                    )
                l += d
            last = p
        return None


class Node:
    def __init__(self, name: str, rect: pygame.Rect):
        self.name = name
        self.rect = rect
        self.paths: [(Path, bool)] = []

    def add_start(self, path: Path):
        self.paths.append((path, False))

    def add_end(self, path: Path):
        self.paths.append((path, True))

    def spawn_random_spark(self):
        path = random.choice(self.paths)
        sp = Spark(path[0], 200.0, path[1])
        return [sp]

    def receive_spark(self, spark: Spark):
        return self.spawn_random_spark()


class Pin(Node):
    def receive_spark(self, spark: Spark):
        # simply consume spark
        return []


class Neuron(Node):
    def __init__(self, name: str, rect: pygame.Rect):
        super().__init__(name, rect)
        self.threshold = 4.0
        self.charge = 0.0

    def receive_spark(self, spark: Spark):
        self.charge += 1.0
        if self.charge >= self.threshold:
            self.charge = 0.0
            sparks = []
            for path in self.paths:
                sp = Spark(path[0], 200.0, path[1])
                sparks.append(sp)
            return sparks
        return []


class BottomNeuron(Node):
    def __init__(self, name: str, rect: pygame.Rect):
        super().__init__(name, rect)
        self.threshold = 4.0
        self.charge = 0.0

    def receive_spark(self, spark: Spark):
        self.charge += 1.0
        if self.charge >= self.threshold:
            self.charge = 0.0
            sparks = []
            for path in self.paths:
                sp = Spark(path[0], 200.0, path[1])
                sp.direction = "up"
                sparks.append(sp)
            return sparks
        return []


class BiNeuron(Node):
    def __init__(self, name: str, rect: pygame.Rect):
        super().__init__(name, rect)
        self.threshold = 3.0
        self.charge_up = 0.0
        self.charge_down = 0.0
        self.paths_up: [int] = []
        self.paths_down: [int] = []

    def receive_spark(self, spark: Spark):
        if spark.direction == "up":
            self.charge_up += 1.0
        else:
            self.charge_down += 1.0
        sparks = []
        if self.charge_up >= self.threshold:
            print("UP")
            self.charge_up = 0.0
            for n in self.paths_up:
                path = self.paths[n]
                sp = Spark(path[0], 200.0, path[1])
                sp.direction = "up"
                sparks.append(sp)
        if self.charge_down >= self.threshold:
            print("DOWN")
            self.charge_down = 0.0
            for n in self.paths_down:
                path = self.paths[n]
                sp = Spark(path[0], 200.0, path[1])
                sp.direction = "down"
                sparks.append(sp)
        return sparks

# 122.96, 133.49 -> 10.53

class Logo:
    def __init__(self):
        self.nodes = []
        self.paths = []
        self.sparks = []
        self.build()

    def move(self, dt: float):
        sparks = []
        for spark in self.sparks:
            if spark.move(dt):
                sparks.append(spark)
            else:
                if spark.distance <= 0.0:
                    node = spark.path.start
                else:
                    node = spark.path.end
                new_sparks = node.receive_spark(spark)
                for new_spark in new_sparks:
                    sparks.append(new_spark)
        self.sparks = sparks

    def go(self):
        num = random.choice(range(8))
        pin = self.nodes[num]
        spark = Spark(pin.paths[0][0], 200.0)
        self.sparks.append(spark)

    def add_hole(self, name: str, pos: (float, float)):
        diameter = 10.53
        r = pygame.Rect(pos[0] - diameter/2, pos[1] - diameter/2, diameter, diameter)
        node = Pin(name, r)
        self.nodes.append(node)
        return node

    def add_letter(self, name: str, rect: pygame.Rect):
        node = BiNeuron(name, rect)
        self.nodes.append(node)
        return node

    def add_bobble(self, name: str, pos: (float, float), clazz: type=BiNeuron):
        diameter = 38.995
        r = pygame.Rect(pos[0], pos[1], diameter, diameter)
        node = clazz(name, r)
        self.nodes.append(node)
        return node

    def add_path(self, start: "Node", end: "Node", points: Iterable[Tuple[float, float]]):
        path = Path(start, end, points)
        self.paths.append(path)
        start.add_start(path)
        end.add_end(path)

    def build(self):
        # left side contacts
        l0 = self.add_hole("pin_l0", (28.131, 128.235))
        l1 = self.add_hole("pin_l1", (28.131, 142.034))
        l2 = self.add_hole("pin_l2", (28.131, 153.835))
        l3 = self.add_hole("pin_l3", (28.131, 166.635))
        l4 = self.add_hole("pin_l4", (28.131, 179.435))
        l5 = self.add_hole("pin_l5", (28.131, 192.255))
        l6 = self.add_hole("pin_l6", (28.131, 205.035))
        # top side contacts
        t0 = self.add_hole("pin_t0", (200.931, 77.035))
        t1 = self.add_hole("pin_t1", (213.731, 77.035))
        t2 = self.add_hole("pin_t2", (226.531, 77.035))
        t3 = self.add_hole("pin_t3", (239.331, 77.035))
        t4 = self.add_hole("pin_t4", (252.131, 77.035))
        t5 = self.add_hole("pin_t5", (264.931, 77.035))
        t6 = self.add_hole("pin_t6", (277.731, 77.035))
        # Letters
        lt0 = self.add_letter("lt0", pygame.Rect(87.722, 110.160, 62.453, 44.800))
        lt0.paths_up = [3, 4]
        lt0.paths_down = [5]
        lt1 = self.add_letter("lt1", pygame.Rect(148.035, 122.373, 57.227, 32.587))
        lt0.paths_up = [0]
        lt0.paths_down = [1, 2]
        lt2 = self.add_letter("lt2", pygame.Rect(205.951, 122.373, 57.227, 32.587))
        lt3 = self.add_letter("lt3", pygame.Rect(260.401, 122.373, 62.453, 44.800))
        lt4 = self.add_letter("lt4", pygame.Rect(59.389, 175.707, 58.507, 32.587))
        lt5 = self.add_letter("lt5", pygame.Rect(118.556, 175.707, 58.507, 44.800))
        lt6 = self.add_letter("lt6", pygame.Rect(177.201, 163.493, 57.227, 44.800))
        lt7 = self.add_letter("lt7", pygame.Rect(235.118, 175.707, 57.227, 32.587))
        lt8 = self.add_letter("lt8", pygame.Rect(293.035, 175.707, 58.507, 32.587))
        # Bobbles
        b0 = self.add_bobble("b0", (81.416, 233.500))
        b1 = self.add_bobble("b1", (142.140, 233.500))
        b2 = self.add_bobble("b2", (202.865, 233.500))
        b3 = self.add_bobble("b3", (263.589, 233.500))
        b4 = self.add_bobble("b4", (111.282, 295.108), BottomNeuron)
        b5 = self.add_bobble("b5", (172.007, 295.108), BottomNeuron)
        b6 = self.add_bobble("b6", (232.732, 295.108), BottomNeuron)
        # Paths
        # - from left pins
        self.add_path(l0, t0, (
            (32.561, 128.293),
            (90.61, 128.293),
            (94.425, 115.502),
            (128.550, 115.502),
            (132.115, 104.827),
            (154.162, 104.827),
            (156.317, 111.227),
            (189.004, 111.227),
            (191.848, 102.693),
            (201.094, 102.693),
            (201.094, 81.360),
        ))
        self.add_path(l1, lt0, (
            (32.557, 140.927),
            (97.010, 140.927),
        ))
        self.add_path(l2, lt0, (
            (32.581, 153.871),
            (53.184, 153.893),
            (53.894, 156.026),
            (94.427, 156.026),
            (96.561, 149.626),
        ))
        self.add_path(l3, lt0, (
            (32.558, 166.688),
            (51.761, 166.693),
            (53.894, 160.293),
            (111.494, 160.293),
            (112.917, 156.026),
            (124.294, 156.026),
            (124.294, 151.759),
        ))
        self.add_path(l4, lt6, (
            (32.573, 179.496),
            (51.761, 179.492),
            (56.738, 164.559),
            (114.338, 164.559),
            (115.761, 160.293),
            (161.271, 160.293),
            (162.694, 164.558),
            (187.584, 164.558),
            (189.004, 160.292),
            (191.850, 160.292),
            (192.571, 162.425),
            (192.571, 166.695),
        ))
        self.add_path(l5, lt5, (
            (32.561, 192.290),
            (51.761, 192.292),
            (59.584, 168.825),
            (117.184, 168.825),
            (118.604, 164.558),
            (158.424, 164.557),
            (159.850, 168.824),
            (171.227, 168.837),
            (171.227, 177.358),
        ))
        self.add_path(l6, lt4, (
            (32.561, 205.092),
            (51.761, 205.092),
            (62.427, 173.092),
            (73.094, 173.092),
            (73.094, 181.625),
        ))
        # - from d
        self.add_path(lt0, t1, (
            (102.250, 126.160),
            (104.384, 119.760),
            (131.404, 119.758),
            (134.961, 109.094),
            (151.315, 109.100),
            (153.448, 115.493),
            (191.848, 115.493),
            (194.695, 106.960),
            (213.894, 106.960),
            (213.894, 81.360),
        ))
        self.add_path(lt0, t2, (
            (134.961, 149.627),
            (142.784, 149.627),
            (152.738, 119.760),
            (194.848, 119.627),
            (197.538, 111.227),
            (226.694, 111.218),
            (226.694, 81.360),
        ))
        self.add_path(lt0, lt6, (
            (128.561, 151.759),
            (128.594, 156.068),
            (164.117, 156.026),
            (165.538, 160.293),
            (185.094, 160.293),
            (186.694, 156.026),
            (194.694, 156.026),
            (196.828, 162.426),
            (196.827, 166.717),
        ))
        # e1
        self.add_path(lt1, t3, (
            (197.538, 123.993),
            (200.381, 115.493),
            (239.494, 115.480),
            (239.494, 81.357),
        ))
        self.add_path(lt1, lt3, (
            (192.561, 136.826),
            (194.694, 143.226),
            (203.938, 143.226),
            (211.761, 119.762),
            (250.871, 119.758),
            (252.303, 115.503),
            (294.961, 115.503),
            (294.967, 126.159),
        ))
        self.add_path(lt1, lt8, (
            (181.788, 147.519),
            (201.804, 147.493),
            (207.494, 164.559),
            (250.161, 164.559),
            (253.004, 173.096),
            (275.761, 173.092),
            (278.604, 164.560),
            (302.784, 164.564),
            (307.761, 179.493),
        ))
        self.add_path(lt1, lt6, (
            (166.997, 151.759),
            (168.381, 156.026),
            (182.604, 156.026),
            (184.027, 151.759),
            (198.961, 151.759),
            (204.650, 168.826),
            (224.564, 168.826),
            (224.568, 177.364),
        ))
        # - e2
        self.add_path(lt2, lt3, (
            (250.161, 136.827),
            (252.294, 143.227),
            (262.248, 143.227),
            (270.781, 119.760),
            (278.604, 119.760),
            (280.738, 126.160),
        ))
        self.add_path(lt2, lt3, (
            (239.494, 143.227),
            (247.317, 143.227),
            (248.738, 147.493),
            (269.361, 147.493),
        ))
        self.add_path(lt2, lt3, (
            (237.361, 147.493),
            (244.471, 147.493),
            (245.894, 151.760),
            (267.227, 151.760),
        ))
        self.add_path(lt2, lt3, (
            (230.248, 151.759),
            (231.671, 156.026),
            (255.850, 156.026),
            (258.694, 164.559),
            (262.961, 164.559),
        ))
        self.add_path(lt2, lt8, (
            (211.760, 151.757),
            (214.604, 160.293),
            (252.998, 160.293),
            (255.850, 168.826),
            (272.917, 168.826),
            (275.761, 160.293),
            (305.627, 160.288),
            (309.894, 173.093),
            (334.783, 173.093),
            (336.917, 179.493),
        ))
        # - p
        self.add_path(lt3, t4, (
            (316.294, 124.026),
            (312.027, 111.226),
            (252.294, 111.226),
            (252.294, 81.359),
        ))
        self.add_path(lt3, t5, (
            (311.317, 151.759),
            (312.738, 156.026),
            (316.294, 156.026),
            (324.827, 130.426),
            (324.827, 124.026),
            (319.138, 106.959),
            (265.094, 106.968),
            (265.105, 81.363),
        ))
        self.add_path(lt3, lt8, (
            (276.471, 151.759),
            (277.894, 156.026),
            (308.471, 156.026),
            (312.738, 168.826),
            (337.627, 168.826),
        ))
        # - c
        self.add_path(lt4, lt5, (
            (77.361, 177.358),
            (77.361, 173.092),
            (120.027, 173.092),
            (121.450, 168.825),
            (155.584, 168.825),
            (157.004, 173.092),
            (166.961, 173.092),
            (166.961, 177.358),
        ))
        self.add_path(lt4, lt5, (
            (115.761, 179.492),
            (122.161, 179.492),
            (124.294, 173.092),
            (130.694, 173.092),
            (132.827, 179.492),
        ))
        # - y
        self.add_path(lt5, lt6, (
            (166.961, 199.760),
            (173.894, 199.760),
            (180.827, 178.427),
            (188.294, 178.427),
        ))
        # - b
        self.add_path(lt6, lt7, (
            (228.827, 179.493),
            (228.827, 168.826),
            (247.317, 168.826),
            (250.161, 177.359),
        ))
        # - e3
        self.add_path(lt7, lt8, (
            (277.894, 179.493),
            (281.451, 168.826),
            (299.938, 168.826),
            (305.627, 185.893),
        ))
        self.add_path(lt7, lt8, (
            (282.161, 179.493),
            (284.294, 173.093),
            (297.096, 173.093),
            (299.227, 179.507),
            (299.223, 181.626),
            (296.384, 190.151),
            (296.384, 194.426),
            (300.650, 200.826),
        ))
        # - r
        self.add_path(lt8, t6, (
            (345.450, 179.492),
            (340.471, 164.559),
            (321.983, 164.559),
            (320.561, 160.292),
            (320.561, 156.026),
            (329.094, 130.426),
            (329.094, 124.026),
            (321.983, 102.692),
            (277.891, 102.693),
            (277.881, 81.365),
        ))

        # - cyber to upper layer
        self.add_path(lt4, b0, (
            (67.010, 204.030),
            (90.496, 237.953),
        ))
        self.add_path(lt4, b1, (
            (97.920, 203.093),
            (147.344, 241.802),
        ))
        self.add_path(lt5, b0, (
            (129.698, 204.595),
            (110.214, 237.358),
        ))
        self.add_path(lt5, b1, (
            (155.240, 216.486),
            (158.504, 235.114),
        ))
        self.add_path(lt5, b2, (
            (159.870, 216.395),
            (206.574, 243.750),
        ))
        self.add_path(lt6, b1, (
            (198.961, 205.093),
            (172.832, 238.630),
        ))
        self.add_path(lt6, b2, (
            (209.627, 205.093),
            (217.606, 235.106),
        ))
        self.add_path(lt7, b2, (
            (248.114, 205.093),
            (231.104, 236.736),
        ))
        self.add_path(lt7, b3, (
            (262.961, 205.093),
            (276.037, 236.218),
        ))
        self.add_path(lt8, b2, (
            (300.338, 204.443),
            (238.002, 243.259),
        ))
        self.add_path(lt8, b3, (
            (344.368, 186.569),
            (295.474, 239.570),
        ))
        # - upper to lower layer
        self.add_path(b0, b4, (
            (108.844, 269.358),
            (122.840, 298.227),
        ))
        self.add_path(b0, b5, (
            (115.967, 263.235),
            (176.377, 304.318),
        ))
        self.add_path(b0, b6, (
            (117.568, 259.778),
            (235.381, 307.746),
        ))
        self.add_path(b1, b4, (
            (153.426, 269.392),
            (138.871, 298.451),
        ))
        self.add_path(b1, b5, (
            (169.622, 269.468),
            (183.559, 298.215),
        ))
        self.add_path(b1, b6, (
            (176.685, 263.230),
            (237.073, 304.298),
        ))
        self.add_path(b2, b4, (
            (207.279, 263.144),
            (145.962, 304.392),
        ))
        self.add_path(b2, b5, (
            (214.191, 269.311),
            (199.662, 298.318),
        ))
        self.add_path(b2, b6, (
            (230.311, 269.394),
            (244.229, 298.102),
        ))
        self.add_path(b3, b4, (
            (266.056, 259.886),
            (147.808, 307.717),
        ))
        self.add_path(b3, b5, (
            (267.851, 263.247),
            (206.720, 304.369),
        ))
        self.add_path(b3, b6, (
            (274.916, 269.310),
            (260.320, 298.451),
        ))
        print("Paths:", len(self.paths))
        print("LT0:", lt0.paths, lt0.paths_up, lt0.paths_down)