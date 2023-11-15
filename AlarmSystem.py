import simpleaudio as sa


def play_alarm_sound(wav_file):
    wave_obj = sa.WaveObject.from_wave_file(wav_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def main():
    wav_file = '/Users/sreekarpalla/IdeaProjects/DormSecurity/Resources/burglarAlarm.wav'
    while True:
        play_alarm_sound(wav_file)


if __name__ == "__main__":
    main()
