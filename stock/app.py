from flask import Flask, redirect, render_template, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
app.config['GITHUB_ID'] = 'YOUR_GITHUB_CLIENT_ID'  # Replace with your GitHub Client ID
app.config['GITHUB_SECRET'] = 'YOUR_GITHUB_CLIENT_SECRET'  # Replace with your GitHub Client Secret

oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key=app.config['GITHUB_ID'],
    consumer_secret=app.config['GITHUB_SECRET'],
    request_token_params={
        'scope': 'user:email',
    },
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/callback')
def authorized():
    response = github.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['github_token'] = (response['access_token'], '')
    user_info = github.get('user')
    session['user_info'] = user_info.data
    return redirect(url_for('user_landing'))

@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')

@app.route('/user')
def user_landing():
    if 'github_token' not in session:
        return redirect(url_for('login'))
    
    user_info = session.get('user_info')
    return render_template('user_landing.html', user=user_info)

@app.route('/api/<option>')
def api(option):
    # Existing API routes for stock data
    # ...
    pass

if __name__ == '__main__':
    app.run(debug=True)
