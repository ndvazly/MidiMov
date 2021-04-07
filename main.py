from moviepy.editor import *
import pygame as pg
import time
import numpy as np
import tkinter as tk
import glob
import datetime

save_event = None
interrupted = False
# clip_start = 0
rec_start_time = 0
rec_end_time = 0


def ZeroPad(val):
    if val < 10:
        return "0" + str(val)
    return str(val)


def DoubleZeroPad(val):
    if val < 10:
        return "00" + str(val)
    if val < 100:
        return "0" + str(val)
    return str(val)


def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen."""
    a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pg.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pg.display.flip()


def custom_preview(
    screen_buf,
    clip_object,
    fps=15,
    add_key_frame=True,
    duration=None
):
    global interrupted
    global save_event

    clip = clip_object["clip"]
    imdisplay(clip_object["first_frame"], screen_buf)

    t0 = time.time()
    step_size = 1.0 / fps
    if duration is None:
        duration = clip.duration

    # print(in_point)
    if add_key_frame:
        frame_num = (t0 - rec_start_time) / step_size
        print(f'step size: {step_size}\n #frames: {round(frame_num)}')
        in_point = round(frame_num)
        AddKeyFrame(in_point, clip_object)

    for t in np.arange(step_size, duration - 0.001 - clip_object["in"], step_size):
        for clip_event in pg.event.get():
            if clip_event.type == pg.KEYDOWN:
                interrupted = True
                save_event = clip_event
                if add_key_frame:
                    out_time = time.time() - t0
                    SetKeyFrameDuration(in_point, out_time)
                return
        img = clip.get_frame(t - clip_object["in"])
        t1 = time.time()
        time.sleep(max(0, t - (t1 - t0)))
        imdisplay(img, screen_buf)


root = tk.Tk()
root.geometry('400x400')

res = (540, 960)
clips = []
keyframes = {}
clip_keys = {122: 0, 120: 1, 99:2, 118:3, 98:4, 97:5, 115:6, 100:7, 102:8}


def LoadFolder(path):
    global res
    clip_files = []
    clip_files += glob.glob(path + "/*.mov")
    clip_files += glob.glob(path + "/*.wmv")
    clip_files += glob.glob(path + "/*.mp4")
    clip_files += glob.glob(path + "/*.avi")
    for clip_i in range(len(clip_files)):
        new_clip = {"name": clip_files[clip_i]}
        new_clip["clip"] = VideoFileClip(new_clip["name"], target_resolution=res, audio=False)
        new_clip["in"] = 0
        new_clip["first_frame"] = new_clip["clip"].get_frame(new_clip["in"])
        clips.append(new_clip)


def AddKeyFrame(in_time, clip_object):
    keyframes[in_time] = {"clip_object": clip_object}
    # keyframes[in_time]["duration"] = 0.2
    keyframes[in_time]["duration"] = clip_object["clip"].duration
    print(f'Added frame {len(keyframes)} | in: {in_time} ')


def SetKeyFrameDuration(in_time, duration):
    print(f"SetKeyFrameDuration: {duration}")
    keyframes[in_time]["duration"] = duration


def StartRecording():
    global rec_start_time
    rec_start_time = time.time()


def StopRecording():
    global rec_end_time
    rec_end_time = time.time()


def PlayRecording():
    global keyframes
    frame_rate = 30
    step = (1/frame_rate)
    duration = (rec_end_time - rec_start_time) * frame_rate
    print(f'duration: {duration}')
    play_head = 0
    print('Playing Sequence')
    while play_head < duration:
        if keyframes.get(play_head):
            # print(f'{play_head}: play')
            t_before_clip = time.time()
            custom_preview(screen_buf=screen, clip_object=keyframes[play_head]["clip_object"],
                           fps=frame_rate, add_key_frame=False,
                           duration=keyframes[play_head]["duration"])
            frames_elapsed = (time.time() - t_before_clip) / step
            play_head += round(frames_elapsed)
        else:
            play_head += 1
            time.sleep(step)
    print('Sequence Ended')


def HandleEvent(event):
    frame_rate = 30
    global clip_keys
    # print(event.key)
    if event.key in clip_keys:
        index = clip_keys[event.key]
        custom_preview(screen_buf=screen, clip_object=clips[index], fps=frame_rate)


def SecondsToTimeCode(val, fps=30):
    frame_dur = 1 / fps
    time_str = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(val), "%H:%M:%S:%f")
    microseconds = int(time_str[time_str.rfind(':')+1:])
    frames = (microseconds / 1000000) / frame_dur
    time_code = time_str[:time_str.rfind(':')+1] + ZeroPad(round(frames))
    return time_code


def WriteEDL(file_name="test.edl"):
    frame_rate = 30
    frame_dur = 1/frame_rate
    cut_index = 1
    playhead = 0
    edl_str = "TITLE: azly EDL Test\n"
    edl_str += "FCM: NON-DROP FRAME\n\n"
    for k in keyframes:
        playhead_time = playhead / frame_rate
        cut_length_in_frames = (keyframes[k]["duration"] / frame_dur)
        cut_in = k*frame_dur
        delta = k - playhead
        if delta > 1:
            keyframe_time = k / frame_rate
            edl_str += f'{DoubleZeroPad(cut_index)}  BL       V     C        '
            edl_str += SecondsToTimeCode(0) + " "
            edl_str += SecondsToTimeCode(keyframe_time) + " "
            edl_str += SecondsToTimeCode(playhead_time) + " "
            edl_str += SecondsToTimeCode(playhead_time + keyframe_time) + " "
            edl_str += '\n\n'
            playhead += k
            playhead_time = playhead / frame_rate
            cut_index += 1

        edl_str += f'{DoubleZeroPad(cut_index)}  AX       V     C        '
        edl_str += SecondsToTimeCode(keyframes[k]["clip_object"]["in"]) + " "
        edl_str += SecondsToTimeCode(keyframes[k]["duration"]) + " "
        # print(f'playhead time:{playhead_time}')
        edl_str += SecondsToTimeCode(playhead_time) + " "
        edl_str += SecondsToTimeCode(playhead_time+keyframes[k]["duration"]) + " "
        edl_str += '\n'

        clip_name = keyframes[k]["clip_object"]["name"]
        clip_name = clip_name[clip_name.rfind('\\')+1:]
        edl_str += f'* FROM CLIP NAME: {clip_name}\n\n'
        playhead += cut_length_in_frames
        cut_index += 1
    print(edl_str)


videos_list = tk.Listbox(root)
LoadFolder("vid")
for i in range(len(clips)):
    vid_name = clips[i]["name"]
    vid_name = vid_name[vid_name.rfind("\\")+1:]
    videos_list.insert(i, vid_name)
    videos_list.pack()


pg.display.set_caption('Video')
screen = pg.display.set_mode(clips[0]["clip"].size, 0)
pg.display.init()
pg.display.update()

seq_frame = tk.LabelFrame(root)
rec_btn = tk.Button(seq_frame, text="Rec", command=StartRecording).grid(row=0, column=0)
stop_btn = tk.Button(seq_frame, text="Stop", command=StopRecording).grid(row=0, column=1)
play_btn = tk.Button(seq_frame, text="Play", command=PlayRecording).grid(row=0, column=2)
edl_btn = tk.Button(seq_frame, text="EDL", command=WriteEDL).grid(row=0, column=3)
seq_frame.pack()


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
