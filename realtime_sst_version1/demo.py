import os
import wave
import pyaudio
import requests


# FastAPI server port 
api_url = "http://172.21.10.105:7778/transcribe/"

# Define your constants here (NEON_GREEN and RESET_COLOR)
NEON_GREEN = "\033[1;32m"
RESET_COLOR = "\033[0m"


def record_chunk(p, stream, file_path, chunk_length=2):
    frames = []
    for _ in range(0, int(16000 / 2048 * chunk_length)):
        data = stream.read(2048, exception_on_overflow=False)
        frames.append(data)
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def main2():
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)

    accumulated_transcription = ""

    try:
        while True:
            chunk_file = "tempchunk.wav"
            record_chunk(p, stream, chunk_file)
            
            with open(chunk_file, "rb") as f:
                file = {"file": f}
                response = requests.post(api_url, files=file)
                print(response)
            if response.status_code == 200:
                transcription = response.json()
                print(transcription)
                if "text" in transcription:
                    print(NEON_GREEN + transcription["text"] + RESET_COLOR)
                    accumulated_transcription += transcription["text"] + " "
                else:
                    print("NO voice :", transcription)
            else:
                print("Error :", response.status_code)
            
            os.remove(chunk_file)     

    except KeyboardInterrupt:
        print("Stop Record!")
        with open("history.txt", "w") as log_file:
            log_file.write(accumulated_transcription)

        print("Log:" + accumulated_transcription)
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main2()
