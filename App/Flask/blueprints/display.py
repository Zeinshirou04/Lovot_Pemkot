from flask import Blueprint, render_template, redirect

EyesBP = Blueprint('eyes', __name__)

@EyesBP.route('/display')
def display_eyes():
    return render_template('display.html')