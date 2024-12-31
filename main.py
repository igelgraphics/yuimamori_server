import os
from flask import Flask, redirect, url_for, session, render_template, jsonify
from flask_oauthlib.client import OAuth
from functools import wraps
from google.cloud import bigquery

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# BigQuery クライアント
client = bigquery.Client()

# OAuth 設定
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv("GOOGLE_CLIENT_ID"),
    consumer_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# ログイン状態を確認するデコレーター
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'google_token' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'google_token' in session:
        return redirect(url_for('map'))
    return render_template('login.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

@app.route('/oauth2callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args.get('error_reason'),
            request.args.get('error_description')
        )
    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('map'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/map')
@login_required
def map():
    return render_template('map.html')

@app.route('/api/locations')
@login_required
def get_locations():
    # BigQueryクエリ
    query = """
        SELECT latitude, longitude, timestamp
        FROM `yuimamori-server.location_dataset.trackking_data`
        ORDER BY timestamp DESC
        LIMIT 100
    """
    query_job = client.query(query)
    results = query_job.result()

    # データをJSON形式に変換
    locations = []
    for row in results:
        locations.append({
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(locations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
