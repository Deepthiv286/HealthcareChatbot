import streamlit as st
from streamlit_chat import message
import speech_recognition as sr
# from bokeh.models.widgets import Button
# from bokeh.models import CustomJS
# from streamlit_bokeh_events import streamlit_bokeh_events

from Treatment import diseaseDetail
from functions import get_matching_symptoms, get_cooccurring_symptoms, get_next_cooccurring_symptoms


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

        # use the microphone as source for input.
        with sr.Microphone(device_index = 1) as source:

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


def submit(by_voice, text):
    if (text != ''):
        output = get_response(by_voice, text)

        st.session_state.generated.append(
            {"text": text, "is_user": True})
        st.session_state.generated.append({"text": output, "is_user": False})
        if st.session_state.input != '':
            st.session_state.input = ''


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
    # stt_button = Button(label="Speak", width=100)
    st.button('Speak', on_click=get_voice_response)
    # st.image(img)

# stt_button.js_on_event("button_click", CustomJS(code="""
#     var recognition = new webkitSpeechRecognition();
#     recognition.continuous = true;
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
#     stt_button,
#     events="GET_TEXT",
#     key="listen",
#     refresh_on_update=False,
#     override_height=75,
#     debounce_time=0)

# if result:
#     if "GET_TEXT" in result:
#         get_voice_response(result.get("GET_TEXT"))