# Import Flask
from flask import Flask, render_template, request, url_for, redirect, flash
import json, os

from flask_wtf import FlaskForm
from wtforms import StringField, validators, TextAreaField
from wtforms.validators import DataRequired, Length, InputRequired

# Python files
import datafunctions

# Next up, we need to make a Flask app.
# This will allow us to create routes, etc.
app = Flask(__name__) # I put __name__ here, but you can also place any string you want.

# Prevents cache from using the old css file, makes it use the updated one
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
# ^ ^ ^

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class post_form(FlaskForm):
    post_alias = StringField('',[validators.Length(min=2, max=15, message="Must be between 2-15 characters!")])
    post_content = TextAreaField('',[validators.Length(min=10, max=150, message="Must be between 10-150 characters!")],render_kw={"rows": 4, "cols": 50})

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)

    form = post_form()

    if form.validate_on_submit():
        code_name = form.post_alias.data.strip(" ")
        post_content = form.post_content.data.strip(" ")
        post_date = datafunctions.get_pst_time()
        post_colour = request.form['post_colours']

        with open('posts.json', 'r') as file:
            all_posts = json.load(file)
            posts = all_posts["all_posts"]
            post_id = all_posts["post_increments"]

        file.close()

        all_posts["post_increments"] += 1

        this_post = {
            "code_name": code_name,
            "content": post_content,
            "date_posted": post_date,
            "post_id": post_id,
            "colour": post_colour,
            "comments": []
        }

        posts.append(this_post)

        with open('posts.json', 'w') as file:
            json.dump(all_posts, file, indent=4)
        file.close()

        flash(f"You just changed your name to: { code_name }, you posted { post_content }")
        return redirect(url_for('index'))

    return render_template("index.html", post_data=all_posts, form=form)


@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    code_name = request.form['code_name']
    post_content = request.form['post_content']
    post_id = request.form['post_id']
    post_date = datafunctions.get_pst_time()
    
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]

    file.close()
    
    comment = {
        "code_name": code_name,
        "content": post_content,
        "date_posted": post_date,
    }

    for post in posts:
        if str(post_id) == str(post["post_id"]):
            post["comments"].append(comment)

    with open('posts.json', 'w') as file:
        json.dump(all_posts, file, indent=4)

    file.close()


    return redirect(url_for('index'))

# Application routes
@app.route("/") # / means index, it's the homepage.
def index(): # You can name your function whatever you want.
    with open('posts.json', 'r') as file:
        all_posts = json.load(file)
        posts = all_posts["all_posts"]
    file.close()

    return render_template("index.html", post_data=all_posts, form=post_form())



app.run(
  host = "0.0.0.0", # or 127.0.0.1 (DONT USE LOCALHOST)
  port = 8080,
  debug = True
)