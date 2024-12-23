import os
from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # セッション管理のためのキー

# OAuth 設定
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=os.getenv("GOOGLE_CLIENT_ID"),  # 環境変数からクライアントIDを取得
    consumer_secret=os.getenv("GOOGLE_CLIENT_SECRET"),  # 環境変数からクライアントシークレットを取得
    request_token_params={
        'scope': 'email',  # 必要なスコープを指定
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
        return redirect(url_for('map'))  # ログイン後はマップページにリダイレクト
    return render_template('login.html')  # ログイン画面を表示

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    # セッションをクリアしてログアウト
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

    # アクセストークンをセッションに保存
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo').data

    # 許可リストのチェック
    allowed_users = os.getenv("ALLOWED_USERS", "").split(",")
    if user_info['email'] not in allowed_users:
        session.pop('google_token', None)
        return "Access denied: Your account is not authorized."

    session['user'] = user_info
    return redirect(url_for('map'))  # ログイン後にマップページへリダイレクト

@google.tokengetter
def get_google_oauth_token():
    # セッションからトークンを取得
    return session.get('google_token')

# ログイン後に表示するマップページ
@app.route('/map')
@login_required
def map():
    return render_template('map.html')  # マップページを表示

if __name__ == '__main__':
    # ホストとポートを指定して実行
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
