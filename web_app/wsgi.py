"""生产环境使用的 WSGI 入口。

本地学习时仍可运行 ``python -m web_app``。部署平台则让 Gunicorn
导入这里的 ``app``，由生产级服务器负责监听端口和管理请求。
"""

from .app import create_app


app = create_app()
