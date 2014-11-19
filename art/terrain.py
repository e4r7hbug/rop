from collections import OrderedDict
from math import sin, cos

from opc.colormap import Colormap
from opc.colors import rgb
from opc.hue import hsvToRgb, getHueGen
from opc.matrix import OPCMatrix
from opc.utils.prof import timefunc

from utils.diamondsquare import DiamondSquareAlgorithm

import logging

SCALE=16
CENTERZONE = 4

class Art(object):

    description = "Traverse procedurally generated terrain"

    def __init__(self, matrix):
        self.width = matrix.width*SCALE
        self.height = matrix.height*SCALE

        self.diamond = DiamondSquareAlgorithm(self.width, self.height, (matrix.width+matrix.height)/4)
        self.matrix = OPCMatrix(self.width, self.height, None, zigzag=matrix.zigzag)
        self.colormap = Colormap(palette=OrderedDict([
                (rgb["NavyBlue"], 20),
                (rgb["blue"], 15),
                (rgb["yellow3"], 5),
                (rgb["LawnGreen"], 10),
                (rgb["ForestGreen"], 20),
                (rgb["gray50"], 15),
                (rgb["snow1"], 5),
            ]))

        self.diamond.generate()
        self.diamond.translate(self.matrix, colormap=self.colormap)
        self.matrix.soften(ratio=.5)

        self.theta = 0
        self.radius = 0

    def start(self, matrix):
        logging.debug("super matrix size (%d, %d)"%(self.matrix.width,self.matrix.height))
        matrix.setFirmwareConfig(nointerp=True)

    def refresh(self, matrix):
        # XXX:
        # The change in angle per frame increases as we get closer to the
        # center of the matrix:
        #  - when radius is max, then deltatheta is about .005 radians.
        #  - when radius is min, then deltatheta is about .1 radians.
        deltatheta = 0.004
        self.theta += deltatheta
        self.radius -= 0.05

        if self.radius<CENTERZONE:
            self.radius = (self.width+self.height)/4

        x = self.width/2 + self.radius * sin(self.theta)
        y = self.height/2 + self.radius * cos(self.theta)

        logging.debug("visit (%d, %d)"%(x,y))
        
        matrix.copy(self.matrix, x, y)

    def interval(self):
        return 60
