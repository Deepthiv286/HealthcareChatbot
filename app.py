# from flask import Flask, send_from_directory
# from flask_restful import Api, Resource, reqparse
# #from flask_cors import CORS #comment this on deployment
# from api.HelloApiHandler import HelloApiHandler
import streamlit as st
# from Treatment import diseaseDetail

# header=st.container()

# app = Flask(__name__, static_url_path='', static_folder='frontend/build')
# #CORS(app) #comment this on deployment
# api = Api(app)

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

st.sidebar.title("NLP Bot")

name = st.sidebar.text_input("Search for any disease", placeholder="Type Here ...")
 
# display the name when the submit button is clicked
# .title() is used to get the input text string
if(st.sidebar.button('Submit')):
    result = name.title()
    # st.sidebar.title(diseaseDetail(result))

# @app.route("/", defaults={'path':''})
# def serve(path):
#     return send_from_directory(app.static_folder,'index.html')

# api.add_resource(HelloApiHandler, '/flask/hello')
