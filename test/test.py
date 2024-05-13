import unittest
import pygame

from core.main import Tank, Bullet, Base, Booster
from core.tools import shortest_path, make_graph_from_map


class TestBullet(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Test Game")
        self.tank = Tank(100, 100, True, 'simple')

    def test_bullet_movement(self):
        bullet = Bullet('right', 100, 100, self.tank, 'simple')
        old_x = bullet.x
        bullet.move()
        self.assertTrue(bullet.x > old_x)

    def test_bullet_death(self):
        bullet = Bullet('right', 790, 790, self.tank, 'simple')
        bullet.move()
        self.assertFalse(bullet.alive)


class TestTank(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Test Game")

    def test_tank_movement(self):
        tank = Tank(300, 300, True)
        old_x = tank.x
        tank.move()
        self.assertNotEqual(tank.x, old_x)

    def test_tank_collision(self):
        pass


class TestMap(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Test Game")

    def test_map_draw(self):
        pass


class TestBooster(unittest.TestCase):
    def test_booster_init(self):
        booster = Booster('speed')
        self.assertIn(booster.booster_type, ['speed', 'armor', 'fast_reload'])


class TestBase(unittest.TestCase):
    def test_base_init(self):
        base = Base(400, 400)
        self.assertEqual(base.x, 400)
        self.assertEqual(base.y, 400)


class TestBattleCityAlgorithms(unittest.TestCase):

    def test_shortest_path(self):
        graph = {
            (0, 0): [(0, 1), (1, 0)],
            (0, 1): [(0, 0), (1, 1)],
            (1, 0): [(0, 0), (1, 1)],
            (1, 1): [(0, 1), (1, 0)]
        }

        start = (0, 0)
        end = (1, 1)

        expected_paths = [
            [(0, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (1, 1)]
        ]

        result_path = shortest_path(graph, start, end)

        self.assertIn(result_path, expected_paths)

    def test_make_graph_from_map(self):
        road = [
            [0, 1, 0],
            [0, 0, 0],
            [0, 1, 0]
        ]

        expected_graph = {
            (0, 0): [(0, 1)],
            (0, 1): [(0, 0), (0, 2)],
            (0, 2): [(0, 1)],
            (1, 0): [(1, 1)],
            (1, 1): [(1, 0), (1, 2)],
            (1, 2): [(1, 1)],
        }

        generated_graph = make_graph_from_map(road)

        self.assertEqual(generated_graph, expected_graph)


if __name__ == '__main__':
    unittest.main()
