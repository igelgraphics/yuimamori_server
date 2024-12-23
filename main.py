from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, App Engine!"

@app.route('/map.html')
def map_page():
    return app.send_static_file('map.html')

@app.errorhandler(404)
def page_not_found(e):
    return "The requested URL was not found on the server.", 404

if __name__ == '__main__':
    # 環境変数 PORT を使用
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
