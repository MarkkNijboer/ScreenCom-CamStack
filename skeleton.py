import pykinect
from pykinect import nui
from pykinect.nui import JointId

import pygame
from pygame.color import THECOLORS

import re
import itertools


class Skeleton():

    SKELETON_COLORS = [THECOLORS["red"],
                       THECOLORS["blue"],
                       THECOLORS["green"],
                       THECOLORS["orange"],
                       THECOLORS["purple"],
                       THECOLORS["yellow"],
                       THECOLORS["violet"]]
    LEFT_ARM = (JointId.ShoulderCenter,
                JointId.ShoulderLeft,
                JointId.ElbowLeft,
                JointId.WristLeft,
                JointId.HandLeft)
    RIGHT_ARM = (JointId.ShoulderCenter,
                 JointId.ShoulderRight,
                 JointId.ElbowRight,
                 JointId.WristRight,
                 JointId.HandRight)
    LEFT_LEG = (JointId.HipCenter,
                JointId.HipLeft,
                JointId.KneeLeft,
                JointId.AnkleLeft,
                JointId.FootLeft)
    RIGHT_LEG = (JointId.HipCenter,
                 JointId.HipRight,
                 JointId.KneeRight,
                 JointId.AnkleRight,
                 JointId.FootRight)
    SPINE = (JointId.HipCenter,
             JointId.Spine,
             JointId.ShoulderCenter,
             JointId.Head)

    skeletons = None
    people_in_view = {}
    skeleton_to_depth_image = None
    display_info = None
    kinect = None


    ##
    #   METHODS
    ##
    def __init__(self, kinect):
        self.kinect = kinect

    def process_skeleton(self, index, data, skel):
        self.display_info = pygame.display.Info()

        if index not in self.people_in_view:
            self.people_in_view[index] = {'handPositionRightRight' : [], 'handPositionRightLeft' : []};

        if float(skel['pHandR'].group(2)) > float(skel['pSpine'].group(2)):
            if len(self.people_in_view[index]['handPositionRightLeft']) > 2:
                # Hand moet ten op zichte van de vorige positie naar links zijn gegaan
                if float(skel['pHandR'].group(1)) < float(self.people_in_view[index]['handPositionRightLeft'][1].group(1)):
                    if len(self.people_in_view[index]['handPositionRightLeft']) < 10:
                        self.people_in_view[index]['handPositionRightLeft'].insert(0, skel['pHandR'])
                    else:
                        self.people_in_view[index]['handPositionRightLeft'].insert(0, skel['pHandR'])
                        self.people_in_view[index]['handPositionRightLeft'].pop()
                        # Hand moet de laatste tien posities minstens een schouderbreedte hebben afgelegd
                        if (float(self.people_in_view[index]['handPositionRightLeft'][9].group(1)) - float(skel['pHandR'].group(1))) > (float(skel['pShoulderR'].group(1)) - float(skel['pShoulderL'].group(1))):
                            # RunServer.sendToClient({"action" : "swipeleft"})
                            self.people_in_view[index]['handPositionRightLeft'] = []
                else:
                    self.people_in_view[index]['handPositionRightLeft'] = []
            else:
                self.people_in_view[index]['handPositionRightLeft'].insert(0, skel['pHandR'])


            if len(self.people_in_view[index]['handPositionRightRight']) > 2:
                if float(skel['pHandR'].group(1)) > float(self.people_in_view[index]['handPositionRightRight'][1].group(1)):
                    if len(self.people_in_view[index]['handPositionRightRight']) < 10:
                        self.people_in_view[index]['handPositionRightRight'].insert(0, skel['pHandR'])
                    else:
                        self.people_in_view[index]['handPositionRightRight'].insert(0, skel['pHandR'])
                        self.people_in_view[index]['handPositionRightRight'].pop()
                        if (float(skel['pHandR'].group(1))) - float(people_in_view[index]['handPositionRightRight'][9].group(1)) > (float(skel['pShoulderR'].group(1)) - float(skel['pShoulderL'].group(1))):
                            # RunServer.sendToClient({"action" : "swiperight"})
                            self.people_in_view[index]['handPositionRightRight'] = []
                else:
                    self.people_in_view[index]['handPositionRightRight'] = []
            else:
                self.people_in_view[index]['handPositionRightRight'].insert(0, skel['pHandR'])
        else:
            self.people_in_view[index]['handPositionRightLeft'] = []
            self.people_in_view[index]['handPositionRightRight'] = []


    def draw_skeletons(self, skeletons):
        for index, data in enumerate(self.skeletons):
            skel = {}
            p = data.SkeletonPositions[JointId.Head]
            skel['ps'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(p))
            pShoulderR = data.SkeletonPositions[JointId.ShoulderRight]
            skel['pShoulderR'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderR))
            pShoulderL = data.SkeletonPositions[JointId.ShoulderLeft]
            skel['pShoulderL'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderL))
            pShoulderCenter = data.SkeletonPositions[JointId.ShoulderCenter]
            skel['pShoulderCenter'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderCenter))
            pHandR = data.SkeletonPositions[JointId.HandRight]
            skel['pHandR'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pHandR))
            pSpine = data.SkeletonPositions[JointId.Spine]
            skel['pSpine'] = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pSpine))
            if(not skel['ps'] or not skel['pShoulderL'] or not skel['pShoulderR'] or not skel['pShoulderCenter'] or not skel['pHandR'] or not skel['pSpine'] or (skel['ps'].group(1) == "0.0" and skel['ps'].group(2) == "0.0") or (skel['pShoulderR'].group(1) == "0.0" and skel['pShoulderR'].group(2) == "0.0") or (skel['pShoulderCenter'].group(1) == "0.0" and skel['pShoulderCenter'].group(2) == "0.0") or (skel['pHandR'].group(1) == "0.0" and skel['pHandR'].group(2) == "0.0") or (skel['pSpine'].group(1) == "0.0" and skel['pSpine'].group(2) == "0.0")):
                continue;

            self.process_skeleton(index, data, skel)

            HeadPos = nui.SkeletonEngine.skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], self.display_info.current_w, self.display_info.current_h)
            self.draw_skeleton_data(data, index, self.SPINE, 10)
            pygame.draw.circle(self.kinect.get_screen(), self.SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)

            # drawing the limbs
            self.draw_skeleton_data(data, index, self.LEFT_ARM)
            self.draw_skeleton_data(data, index, self.RIGHT_ARM)
            self.draw_skeleton_data(data, index, self.LEFT_LEG)
            self.draw_skeleton_data(data, index, self.RIGHT_LEG)


    def get_skeletons(self):
        return self.skeletons


    def set_skeletons(self, skeletons):
        self.skeletons = skeletons


    def draw_skeleton_data(self, pSkelton, index, positions, width = 4):
        start_pos = pSkelton.SkeletonPositions[positions[0]]
        screen = self.kinect.get_screen()

        for position in itertools.islice(positions, 1, None):
            next_pos = pSkelton.SkeletonPositions[position.value]

            curstart = nui.SkeletonEngine.skeleton_to_depth_image(start_pos, self.display_info.current_w, self.display_info.current_h)
            curend = nui.SkeletonEngine.skeleton_to_depth_image(next_pos, self.display_info.current_w, self.display_info.current_h)

            pygame.draw.line(screen, self.SKELETON_COLORS[index], curstart, curend, width)

            start_pos = next_pos
