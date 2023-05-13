# from flask import Flask, send_from_directory
# from flask_restful import Api, Resource, reqparse
# #from flask_cors import CORS #comment this on deployment
# from api.HelloApiHandler import HelloApiHandler
import streamlit as st
from Treatment import diseaseDetail
from streamlit_chat import message
import random

message_history = []

# header=st.container()

# app = Flask(__name__, static_url_path='', static_folder='frontend/build')
# #CORS(app) #comment this on deployment
# api = Api(app)

st.set_page_config(
    page_title="HEALTHCARE CHATBOT",
    layout="wide",
    initial_sidebar_state="expanded",
)

# if 'sidebar_state' not in st.session_state:
#     st.session_state.sidebar_state = 'expanded'

# st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

st.sidebar.title("NLP Bot")

name = st.sidebar.text_input(
    "Search for any disease", placeholder="Type Here ...")

# display the name when the submit button is clicked
# .title() is used to get the input text string
if (st.sidebar.button('Submit')):
    result = diseaseDetail(name.title())
    st.sidebar.title(result)


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

def query(payload):
	return "Hello"+ str(random.randint(0, 50))

def get_text():
    input_text = st.text_input("You: ", key="input")
    return input_text 

st.session_state.generated.append({"text":"Please enter symptoms separated by comma(,)", "is_user": False})

user_input = get_text()

if user_input:
    output = query({
        "inputs": {
            "generated_responses": st.session_state.generated,
            "text": user_input,
        },"parameters": {"repetition_penalty": 1.33},
    })

    st.session_state.generated.append({"text": user_input, "is_user": True})
    st.session_state.generated.append({"text": output, "is_user": False})

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i].text, is_user=st.session_state["generated"][i].is_user, key=str(i))

# message_history.append(
#     {"text": "Please enter symptoms separated by comma(,)", "is_user": False})


# # placeholder = st.empty()  # placeholder for latest message
# input_ = st.text_input("you:", key="input")

# if (input_):
#     message_history.append({"text": input_, "is_user": True})
#     message_history.append({"text": "Hello", "is_user": False})

# # with placeholder.container():
# #     # display the latest message
# #     message(message_history[-1]["text"], is_user= message_history[-1]["is_user"])

# for i in range(len(message_history)-1,-1,-1):
#         st.write(i)
#         message(message_history[i]["text"], is_user=message_history[i]["is_user"], key=str(i))

# @app.route("/", defaults={'path':''})
# def serve(path):
#     return send_from_directory(app.static_folder,'index.html')

# api.add_resource(HelloApiHandler, '/flask/hello')
