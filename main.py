from moviepy.editor import *
import pygame as pg
import threading
import time
import numpy as np
import tkinter as tk
import glob
from functools import lru_cache

save_event = None
interrupted = False
clip_start = 0
start_time = 0

def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen."""
    a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pg.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pg.display.flip()


def custom_preview(
    screen,
    clip,
    first_frame,
    fps=15,
):
    """
    Displays the clip in a window, at the given frames per second
    (of movie) rate. It will avoid that the clip be played faster
    than normal, but it cannot avoid the clip to be played slower
    than normal if the computations are complex. In this case, try
    reducing the ``fps``.
    Parameters
    ----------
    fps
      Number of frames per seconds in the displayed video.
    audio
      ``True`` (default) if you want the clip's audio be played during
      the preview.
    audio_fps
      The frames per second to use when generating the audio sound.
    fullscreen
      ``True`` if you want the preview to be displayed fullscreen.
    """
    global interrupted
    global save_event

    imdisplay(first_frame, screen)

    t0 = time.time()
    step_size = 1.0 / fps
    frame_num = (t0 - start_time) / step_size
    print(f'step size: {step_size}\n #frames: {round(frame_num)}')
    # in_point = round(how_many_frames) * step_size
    in_point = round(frame_num)
    # print(in_point)
    AddKeyFrame(in_point,clip)
    for t in np.arange(step_size, clip.duration - 0.001 - clip_start, step_size):
        for clip_event in pg.event.get():
            if clip_event.type == pg.KEYDOWN:
                interrupted = True
                save_event = clip_event
                return
                # return result
        img = clip.get_frame(t - clip_start)
        t1 = time.time()
        time.sleep(max(0, t - (t1 - t0)))
        imdisplay(img, screen)


root = tk.Tk()
root.geometry('400x400')

res = (540, 960)
clips = []
clip_names = []
clips_first_frame = []
keyframes = {}
clip_keys = {122: 0, 120: 1, 99:2, 118:3, 98:4, 97:5, 115:6, 100:7, 102:8}


def LoadFolder(path):
    global clip_names
    global res
    clip_names += glob.glob(path + "/*.mov")
    clip_names += glob.glob(path + "/*.wmv")
    clip_names += glob.glob(path + "/*.mp4")
    clip_names += glob.glob(path + "/*.avi")
    for clip_i in range(len(clip_names)):
        clips.append(VideoFileClip(clip_names[clip_i], target_resolution=res, audio=False))
        # clips[clip_i] = clips[clip_i].subclip()
        clips_first_frame.append(clips[clip_i].get_frame(clip_start))


def AddKeyFrame(in_time, clip_object):
    keyframes[in_time] = clip_object
    print(f'Added frame {len(keyframes)} | in: {in_time} clip: {clip_object}')


def StartRecording():
    global start_time
    start_time = time.time()


def PlayRecording():
    global keyframes
    frame_rate = 30
    step = (1/frame_rate)
    duration = 300
    playhead = 0
    print('Playing Sequence')
    # for t in np.arange(0, duration - 0.001, step_size):
    for p in range(duration):
        if keyframes.get(p):
            print(f'{p}: play {keyframes[p]}')
            # custom_preview(screen=screen, clip=keyframes[p], first_frame=clips_first_frame[0], fps=frame_rate)
        time.sleep(step)

    # print (keyframes)
    # while playhead < duration:
    #     if keyframes.get(playhead):
    #         print(f'{playhead}: play {keyframes[playhead]}')
        # else:
        #     print(playhead)
        # playhead += step
    # for t in np.arange(0, duration, step):
    #     if t in keyframes:
    #         print(f'{t}: play {keyframes[t]}')


def HandleEvent(event):
    frame_rate = 30
    global clip_keys
    # print(event.key)
    if event.key in clip_keys:
        index = clip_keys[event.key]
        custom_preview(screen=screen, clip=clips[index], first_frame=clips_first_frame[index], fps=frame_rate)


videos_list = tk.Listbox(root)
LoadFolder("vid")
for i in range(len(clip_names)):
    videos_list.insert(i, clip_names[i][clip_names[i].rfind("\\")+1:])
    videos_list.pack()


pg.display.set_caption('Video')
screen = pg.display.set_mode(clips[0].size, 0)
pg.display.init()
pg.display.update()

rec_btn = tk.Button(root,text="Rec", command=StartRecording)
rec_btn.pack()
play_btn = tk.Button(root,text="Play", command=PlayRecording)
play_btn.pack()

while True:
    pg.display.update()
    root.update()
    events = pg.event.get()
    for event in events:
        if event.type == pg.KEYDOWN:
            # print(event.key)
            HandleEvent(event)
        if event.type == pg.QUIT:
            break
    if interrupted:
        interrupted = False
        HandleEvent(save_event)

pg.quit()
