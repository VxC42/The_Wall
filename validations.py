from flask import Flask, request, redirect, render_template, session, flash
import re

NAME = re.compile(r'^[a-zA-z]+$')
EMAIL = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASSWORD = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')

def formIsValid(client):
    errors=[]
    isValid=True
    if len(client['first_name'])<2:
        errors.append('Please enter your first name.')
        isValid=False
    else:
        session['first_name']=str(client['first_name'])
    if len(client['last_name'])<2:
        errors.append('Please enter your first name.')
        isValid=False
    else:
        session['last_name']=str(client['last_name'])
    if len(client['email'])<1:
        errors.append("Please enter an email.")
        isValid = False
    elif not re.match(EMAIL, client['email']):
        errors.append("Not a valid Email address.")
        isValid = False
    else:
        session['email']=str(client['email'])
    if len(client['password'])<8:
        errors.append('Password must be atleast 8 characters.')
        isValid=False
    else:
        session['password']=str(client['password'])
    if client['password'] != client['confirm_password']:
        errors.append('Passwords do not match.')
        isValid=False
    else:
        session['confirm_password']=str(client['confirm_password'])
    return {"isValid":isValid, "errors":errors}
