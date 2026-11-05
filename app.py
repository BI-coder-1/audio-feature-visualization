"""魔搭创空间的 Streamlit 固定入口。

魔搭会从项目根目录启动 ``app.py``。真正的页面代码放在
``streamlit_app.py``，这样本地运行和公网部署共用同一份界面实现。
"""

from streamlit_app import main


# Streamlit 会把这个文件当作页面脚本执行，因此入口处直接组装页面。
# 不使用 ``if __name__ == "__main__"``，以兼容 Streamlit 的测试运行器。
main()
