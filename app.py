from flask import Flask, request, render_template_string
import logging
import json
import random
import time
from flask import send_file

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()],
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
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
        app_download = render_template_string("""
            <form method="POST" action="/generate_app">
            <input type="hidden" name="name" value="{{name}}"><br>
            <input type="submit" value="Download App">
            </form>
            """, name=name)
        feedback_form = """
        <form method="POST" action="/feedback">
            <label>Feedback: </label><input type="text" name="feedback"><br>
            <input type="submit" value="Submit Feedback">
        </form>
        """
        logger.info(f"Generated site for {name}")
        return render_template_string(template, name=name, content=content, feedback_form=app_download + feedback_form)
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

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    messages = load_json('chat_responses.json', {"responses": [{"text": "Chatbot: How can I assist?", "weight": 1}]})["responses"]
    if request.method == 'POST':
        msg = request.form.get('msg', '')
        with open('chat_feedback.txt', 'a') as f:
            f.write(f"{msg} - {time.ctime()}\n")
        try:
            response = random.choices([m["text"] for m in messages], weights=[m["weight"] for m in messages])[0]
        except IndexError:
            logger.error("Chat responses empty—using default")
            response = "Chatbot: How can I assist?"
        logger.info(f"Chat response: {response}")
        return response
    return """
    <form method="POST">
        <label>Chat: </label><input type="text" name="msg"><br>
        <input type="submit" value="Send">
    </form>
    """

@app.route('/generate_app', methods=['POST'])
def generate_app():
    name = request.form.get('name', 'Default')  # Get name from form
    apk_path = 'apk/it_sme_app.apk'
    default_apk_path = 'apk/default_app.apk'
    try:
        logger.info(f"Generated app for {name}")
        # Use name directly in f-string—no {{}}
        return send_file(apk_path, as_attachment=True, download_name=f"{name}_app.apk")
    except FileNotFoundError:
        logger.error(f"Main APK missing at {apk_path}—attempting fallback")
        try:
            logger.info(f"Using default APK for {name}")
            return send_file(default_apk_path, as_attachment=True, download_name=f"{name}_default_app.apk")
        except FileNotFoundError:
            logger.error("Default APK also missing—self-healing failed")
            return render_template_string("""
            <html>
            <body>
                <h2>Oops!</h2>
                <p>Sorry, we couldn’t generate your app right now. Please try again later or contact support.</p>
                <a href="/">Back to Home</a>
            </body>
            </html>
            """)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)