import pykinect
from pykinect import nui
from pykinect.nui import JointId

import pygame
from pygame.color import THECOLORS


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
    people_in_view = []


    ##
    #   METHODS
    ##
    def process_skeleton(index, data):
        if index not in people_in_view:
            self.people_in_view[index] = {'handPositionRightRight' : [], 'handPositionRightLeft' : []};

        if float(pHandR.group(2)) > float(pSpine.group(2)):
            if len(self.people_in_view[index]['handPositionRightLeft']) > 2:
                # Hand moet ten op zichte van de vorige positie naar links zijn gegaan
                if float(pHandR.group(1)) < float(self.people_in_view[index]['handPositionRightLeft'][1].group(1)):
                    if len(self.people_in_view[index]['handPositionRightLeft']) < 10:
                        self.people_in_view[index]['handPositionRightLeft'].insert(0, pHandR)
                    else:
                        self.people_in_view[index]['handPositionRightLeft'].insert(0, pHandR)
                        self.people_in_view[index]['handPositionRightLeft'].pop()
                        # Hand moet de laatste tien posities minstens een schouderbreedte hebben afgelegd
                        if (float(self.people_in_view[index]['handPositionRightLeft'][9].group(1)) - float(pHandR.group(1))) > (float(pShoulderR.group(1)) - float(pShoulderL.group(1))):
                            RunServer.sendToClient({"action" : "swipeleft"})
                            self.people_in_view[index]['handPositionRightLeft'] = []
                else:
                    self.people_in_view[index]['handPositionRightLeft'] = []
            else:
                self.people_in_view[index]['handPositionRightLeft'].insert(0, pHandR)


            if len(self.people_in_view[index]['handPositionRightRight']) > 2:
                if float(pHandR.group(1)) > float(self.people_in_view[index]['handPositionRightRight'][1].group(1)):
                    if len(self.people_in_view[index]['handPositionRightRight']) < 10:
                        self.people_in_view[index]['handPositionRightRight'].insert(0, pHandR)
                    else:
                        self.people_in_view[index]['handPositionRightRight'].insert(0, pHandR)
                        self.people_in_view[index]['handPositionRightRight'].pop()
                        if (float(pHandR.group(1))) - float(people_in_view[index]['handPositionRightRight'][9].group(1)) > (float(pShoulderR.group(1)) - float(pShoulderL.group(1))):
                            RunServer.sendToClient({"action" : "swiperight"})
                            self.people_in_view[index]['handPositionRightRight'] = []
                else:
                    self.people_in_view[index]['handPositionRightRight'] = []
            else:
                self.people_in_view[index]['handPositionRightRight'].insert(0, pHandR)
        else:
            self.people_in_view[index]['handPositionRightLeft'] = []
            self.people_in_view[index]['handPositionRightRight'] = []


    def draw_skeletons(skeletons):
        for index, data in enumerate(skeletons):
            p = data.SkeletonPositions[JointId.Head]
            ps = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(p))
            pShoulderR = data.SkeletonPositions[JointId.ShoulderRight]
            pShoulderR = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderR))
            pShoulderL = data.SkeletonPositions[JointId.ShoulderLeft]
            pShoulderL = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderL))
            pShoulderCenter = data.SkeletonPositions[JointId.ShoulderCenter]
            pShoulderCenter = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pShoulderCenter))
            pHandR = data.SkeletonPositions[JointId.HandRight]
            pHandR = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pHandR))
            pSpine = data.SkeletonPositions[JointId.Spine]
            pSpine = re.search("\<x\=([0-9\.\-]+)\, y\=([0-9\.\-]+)\, z\=([0-9\.\-]+)",str(pSpine))
            if(not ps or not pShoulderL or not pShoulderR or not pShoulderCenter or not pHandR or not pSpine or (ps.group(1) == "0.0" and ps.group(2) == "0.0") or (pShoulderR.group(1) == "0.0" and pShoulderR.group(2) == "0.0") or (pShoulderCenter.group(1) == "0.0" and pShoulderCenter.group(2) == "0.0") or (pHandR.group(1) == "0.0" and pHandR.group(2) == "0.0") or (pSpine.group(1) == "0.0" and pSpine.group(2) == "0.0")):
                continue;

            process_skeleton(index, data)

            HeadPos = skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], dispInfo.current_w, dispInfo.current_h)
            draw_skeleton_data(data, index, SPINE, 10)
            pygame.draw.circle(self._PyO, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)

            # drawing the limbs
            draw_skeleton_data(data, index, LEFT_ARM)
            draw_skeleton_data(data, index, RIGHT_ARM)
            draw_skeleton_data(data, index, LEFT_LEG)
            draw_skeleton_data(data, index, RIGHT_LEG)
