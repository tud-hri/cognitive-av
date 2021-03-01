import random
import time

import numpy as np

import carlo.world
from carlo.agents import Painting, RectangleBuilding
from carlo.entities import Point

from agents import CarHardCoded


class World(carlo.world.World):
    def __init__(self, dt: float, end_time: float, width: float, height: float, ppm: float = 8):
        """
        Redefinition of CARLO's World class, in case we want to customize it
        :param dt:
        :param width:
        :param height:
        :param ppm:
        """
        super(World, self).__init__(dt, width, height, ppm)

        self.width = width
        self.height = height

        self.play_in_rt = True  # flag if simulation is played in realtime, set to False for quick simulations

        # time vector
        self.time_vector = np.arange(0., end_time, dt)  # time vector

    def run(self):
        for k in range(0, len(self.time_vector)):
            # set control for all agents
            for agent in self.dynamic_agents:
                # this is ugly, needs better solution
                if isinstance(agent, CarHardCoded):
                    agent.set_control(k)

            # step the world and render
            self.tick()
            self.render()  # move to self.play_in_rt to speed simulation up

            if self.play_in_rt:
                time.sleep(self.dt / 4.)


def scenario1(dt, end_time):
    """
    Scenario 1
    Straight intersection, two approaching cars, ego vehicle turns left, automated vehicle goes straight
    :param dt: time step
    :param end_time: end time of simulation
    """

    # create our world
    # coordinate system: x (right, meters), y (up, meters), psi (CCW, east = 0., rad)
    world = World(dt, end_time, width=80., height=80., ppm=6.)  # The world is 120 meters by 120 meters. ppm is the pixels per meter.

    # create the intersection
    p_intersection = Point(50., 30.)
    n_lanes = 2
    lane_width = 3.  # meters
    road_width = n_lanes * lane_width
    sidewalk_width = 2.

    # in carlo, roads are defined by the sidewalks, so, create sidewalks, buildings
    # this is a bit of a mess
    # bottom left
    world.add(Painting(p_intersection / 2. - Point(road_width, road_width) / 2., p_intersection, 'gray80'))
    world.add(
        RectangleBuilding(p_intersection / 2. - Point(road_width + sidewalk_width, road_width + sidewalk_width) / 2., p_intersection, 'forest green'))

    # bottom right
    world.add(Painting(Point(p_intersection.x + (world.width - p_intersection.x) / 2. + road_width / 2., p_intersection.y / 2. - road_width / 2.),
                       Point(world.width - p_intersection.x, p_intersection.y), 'gray80'))  # sidewalk
    world.add(RectangleBuilding(Point(p_intersection.x + (world.width - p_intersection.x) / 2. + (road_width + sidewalk_width) / 2.,
                                      p_intersection.y / 2. - (road_width + sidewalk_width) / 2.),
                                Point(world.width - p_intersection.x, p_intersection.y), 'forest green'))  # building / grass

    # top left
    world.add(Painting(p_intersection / 2. + Point(0., world.height / 2.) + Point(-road_width, road_width) / 2,
                       Point(p_intersection.x, world.height - p_intersection.y), 'gray80'))
    world.add(Painting(p_intersection / 2. + Point(0., world.height / 2.) + Point(-(road_width + sidewalk_width), (road_width + sidewalk_width)) / 2,
                       Point(p_intersection.x, world.height - p_intersection.y), 'forest green'))

    # top right
    pos_topright = Point(world.width, world.height)
    world.add(Painting(pos_topright - (pos_topright - p_intersection) / 2. + Point(road_width, road_width) / 2, pos_topright - p_intersection, 'gray80'))
    world.add(RectangleBuilding(pos_topright - (pos_topright - p_intersection) / 2. + Point(road_width + sidewalk_width, road_width + sidewalk_width) / 2.,
                                pos_topright - p_intersection, 'forest green'))

    # adding lane markings to make things pretty
    lane_marker_length = 2.
    lane_marker_width = 0.2

    # north-south road
    for y in np.arange(0., world.height + 2. * lane_marker_length, 2. * lane_marker_length):
        world.add(Painting(Point(p_intersection.x, y), Point(lane_marker_length, lane_marker_width), 'white', heading=np.pi / 2))

    # east-west road
    for x in np.arange(0., world.width + 2. * lane_marker_length, 2. * lane_marker_length):
        world.add(Painting(Point(x, p_intersection.y), Point(lane_marker_length, lane_marker_width), 'white', heading=-np.pi))

    # small patch to cover the lane markings at the intersection
    world.add(Painting(p_intersection, Point(road_width, road_width), 'gray'))

    # stop lines
    world.add(Painting(p_intersection + Point(road_width / 4., -road_width / 2. - 0.15), Point(road_width / 2., 0.3), 'white'))
    world.add(Painting(p_intersection + Point(0., -1. - road_width / 2.), Point(0.3, 2.), 'white'))
    world.add(Painting(p_intersection + Point(-road_width / 4., road_width / 2. + 0.15), Point(road_width / 2., 0.3), 'white'))
    world.add(Painting(p_intersection + Point(0., 1. + road_width / 2.), Point(0.3, 2.), 'white'))
    world.add(Painting(p_intersection + Point(road_width / 2. + 0.15, road_width / 4.), Point(road_width / 2., 0.3), 'white', heading=np.pi / 2.))
    world.add(Painting(p_intersection + Point(1. + road_width / 2., 0.), Point(0.3, 2.), 'white', heading=np.pi / 2.))
    world.add(Painting(p_intersection + Point(-road_width / 2. - 0.15, -road_width / 4.), Point(road_width / 2., 0.3), 'white', heading=np.pi / 2.))
    world.add(Painting(p_intersection + Point(-1. - road_width / 2., 0.), Point(0.3, 2.), 'white', heading=np.pi / 2.))

    # cars
    # add ego vehicle (hardcoded inputs)
    # at stop sign at the intersection, accelerated and turns left
    u = np.zeros((2, world.time_vector.shape[0]))
    idx = random.randint(5, 10)
    u[0, idx + int(5 / dt):idx + int(11 / dt)] = 0.455
    u[1, idx + int(3 / dt):idx + int(12 / dt)] = 0.5
    car_ego = CarHardCoded(center=Point(p_intersection.x + road_width / 4., p_intersection.y - road_width / 2. - 3.), heading=np.pi / 2., input=u, color='blue')
    world.add(car_ego)

    # add AV (hardcoded inputs)
    u = np.zeros((2, world.time_vector.shape[0]))
    u[1, 0:int(10 / dt)] = 0.5
    u[1, int(10 / dt):-1] = 0.05  # just a little bit of acceleration to negate friction
    car_av = CarHardCoded(center=Point(p_intersection.x - road_width / 4., world.height - 25.), heading=- np.pi / 2., input=u)
    world.add(car_av)

    # render, just to get to see our work come to life
    world.render()

    return world
