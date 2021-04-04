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
    audio=False,
    audio_fps=22050,
    audio_buffersize=3000,
    audio_nbytes=2,
    fullscreen=False,
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

    flags = 0

    # compute and splash the first image
    # screen = pg.display.set_mode(clip.size, flags)

    # audio = audio and (clip.audio is not None)
    #
    # if audio:
    #     # the sound will be played in parrallel. We are not
    #     # parralellizing it on different CPUs because it seems that
    #     # pygame and openCV already use several cpus it seems.
    #
    #     # two synchro-flags to tell whether audio and video are ready
    #     video_flag = threading.Event()
    #     audio_flag = threading.Event()
    #     # launch the thread
    #     audiothread = threading.Thread(
    #         target=clip.audio.preview,
    #         args=(audio_fps, audio_buffersize, audio_nbytes, audio_flag, video_flag),
    #     )
    #     audiothread.start()

    # img = clip.get_frame(0)
    # img = first_frame;
    imdisplay(first_frame, screen)
    # if audio:  # synchronize with audio
    #     video_flag.set()  # say to the audio: video is ready
    #     audio_flag.wait()  # wait for the audio to be ready

    result = []

    t0 = time.time()
    for t in np.arange(1.0 / fps, clip.duration - 0.001, 1.0 / fps):

        img = clip.get_frame(t)

        for clip_event in pg.event.get():
            if clip_event.type == pg.KEYDOWN:
                interrupted = True
                save_event = clip_event
                return result

        t1 = time.time()
        time.sleep(max(0, t - (t1 - t0)))
        imdisplay(img, screen)


root = tk.Tk()
root.geometry('400x400')

res = (540, 960)
clips = []
clip_names = []
clips_first_frame = []
# clip_keys = {97: 0, 98: 1, 99: 2, 100: 3, 101: 4, 102: 5}
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
        clips_first_frame.append(clips[clip_i].get_frame(0))


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
# pg.init()

# elif event.type == pg.MOUSEBUTTONDOWN:
# x, y = pg.mouse.get_pos()
# rgb = img[y, x]
# result.append({"time": t, "position": (x, y), "color": rgb})
# print(
#     "time, position, color : ",
#     "%.03f, %s, %s" % (t, str((x, y)), str(rgb)),
# )
