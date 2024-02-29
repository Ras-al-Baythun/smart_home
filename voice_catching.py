import pyaudio
import wave
import audioop
from collections import deque
import whisper


def record_audio():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.
    """
    print("yeses maria22222")
    p = pyaudio.PyAudio()
    print("yeses maria")
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100,
                    input=True, frames_per_buffer=1024)

    print("Please speak. Recording will start when you speak.")
    audio2send = []
    cur_data = ''  # current chunk of audio data
    rel = 44100 / 1024
    slid_win = deque(maxlen=int(2 * rel))
    started = False
    threshold = 500  # sound level threshold

    while True:
        cur_data = stream.read(1024)
        slid_win.append(audioop.max(cur_data, 2))
        if sum([1 for x in slid_win if x > threshold]) > 0:
            if not started:
                print("Recording...")
                started = True
            audio2send.append(cur_data)
        elif started:
            print("Finished recording.")
            break

    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(audio2send))
    wf.close()

    return audio_transcribe("output.wav")


def audio_transcribe(audio_file):
    # Laden des Whisper-Modells
    model = whisper.load_model("tiny")
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    options = whisper.DecodingOptions(fp16=False, language="de")
    result = whisper.decode(model, mel, options)
    print(result)

    text = result.text.lower().strip(",").strip(".")
    return text
