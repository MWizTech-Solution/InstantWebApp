from flask import Flask, request, render_template_string
import logging
import json
import random
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('app.log'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def load_json(file, default):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"{file} missing—using default")
        return default

@app.route('/', methods=['GET', 'POST'])
def generate_web():
    if request.method == 'POST':
        name = request.form.get('name', 'Default')
        messages = load_json('welcome_messages.json', {"messages": [{"text": "Welcome to {{name}} - Your IT Partner", "weight": 1}]})["messages"]
        content = random.choices([m["text"] for m in messages], weights=[m["weight"] for m in messages])[0].replace("{{name}}", name)
        try:
            with open('templates/base.html') as f:
                template = f.read()
        except FileNotFoundError:
            logger.error("Template missing—using default")
            template = "<html><body><h1>{{name}}</h1><p>{{content}}</p>{{feedback_form}}</body></html>"
        feedback_form = """
        <form method="POST" action="/feedback">
            <label>Feedback: </label><input type="text" name="feedback"><br>
            <input type="submit" value="Submit Feedback">
        </form>
        """
        logger.info(f"Generated site for {name}")
        return render_template_string(template, name=name, content=content, feedback_form=feedback_form)
    return """
    <form method="POST">
        <label>Company Name: </label><input type="text" name="name"><br>
        <input type="submit" value="Generate Site">
    </form>
    """

@app.route('/feedback', methods=['POST'])
def feedback():
    feedback = request.form.get('feedback', '')
    with open('feedback.txt', 'a') as f:
        f.write(f"{feedback} - {time.ctime()}\n")
    logger.info("Feedback saved")
    return "Feedback received"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)