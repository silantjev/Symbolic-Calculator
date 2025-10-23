def time_sec(sec : int) -> int:
    minutes = sec // 60
    sec %= 60
    hours = minutes // 60
    minutes %= 60
    return sec + 100*minutes + 10000*hours

if __name__ == '__main__':
    second_arr = [8, 9, 89, 210, 211, 212, 267, 480, 480]
    for s in second_arr:
        print(f"{s=} -> {time_sec(s)}")
