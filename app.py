import streamlit as st
import requests
import time
import json
from collections import defaultdict

# ==================== 多国语言（简洁版） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.0 - 服务端版",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测（服务端请求）",
        "lang_label": "界面语言 / Language:",
        "footer": "v2.0 服务端检测 • 绕过浏览器CORS • 结果更准确（接近本地EXE）",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 服务端正在检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | 直播: {3}个 | 电影: {4}个{5}",
        "no_resource": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | （资源已检测）",
    },
    "English": { ... }  # 可自行补充或简化
}

trans = LANGUAGES["简体中文"]   # 默认简体中文，你可以加语言切换

st.set_page_config(page_title="IPTVNator 服务端检测", layout="wide")
st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://line.uhdnovus.com\nhttp://onee.pro"

servers_input = st.text_area(trans["servers"], height=200, 
                             value=st.session_state.get("servers", ""),
                             placeholder="一行一个服务器地址")

st.info("💡 本版本使用**服务器端 requests** 发起请求，可绕过浏览器 CORS 限制，结果更接近本地 EXE。")

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    if not servers or not username.strip() or not password.strip():
        st.error(trans["warning"])
        st.stop()

    result_placeholder = st.empty()
    progress_bar = st.progress(0)
    result_text = trans["running"].format(len(servers)) + "\n\n"
    result_placeholder.markdown(result_text)

    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    resource_checked = False

    for i, server in enumerate(servers, 1):
        if not server.startswith(("http://", "https://")):
            server = "http://" + server
        server = server.rstrip("/")

        base_url = f"{server}/player_api.php?username={username.strip()}&password={password.strip()}"
        
        result_text += trans["detecting"].format(i, len(servers), server) + "\n"
        result_placeholder.markdown(result_text)

        start_time = time.time()
        success = False

        try:
            resp = requests.get(base_url, headers=HEADERS, timeout=15)
            elapsed = round(time.time() - start_time, 2)

            if resp.status_code != 200:
                result = trans["http_error"].format(resp.status_code, elapsed)
            else:
                data = resp.json()
                if not isinstance(data, dict) or "user_info" not in data:
                    result = trans["no_userinfo"].format(elapsed)
                else:
                    ui = data["user_info"]
                    status = ui.get("status", "Unknown")
                    exp = ui.get("exp_date", "永久")
                    if str(exp).isdigit():
                        exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))

                    # 只对第一个成功服务器检测资源
                    live_c = vod_c = 0
                    lang_info = ""
                    if not resource_checked:
                        try:
                            r = requests.get(f"{base_url}&action=get_live_streams", headers=HEADERS, timeout=12)
                            if r.status_code == 200 and isinstance(r.json(), list):
                                live_c = len(r.json())
                            r = requests.get(f"{base_url}&action=get_vod_streams", headers=HEADERS, timeout=12)
                            if r.status_code == 200 and isinstance(r.json(), list):
                                vod_c = len(r.json())
                        except:
                            pass
                        resource_checked = True

                    result = trans["available"].format(elapsed, status, exp, live_c, vod_c, lang_info)
                    success = True

        except requests.exceptions.Timeout:
            result = trans["timeout"]
        except requests.exceptions.ConnectionError:
            result = trans["conn_fail"]
        except Exception as e:
            result = trans["unknown"].format(str(e)[:100])

        result_text += f"{server} → {result}\n\n"
        result_placeholder.markdown(result_text)
        progress_bar.progress(i / len(servers))
        time.sleep(0.4)   # 防止请求过快

    result_text += "\n" + trans["complete"].format(len(servers))
    result_placeholder.markdown(result_text)
    st.success("检测完成！")

st.caption(trans["footer"])
