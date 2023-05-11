# from flask import Flask, send_from_directory
# from flask_restful import Api, Resource, reqparse
# #from flask_cors import CORS #comment this on deployment
# from api.HelloApiHandler import HelloApiHandler
import streamlit as st
from Treatment import diseaseDetail
from streamlit_chat import message

message_history= []

# header=st.container()

# app = Flask(__name__, static_url_path='', static_folder='frontend/build')
# #CORS(app) #comment this on deployment
# api = Api(app)

st.set_page_config(
    page_title="HEALTHCARE CHATBOT",
    layout="wide",
)

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

st.sidebar.title("NLP Bot")

name = st.sidebar.text_input("Search for any disease", placeholder="Type Here ...")
result = ''
# display the name when the submit button is clicked
# .title() is used to get the input text string
if(st.sidebar.button('Submit')):
    result = name.title()
    
st.sidebar.title(diseaseDetail(result))

message("My message")

for message_ in message_history:
    message(message_)   # display all the previous message

placeholder = st.empty()  # placeholder for latest message
input_ = st.text_input("you:")
message_history.append(input_)

with placeholder.container():
    message(message_history[-1]) # display the latest message


# @app.route("/", defaults={'path':''})
# def serve(path):
#     return send_from_directory(app.static_folder,'index.html')

# api.add_resource(HelloApiHandler, '/flask/hello')
