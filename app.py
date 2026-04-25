import streamlit as st
import requests
import time

st.set_page_config(page_title="IPTVNator 服务端检测", layout="wide", page_icon="🚀")
st.title("🚀 IPTVNator 批量检测工具 v2.4 - 服务端版（推荐）")

username = st.text_input("用户名:", placeholder="username")
password = st.text_input("密码:", type="password", placeholder="password")

servers_input = st.text_area("服务器地址（一行一个）:", height=220, 
                             placeholder="http://line.uhdnovus.com\nhttp://onee.pro\nhttp://line.proswifts.com")

if st.button("🚀 开始服务端检测", type="primary", use_container_width=True):
    servers = [s.strip() for s in servers_input.strip().splitlines() if s.strip()]
    if not servers or not username.strip() or not password.strip():
        st.error("请填写服务器列表、账号和密码！")
        st.stop()

    placeholder = st.empty()
    progress_bar = st.progress(0)
    result_text = f"🚀 服务端正在检测 {len(servers)} 个服务器...\n\n"
    placeholder.markdown(result_text)

    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for i, server in enumerate(servers, 1):
        if not server.startswith(("http://", "https://")):
            server = "http://" + server
        server = server.rstrip("/")

        base_url = f"{server}/player_api.php?username={username.strip()}&password={password.strip()}"

        result_text += f"[{i}/{len(servers)}] 检测中: {server}\n"
        placeholder.markdown(result_text)

        start_time = time.time()
        try:
            resp = requests.get(base_url, headers=HEADERS, timeout=15)
            elapsed = round(time.time() - start_time, 2)

            if resp.status_code != 200:
                result = f"❌ HTTP错误 {resp.status_code} | 耗时 {elapsed}s"
            else:
                data = resp.json()
                if isinstance(data, dict) and "user_info" in data:
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

        result_text += f"{server} → {result}\n\n"
        placeholder.markdown(result_text)
        progress_bar.progress(i / len(servers))
        time.sleep(0.35)

    result_text += f"\n✅ 检测完成！共检测 {len(servers)} 个服务器。"
    placeholder.markdown(result_text)
    st.success("检测完成！")

st.caption("v2.4 服务端检测 • 绕过浏览器 CORS • 结果更接近本地 EXE")
st.info("💡 此版本在服务器端发起请求，不受浏览器 CORS 影响，结果准确率高。")
