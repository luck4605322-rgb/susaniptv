import streamlit as st
import streamlit.components.v1 as components
import json

# ==================== 1. 页面配置与多语言字典 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

# 整合了您提供的所有语言版本并添加联系方式
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v2.2",
        "contact": "作者：susan | WhatsApp: +8615573857383",
        "username": "用户名", "password": "密码", 
        "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始本地网络批量检测",
        "ip_label": "您的当前探测 IP",
        "notice": "探测请求由您的浏览器发出，结果受本地网络和代理规则影响。"
    },
    "English": {
        "title": "IPTVNator Web Tester v2.2",
        "contact": "Author: susan | WhatsApp: +8615573857383",
        "username": "Username", "password": "Password", 
        "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Local Batch Test",
        "ip_label": "Your Current IP",
        "notice": "Requests are sent via your browser, reflecting your local network/proxy rules."
    },
    "Español": {
        "title": "Probador de IPTV v2.2",
        "contact": "Autor: susan | WhatsApp: +8615573857383",
        "username": "Usuario", "password": "Password", 
        "servers": "Servidores (uno por línea)",
        "start_btn": "🚀 Iniciar prueba local",
        "ip_label": "Tu IP actual",
        "notice": "Las solicitudes se envían a través de su navegador."
    }
}

# 侧边栏设置
st.sidebar.title("Settings / 设定")
lang_choice = st.sidebar.selectbox("Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.sidebar.markdown("---")
st.sidebar.write(f"**{t['contact']}**") # 添加联系方式到侧边栏

# ==================== 2. 主界面布局 ====================
st.title(t["title"])
st.caption(t["contact"]) # 标题下方也显示联系方式
st.markdown("---")

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"])
    with c2:
        pwd = st.text_input(t["password"], type="password")
    servers_text = st.text_area(t["servers"], height=200, placeholder="example.com:8080")

with col_info:
    st.info(f"**{t['notice']}**")
    st.warning("⚠️ 如果检测显示失败，请检查您的代理软件是否拦截了跨域请求，或尝试切换为直连模式探测。")

# ==================== 3. 核心探测逻辑 (JS 执行) ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not servers_text:
        st.error("请输入服务器地址！")
    else:
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        js_servers = json.dumps(server_list)
        
        # 注入修复后的 HTML/JS 探测组件
        components.html(
            f"""
            <div id="status-container" style="background:#1e1e1e; color:#d4d4d4; padding:20px; font-family:monospace; border-radius:10px; border:1px solid #333;">
                <div id="ip-header" style="color:#00ff00; margin-bottom:15px; border-bottom:1px solid #444; padding-bottom:10px;">获取探测 IP 中...</div>
                <div id="log-box" style="height:350px; overflow-y:auto; line-height:1.6; font-size:13px;">
                    > 引擎已就绪，准备探测...
                </div>
            </div>

            <script>
                const servers = {js_servers};
                const logBox = document.getElementById('log-box');
                const ipHeader = document.getElementById('ip-header');

                function writeLog(msg, color="#d4d4d4") {{
                    const div = document.createElement('div');
                    div.style.color = color;
                    div.style.marginBottom = "5px";
                    div.innerText = `[${{new Date().toLocaleTimeString()}}] ${{msg}}`;
                    logBox.appendChild(div);
                    logBox.scrollTop = logBox.scrollHeight;
                }}

                // 获取本地出口 IP
                fetch('https://api.ipify.org?format=json')
                    .then(r => r.json())
                    .then(d => {{ ipHeader.innerText = "{t['ip_label']}: " + d.ip; }})
                    .catch(() => {{ ipHeader.innerText = "{t['ip_label']}: 获取失败 (请检查网络)"; }});

                async function probe(url) {{
                    const target = (url.startsWith('http') ? url : 'http://' + url).replace(/\/$/, "");
                    const start = Date.now();
                    try {{
                        // 使用 no-cors 模式确保通过本地网络发起请求
                        await fetch(`${{target}}/player_api.php`, {{ mode: 'no-cors', cache: 'no-cache' }});
                        return {{ success: true, time: Date.now() - start }};
                    }} catch (e) {{
                        return {{ success: false, time: 0 }};
                    }}
                }}

                async function startTask() {{
                    writeLog("开始批量检测...", "#ce9178");
                    for (const s of servers) {{
                        writeLog(`正在探测: ${{s}}`);
                        const res = await probe(s);
                        if (res.success) {{
                            writeLog(`✅ 连通成功 | 响应延迟: ${{res.time}}ms`, "#6a9955");
                        }} else {{
                            writeLog(`❌ 无法访问 | 请检查地址或本地网络`, "#f44747");
                        }}
                    }}
                    writeLog("--- 检测任务完成 ---", "#569cd6");
                }}

                setTimeout(startTask, 500);
            </script>
            """,
            height=450,
        )
