import streamlit as st
import requests
import time

LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.2 - 服务端检测（推荐）",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始服务端检测（推荐）",
        "lang_label": "界面语言 / Language:",
        "footer": "v2.2 服务端检测 • 绕过CORS • 结果更准确",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 服务端正在检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    }
}

st.set_page_config(page_title="IPTVNator 服务端检测", layout="wide")
st.title("🚀 " + LANGUAGES["简体中文"]["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(LANGUAGES["简体中文"]["username"], placeholder="username")
    password = st.text_input(LANGUAGES["简体中文"]["password"], type="password", placeholder="password")
with col2:
    if st.button(LANGUAGES["简体中文"]["example"], use_container_width=True):
        st.session_state["servers"] = "http://line.uhdnovus.com\nhttp://onee.pro"

servers_input = st.text_area(LANGUAGES["简体中文"]["servers"], height=200, value=st.session_state.get("servers", ""), placeholder="一行一个服务器地址")

if st.button(LANGUAGES["简体中文"]["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(LANGUAGES["简体中文"]["warning"])
        st.stop()

    result_placeholder = st.empty()
    progress_bar = st.progress(0)
    result_text = LANGUAGES["简体中文"]["running"].format(len(servers)) + "\n\n"
    result_placeholder.markdown(result_text)

    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for i, server in enumerate(servers, 1):
        if not server.startswith(("http://", "https://")):
            server = "http://" + server
        server = server.rstrip("/")

        base_url = f"{server}/player_api.php?username={username_str}&password={password_str}"

        result_text += LANGUAGES["简体中文"]["detecting"].format(i, len(servers), server) + "\n"
        result_placeholder.markdown(result_text)

        start_time = time.time()
        try:
            resp = requests.get(base_url, headers=HEADERS, timeout=15)
            elapsed = round(time.time() - start_time, 2)

            if resp.status_code != 200:
                result = LANGUAGES["简体中文"]["http_error"].format(resp.status_code, elapsed)
            else:
                data = resp.json()
                if isinstance(data, dict) and "user_info" in data:
                    ui = data["user_info"]
                    status = ui.get("status", "Unknown")
                    exp = ui.get("exp_date", "永久")
                    if str(exp).isdigit():
                        exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
                    result = LANGUAGES["简体中文"]["available"].format(elapsed, status, exp)
                else:
                    result = LANGUAGES["简体中文"]["no_userinfo"].format(elapsed)
        except requests.exceptions.Timeout:
            result = LANGUAGES["简体中文"]["timeout"]
        except requests.exceptions.ConnectionError:
            result = LANGUAGES["简体中文"]["conn_fail"]
        except Exception as e:
            result = LANGUAGES["简体中文"]["unknown"].format(str(e)[:80])

        result_text += f"{server} → {result}\n\n"
        result_placeholder.markdown(result_text)
        progress_bar.progress(i / len(servers))
        time.sleep(0.4)

    result_text += "\n" + LANGUAGES["简体中文"]["complete"].format(len(servers))
    result_placeholder.markdown(result_text)
    st.success("✅ 检测完成！")

st.caption(LANGUAGES["简体中文"]["footer"])
