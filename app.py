import streamlit as st
import requests
import time

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v2.1 - 服务端简易版",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "footer": "v2.1 服务端检测 • 只检查是否可用 + 状态 + 过期时间 • 绕过CORS限制",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 服务端正在检测 {0} 个服务器...",
        "detecting": "[{0}/{1}] 检测中: {2}",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v2.1 - Server Side Simple",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "footer": "v2.1 Server-side Check • Only availability + status + expiration • Bypass CORS",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Server is testing {0} servers...",
        "detecting": "[{0}/{1}] Testing: {2}",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2}"
    }
}

st.set_page_config(page_title="IPTVNator 批量检测工具 v2.1", layout="wide", page_icon="🚀")

lang = st.selectbox(LANGUAGES["简体中文"]["lang_label"], options=list(LANGUAGES.keys()), index=0)
trans = LANGUAGES[lang]

st.title("🚀 " + trans["title"])

col1, col2 = st.columns([2, 1])
with col1:
    username = st.text_input(trans["username"], placeholder="username")
    password = st.text_input(trans["password"], type="password", placeholder="password")
with col2:
    if st.button(trans["example"], use_container_width=True):
        st.session_state["servers"] = "http://line.uhdnovus.com\nhttp://onee.pro\nhttp://line.proswifts.com"

servers_input = st.text_area(
    trans["servers"],
    height=180,
    value=st.session_state.get("servers", ""),
    placeholder="一行一个服务器地址\nhttp://example.com:8080"
)

st.info("💡 本版本使用服务器端请求检测，绕过浏览器 CORS 限制，结果更准确、速度更快。")

if st.button(trans["start_btn"], type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    username_str = username.strip()
    password_str = password.strip()

    if not servers or not username_str or not password_str:
        st.error(trans["warning"])
        st.stop()

    # 显示区域
    result_placeholder = st.empty()
    progress_bar = st.progress(0)

    result_text = trans["running"].format(len(servers)) + "\n\n"
    result_placeholder.markdown(result_text)

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for i, server in enumerate(servers, 1):
        if not server.startswith(("http://", "https://")):
            server = "http://" + server
        server = server.rstrip("/")

        base_url = f"{server}/player_api.php?username={username_str}&password={password_str}"

        result_text += trans["detecting"].format(i, len(servers), server) + "\n"
        result_placeholder.markdown(result_text)

        start_time = time.time()
        try:
            resp = requests.get(base_url, headers=HEADERS, timeout=15, allow_redirects=True)
            elapsed = round(time.time() - start_time, 2)

            if resp.status_code != 200:
                result = trans["http_error"].format(resp.status_code, elapsed)
            else:
                try:
                    data = resp.json()
                    if isinstance(data, dict) and "user_info" in data:
                        ui = data["user_info"]
                        status = ui.get("status", "Unknown")
                        exp = ui.get("exp_date", "永久")
                        if str(exp).isdigit():
                            exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
                        result = trans["available"].format(elapsed, status, exp)
                    else:
                        result = trans["no_userinfo"].format(elapsed)
                except:
                    result = trans["no_userinfo"].format(elapsed)

        except requests.exceptions.Timeout:
            result = trans["timeout"]
        except requests.exceptions.ConnectionError:
            result = trans["conn_fail"]
        except Exception as e:
            result = trans["unknown"].format(str(e)[:80])

        result_text += f"{server} → {result}\n\n"
        result_placeholder.markdown(result_text)

        # 更新进度条
        progress_bar.progress(i / len(servers))
        time.sleep(0.35)  # 防止请求过快

    result_text += "\n" + trans["complete"].format(len(servers))
    result_placeholder.markdown(result_text)
    st.success("✅ 检测完成！")

st.caption(trans["footer"])
st.info("💡 此版本在服务器端发起请求，不受浏览器 CORS 影响，结果与本地 EXE 非常接近。")
