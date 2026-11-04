"""允许使用 ``python -m web_app`` 启动网页。"""

from .app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
