import streamlit as st
import requests
import time

st.set_page_config(page_title="IPTVNator 服务端检测", layout="wide")
st.title("🚀 IPTVNator 批量检测工具 v2.3 - 服务端版（推荐）")

username = st.text_input("用户名:", placeholder="username")
password = st.text_input("密码:", type="password", placeholder="password")

servers_input = st.text_area("服务器地址（一行一个）:", height=200, 
                             placeholder="http://line.uhdnovus.com\nhttp://onee.pro")

if st.button("🚀 开始服务端检测", type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    if not servers or not username.strip() or not password.strip():
        st.error("请填写服务器列表、账号和密码！")
        st.stop()

    placeholder = st.empty()
    progress_bar = st.progress(0)
    text = "🚀 服务端正在检测...\n\n"
    placeholder.markdown(text)

    for i, server in enumerate(servers, 1):
        if not server.startswith("http"):
            server = "http://" + server
        server = server.rstrip("/")

        base_url = f"{server}/player_api.php?username={username.strip()}&password={password.strip()}"

        text += f"[{i}/{len(servers)}] 检测中: {server}\n"
        placeholder.markdown(text)

        try:
            start = time.time()
            resp = requests.get(base_url, timeout=15)
            elapsed = round(time.time() - start, 2)

            if resp.status_code != 200:
                result = f"❌ HTTP错误 {resp.status_code} | 耗时 {elapsed}s"
            else:
                data = resp.json()
                if "user_info" in data:
                    ui = data["user_info"]
                    status = ui.get("status", "Unknown")
                    exp = ui.get("exp_date", "永久")
                    if str(exp).isdigit():
                        exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
                    result = f"✅ 可用 | 耗时 {elapsed}s | 状态: {status} | 过期: {exp}"
                else:
                    result = f"❌ 登录失败（无 user_info） | 耗时 {elapsed}s"
        except requests.exceptions.Timeout:
            result = "❌ 超时 (>15s)"
        except requests.exceptions.ConnectionError:
            result = "❌ 连接失败"
        except Exception as e:
            result = f"❌ 未知错误: {str(e)[:80]}"

        text += f"{server} → {result}\n\n"
        placeholder.markdown(text)
        progress_bar.progress(i / len(servers))
        time.sleep(0.4)

    text += f"\n✅ 检测完成！共检测 {len(servers)} 个服务器。"
    placeholder.markdown(text)
    st.success("检测完成！")

st.caption("v2.3 服务端检测 • 绕过浏览器 CORS 限制 • 结果更准确")
