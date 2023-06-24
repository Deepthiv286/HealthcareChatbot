import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
# from streamlit_bokeh_events import streamlit_bokeh_events
from audiorecorder import audiorecorder
from pydub import AudioSegment
import pyaudio
# from queue import Queue
# from threading import Thread

import base64
import subprocess
import json
from vosk import Model, KaldiRecognizer
import time
# import sys
# sys.path.append('ffmpeg-6.0')

from Treatment import diseaseDetail
from functions import get_matching_symptoms, get_cooccurring_symptoms, get_next_cooccurring_symptoms


# messages = Queue()
# recordings = Queue()


# Initialize the recognizer
r = sr.Recognizer()


st.set_page_config(
    page_title="HEALTHCARE CHATBOT",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("NLP Bot")


disease = st.sidebar.text_input(
    "Search for any disease", placeholder="Type Here ...", key="sidebar_input")


if (st.sidebar.button('Submit')):
    result = diseaseDetail(disease.title())
    st.sidebar.title(result)


if 'generated' not in st.session_state:
    st.session_state['generated'] = [
        {"text": "Please enter symptoms separated by comma(,)", "is_user": False}]


if 'input' not in st.session_state:
    st.session_state.input = ''


if 'step' not in st.session_state:
    st.session_state.step = 1


if 'count' not in st.session_state:
    st.session_state.count = 0


if 'start' not in st.session_state:
    st.session_state.start = False


def get_response(by_voice, text):
    response = ''
    if st.session_state.step == 1:
        response = get_matching_symptoms(text, by_voice)
        if response != []:
            st.session_state.step += 1
        else:
            response = "Please enter symptoms separated by comma(,)"
    elif st.session_state.step == 2:
        [response, out_of_bound] = get_cooccurring_symptoms(text)
        if out_of_bound == False:
            st.session_state.step += 1
    else:
        [response, out_of_bound, count] = get_next_cooccurring_symptoms(
            text.lower().split(), st.session_state.count)
        if out_of_bound == False:
            st.session_state.count += 1
        elif st.session_state.count != count:
            st.session_state.count = count

    return response


def send():
    submit('', st.session_state.input)


def get_voice_response():
    # submit('by_voice', text.lower())
    try:
        # MICROPHONE_INDEX = 0
        # for index, name in enumerate(sr.Microphone.list_microphone_names()):
        #     if(name.lower() == 'microphone'):
        #         MICROPHONE_INDEX = index
        #     print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

        # # use the microphone as source for input.
        with sr.Microphone() as source:

        # m = None
        # for device_index in sr.Microphone.list_working_microphones():
        #     m = sr.Microphone(device_index=device_index)
        #     break
        # else:
        #     raise Error("No working microphones found!")

        # if m is not None:
        #     print("Mic ready")
        #     with m as source:
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
            r.adjust_for_ambient_noise(source, duration=1)

            # listens for the user's input
            audio = r.listen(source)

            # Using google to recognize audio
            text = r.recognize_google(audio)
            text = text.lower()

            print("Did you say ", text)
            submit('by_voice', text)

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("unknown error occurred")


# def get_voice_response1():
#     if st.session_state.start == False:
#         st.session_state.start = True
#         start_recording()
#     else:
#         st.session_state.start = False
#         stop_recording()

# def start_recording():
#     messages.put(True)

#     record = Thread(target=record_microphone)
#     record.start()
#     transcribe = Thread(target=speech_recognition, args=())
#     transcribe.start()

# def stop_recording():
#     messages.get()



# def record_microphone(chunk=1024):
#     CHANNELS = 1
#     FRAME_RATE = 16000
#     RECORD_SECONDS = 20
#     AUDIO_FORMAT = pyaudio.paInt16
#     SAMPLE_SIZE = 2

#     p = pyaudio.PyAudio()

#     stream = p.open(format=AUDIO_FORMAT,
#                     channels=CHANNELS,
#                     rate=FRAME_RATE,
#                     input=True,
#                     input_device_index=2,
#                     frames_per_buffer=chunk)

#     frames = []

#     while not messages.empty():
#         data = stream.read(chunk)
#         frames.append(data)
#         if len(frames) >= (FRAME_RATE * RECORD_SECONDS) / chunk:
#             recordings.put(frames.copy())
#             frames = []

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

# def speech_recognition():
#     model = Model(model_name="vosk-model-en-us-0.22")
#     rec = KaldiRecognizer(model, 16000)
#     rec.SetWords(True)
    
#     while not messages.empty():
#         frames = recordings.get()
        
#         rec.AcceptWaveform(b''.join(frames))
#         result = rec.Result()
#         text = json.loads(result)["text"]
        
#         cased = subprocess.check_output('python recasepunc/recasepunc.py predict recasepunc/checkpoint', shell=True, text=True, input=text)
#         print('cased', cased)


def submit(by_voice, text):
    if (text != ''):
        output = get_response(by_voice, text)

        st.session_state.generated.append(
            {"text": text, "is_user": True})
        st.session_state.generated.append({"text": output, "is_user": False})
        if st.session_state.input != '':
            st.session_state.input = ''


st.title("Disease Predictor Chatbot")


for i in range(len(st.session_state['generated'])):
    message(st.session_state["generated"][i]["text"],
            is_user=st.session_state["generated"][i]["is_user"], key=str(i))


col1, col2 = st.columns([20, 3])
with col1:
    st.text_input("You: ", key="input", on_change=send)
with col2:
    # content = """
    # <a href='#' id='Image 1'><img width='20px' style='margin-top: 40px' src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZfUZT8VfaBNVtHLy7m2dbPVTE4loEDAOYib7pZFC_J5beuErGkBIncAckBGYFdz9sRHM&usqp=CAU'></a>
    # """
    # p = pyaudio.PyAudio()
    # audio = audiorecorder("Click to record", "Recording...")
    # stt_button = Button(label="Speak", width=100, button_type='success')
    st.button('Speak', on_click=get_voice_response)
    # st.image(img)

# stream = p.open(
#    format=pyaudio.paInt16,
#    channels=1,
#    rate=16000,
#    input=True,
#    frames_per_buffer=3200
# )

# data = stream.read(3200)
# data = base64.b64encode(data).decode("utf-8")
# json_data = json.dumps({"audio_data":str(data)})
# print('json_data', json_data)
# if json_data:
#     result = json.loads(json_data)['audio_data']

# if json_data and json.loads(json_data)['message_type']=='FinalTranscript':
#     print(result)
#     st.write(result)

# if len(audio) > 0:
#     # To play audio in frontend:
#     st.audio(audio.tobytes())
    
#     # To save audio to a file:
#     wav_file = open("audio.mp3", "wb")
    
#     wav_file.write(audio.tobytes())
#     # print(audio.tobytes())
#     sound = AudioSegment.from_mp3("audio.mp3")
#     sound.export("transcript.wav", format="wav")


#     # transcribe audio file                                                         
#     AUDIO_FILE = "transcript.wav"

#     # use the audio file as the audio source                                        
#     r = sr.Recognizer()
#     with sr.AudioFile(AUDIO_FILE) as source:
#             audio = r.record(source)  # read the entire audio file                  

#             print("Transcription: " + r.recognize_google(audio))

# stt_button.js_on_event("button_click", CustomJS(code="""
#     var recognition = new webkitSpeechRecognition();
#     recognition.continuous = false;
#     recognition.interimResults = true;
 
#     recognition.onresult = function (e) {
#         var value = "";
#         for (var i = e.resultIndex; i < e.results.length; ++i) {
#             if (e.results[i].isFinal) {
#                 value += e.results[i][0].transcript;
#             }
#         }
#         if ( value != "") {
#             document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
#         }
#     }
#     recognition.start();
#     """))

# result = streamlit_bokeh_events(
#     bokeh_plot = stt_button,
#     events="GET_TEXT",
#     key="listen",
#     refresh_on_update=False,
#     override_height=75,
#     debounce_time=0)

# if result:
#     if "GET_TEXT" in result:
#         st.write(result.get("GET_TEXT"))