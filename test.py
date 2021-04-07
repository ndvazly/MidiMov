import datetime


def DoubleZeroPad(val):
    if val < 10:
        return "00" + str(val)
    if val < 100:
        return "0" + str(val)
    return str(val)


def SecondsToTimeCode(val, fps=30):
    frame_dur = 1 / fps
    time_str = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(val), "%H:%M:%S:%f")
    print(f'original: {time_str}')
    microseconds = int(time_str[time_str.rfind(':')+1:])
    frames = (microseconds / 1000000) / frame_dur
    time_code = time_str[:time_str.rfind(':')+1] + str(round(frames))
    return time_code


print(SecondsToTimeCode(517.365467893))

# print(f'microseconds: {microseconds}')
# print(f'sec: {(microseconds / 1000000)}')
# print(f'frames: {round(frames)}')
