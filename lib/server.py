# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import base64
import datetime
import io
from zipfile import ZipFile 
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash
import dash_table
from flask import Flask, send_file, send_from_directory
from dash.dependencies import Input, State, Output
import sys
import importlib
from lib import recommender, db
from lib.pages.index import get_layout
from lib.dash_app import app, server
import os


@server.route("/health")
def health():
    return "I am fine."
    # return "hello"

@server.after_request
def add_header(response):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
    # response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@server.route("/download")
def download_csv():

    def format_matches():
        match_csv = pd.read_csv('./downloads/matches.csv')
        k = match_csv['mentor_name']+'-'+match_csv['mentee_name']
        match_csv['match']=k
        new_cols = ['match','mentor_name','mentor_ethnicity','mentor_address','mentor_id','mentee_name','mentee_ethnicity', 'mentee_address', 'mentee_id']
        new_matches=match_csv[new_cols]
        new_matches.to_csv('./downloads/matches.csv')
        matched_mentors = new_matches['mentor_name'].tolist()
        matched_mentees = new_matches['mentee_name'].tolist()
        return matched_mentors, matched_mentees
    
    def format_mentees(matched):
        matched_mentees = matched
        mentees_csv = pd.read_csv('./downloads/remaining-mentees.csv')
        new_cols = ['mentee_name','mentee_ethnicity','mentee_address']
        new_mentees = mentees_csv[new_cols]
        new_mentees.drop_duplicates(subset="mentee_name", keep="first", inplace=True)
        for r in matched_mentees:
            new_mentees = new_mentees[new_mentees.mentee_name != r]
        new_mentees.columns = ['name', 'ethnicity', 'address']
        new_mentees.to_csv('./downloads/remaining-mentees.csv')

    def format_mentors(matched):
        matched_mentors = matched
        mentors_csv = pd.read_csv('./downloads/remaining-mentors.csv')
        new_cols = ['mentor_name','mentor_ethnicity','mentor_address']
        new_mentors = mentors_csv[new_cols]
        new_mentors.drop_duplicates(subset="mentor_name", keep="first", inplace=True)
        new_mentors.to_csv('./downloads/remaining-mentors.csv')
        for r in matched_mentors:
            new_mentors = new_mentors[new_mentors.mentor_name != r]
        new_mentors.columns = ['name', 'ethnicity', 'address']
        new_mentors.to_csv('./downloads/remaining-mentors.csv')

    try:
        matched_mentors, matched_mentees = format_matches()
        format_mentees(matched_mentees)
        format_mentors(matched_mentors)
    except:
        
        return app.index()

    try:
        directory = "./downloads"
        file_paths = []

        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
        
        data = io.BytesIO()

        with ZipFile(data,mode="w") as zip:
            for file in file_paths: 
                zip.write(file)
        data.seek(0)

        
        return send_file(
            data, 
            mimetype="application/zip", 
            attachment_filename="download.zip",
            as_attachment=True,
        ) 

    except:
        return "Download is not working!"

def clear_csv():
    open('./downloads/matches.csv', 'w').close()
    open('./downloads/remaining-mentees.csv', 'w').close()
    open('./downloads/remaining-mentors.csv', 'w').close()

@app.callback(
    Output("page-content", "children"), [dash.dependencies.Input("url", "pathname")]
)
def handle_url_change(pathname):
    if pathname is None or pathname == "" or pathname == "/":
        clear_csv()
        return get_layout()
    else:
        page_module = importlib.import_module(pathname.replace("/", "."), "lib.pages")
        clear_csv()
        return page_module.get_layout()



if __name__ == "__main__":
    # sanity_check()
    db.init_db()
    app.run_server(host="0.0.0.0", debug=True)
