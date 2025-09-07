from flask import Flask, render_template

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    """Renders the main index.html file."""
    return render_template('index.html')

if __name__ == '__main__':
    # This server is for local development only.
    # In a production environment, use a more robust server like Gunicorn or uWSGI.
    app.run(host='0.0.0.0', port=5000)
