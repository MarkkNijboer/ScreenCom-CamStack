import thread
import threading
import ctypes

import pykinect
from pykinect import nui

import pygame
from pygame.color import THECOLORS

from skeleton import Skeleton


class ScreenComKinect(threading.Thread):

    screen = None
    video_display = True
    screen_lock = None
    skeleton = None
    done = False
    kinect_event = pygame.USEREVENT
    Py_ssize_t = None
    _PyObject_AsWriteBuffer = None


    ##
    #   INITALIZATION
    ##
    def init(self):
        pygame.init()
        self._init_screen()
        self._init_kinect()
        self._init_surface()

        self.skeleton = Skeleton()

    def _init_screen(self):
        depth_winsize = 320, 240
        video_winsize = 640, 480

        self.screen_lock = thread.allocate()
        self.screen = pygame.display.set_mode(depth_winsize, 0, 16)
        pygame.display.set_caption('ScreenCom CamStack')
        self.screen.fill(THECOLORS['black'])

    def _init_kinect(self):
        self.kinect = nui.Runtime()
        self.kinect.skeleton_engine.enabled = True
        self.kinect.skeleton_frame_ready += self.post_frame

        self.kinect.depth_frame_ready += self.frame_ready
        self.kinect.video_frame_ready += self.frame_ready

        self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
        self.kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

    def _init_surface(self):
        if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
           self.Py_ssize_t = ctypes.c_int
        elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
           self.Py_ssize_t = ctypes.c_int64
        else:
           raise TypeError("Cannot determine type of Py_ssize_t")

        self._PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
        self._PyObject_AsWriteBuffer.restype = ctypes.c_int
        self._PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
                                          ctypes.POINTER(ctypes.c_void_p),
                                          ctypes.POINTER(self.Py_ssize_t)]



    ##
    #   METHODS
    ##
    def frame_ready(self, frame):
        if self.video_display:
            return

        with self.screen_lock:
            address = self.surface_to_array(self.screen)
            frame.image.copy_bits(address)
            arr2d = None
            if self.video_display:
                arr2d = (pygame.surfarray.pixels2d(self.screen) >> 3) & 4095
            else:
                arr2d = (pygame.surfarray.pixels2d(self.screen) >> 7) & 255

            pygame.surfarray.blit_array(self.screen, arr2d)
            print(self.skeleton.get_skeletons())
            if self.skeleton.get_skeletons() is not None:
                self.skeleton.draw_skeletons()
            pygame.display.update()



    def surface_to_array(self, surface):
       buffer_interface = surface.get_buffer()
       address = ctypes.c_void_p()
       size = self.Py_ssize_t()
       self._PyObject_AsWriteBuffer(buffer_interface,
                              ctypes.byref(address), ctypes.byref(size))
       bytes = (ctypes.c_byte * size.value).from_address(address.value)
       bytes.object = buffer_interface
       return bytes


    def post_frame(self, frame):
        try:
            pygame.event.post(pygame.event.Event(self.kinect_event, skeletons = frame.SkeletonData))
        except:
            # event queue full
            pass



    ##
    #   MAIN LOOP
    ##
    def run(self):
        while not self.done:
            e = pygame.event.wait()
            if e.type == pygame.QUIT:
                self.done = True
                break
            elif e.type == self.kinect_event:
                self.skeleton.set_skeletons(e.skeletons)
                self.skeleton.draw_skeletons(self.skeleton.get_skeletons())
                pygame.display.update()
