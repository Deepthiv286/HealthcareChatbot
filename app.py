import streamlit as st
from streamlit_chat import message
import random

from Treatment import diseaseDetail
from functions import get_matching_symptoms

st.set_page_config(
    page_title="HEALTHCARE CHATBOT",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("NLP Bot")

if 'sidebar_input' not in st.session_state:
    st.session_state.sidebar_input = ''

st.sidebar.text_input(
    "Search for any disease", placeholder="Type Here ...", key="sidebar_input")

# display the name when the submit button is clicked
# .title() is used to get the input text string
if (st.sidebar.button('Submit')):
    result = diseaseDetail(st.session_state.sidebar_input)
    st.session_state.sidebar_input = ''
    st.sidebar.title(result)


if 'generated' not in st.session_state:
    st.session_state['generated'] = [{"text":"Please enter symptoms separated by comma(,)", "is_user": False}]

if 'input' not in st.session_state:
    st.session_state.input = ''


def query(payload):
	return "Hello\n"+ str(random.randint(0, 50))


def submit():
    output = get_matching_symptoms(st.session_state.input)

    st.session_state.generated.append({"text": st.session_state.input, "is_user": True})
    st.session_state.generated.append({"text": output, "is_user": False})
    st.session_state.input = ''


if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])):
        message(st.session_state["generated"][i]["text"], is_user=st.session_state["generated"][i]["is_user"], key=str(i))


st.text_input("You: ", key="input", on_change=submit)
