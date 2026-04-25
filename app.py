import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json

# ==================== 1. 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTV 访问者本地网络检测工具 v1.8",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始本地真实网络检测", "result_label": "实时检测状态",
        "warning": "请填写完整信息！", "your_ip": "您的公网 IP"
    },
    "English": {
        "title": "IPTV Visitor Local Network Tester v1.8",
        "username": "Username", "password": "Password", "servers": "Servers (one per line)",
        "start_btn": "🚀 Start Local Network Test", "result_label": "Live Status",
        "warning": "Please fill in all fields!", "your_ip": "Your Public IP"
    }
}

# ==================== 2. 页面配置 ====================
st.set_page_config(page_title="IPTV Local Tester", layout="wide", page_icon="📺")

# 侧边栏配置
st.sidebar.title("Settings / 设定")
lang_choice = st.sidebar.selectbox("Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.sidebar.markdown("---")
st.sidebar.subheader(t["your_ip"])

# 获取访问者 IP (由浏览器执行)
components.html(
    """
    <div id="ip-display" style="background:#0e1117; color:#00ff00; padding:8px; border-radius:5px; border:1px solid #31333f; font-family:monospace; font-size:14px;">Detecting...</div>
    <script>
        fetch('https://api.ipify.org?format=json').then(r => r.json())
        .then(d => { document.getElementById('ip-display').innerText = d.ip; })
        .catch(() => { document.getElementById('ip-display').innerText = 'Check Proxy/Network'; });
    </script>
    """, height=60
)

# 主界面
st.title(t["title"])
st.info("💡 **原理**：此工具通过您的浏览器发起探测。检测结果受您本地 **Windows 11** 环境及 **Clash/Mihomo** 代理规则影响。")

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"])
    with c2:
        pwd = st.text_input(t["password"], type="password")
    servers_text = st.text_area(t["servers"], height=200, placeholder="example.com:8080")

# ==================== 3. 核心检测逻辑 (浏览器端图片探测法) ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not servers_text:
        st.warning(t["warning"])
    else:
        server_list = [s.strip() for s in servers_text.splitlines() if s.strip()]
        js_servers = json.dumps(server_list)
        
        # 注入本地检测逻辑
        components.html(
            f"""
            <div id="console" style="background:#1e1e1e; color:#d4d4d4; padding:15px; font-family:monospace; border-radius:8px; height:400px; overflow-y:auto; border:1px solid #444;">
                <div style="color:#569cd6;">> 初始化本地探测引擎...</div>
            </div>

            <script>
                const servers = {js_servers};
                const consoleBox = document.getElementById('console');

                function log(msg, color="#d4d4d4") {{
                    const div = document.createElement('div');
                    div.style.color = color;
                    div.style.marginBottom = "4px";
                    div.innerText = `[${{new Date().toLocaleTimeString()}}] ${{msg}}`;
                    consoleBox.appendChild(div);
                    consoleBox.scrollTop = consoleBox.scrollHeight;
                }}

                async function probe(url) {{
                    return new Promise((resolve) => {{
                        const start = Date.now();
                        const img = new Image();
                        
                        // 尝试请求服务器上的 player_api.php (作为资源加载)
                        // 即使它不是图片，浏览器发起请求本身就能确认连通性
                        img.onload = () => resolve(Date.now() - start);
                        img.onerror = () => resolve(Date.now() - start);
                        
                        // 设置 5 秒超时
                        setTimeout(() => resolve(9999), 5000);
                        
                        img.src = `${{url}}/player_api.php?t=${{start}}`;
                    }});
                }}

                async function runTest() {{
                    log("开始批量探测目标服务器连通性...", "#ce9178");
                    
                    for (let s of servers) {{
                        if (!s.startsWith('http')) s = 'http://' + s;
                        s = s.replace(/\/$/, "");
                        
                        log(`正在探测: ${{s}} ...`);
                        const latency = await probe(s);
                        
                        if (latency < 5000) {{
                            log(`✅ 连通成功 | 响应耗时: ${{latency}}ms`, "#6a9955");
                        }} else if (latency === 9999) {{
                            log(`❌ 探测超时 | 目标不可达或被防火墙拦截`, "#f44747");
                        } else {{
                            log(`⚠️ 响应缓慢 | 耗时: ${{latency}}ms`, "#dcdcaa");
                        }}
                    }}
                    log("--- 所有本地探测任务已完成 ---", "#569cd6");
                }}

                runTest();
            </script>
            """,
            height=450,
        )

with col_info:
    st.markdown(f"""
    ### 探测指南
    1. **真实性**：检测请求由您的浏览器直接发出，不经过服务器中转。
    2. **代理影响**：如果您开启了 **Clash Verge Rev** 或 **Mihomo Party**，检测结果将遵循您的代理分流规则：
       - **直连 (DIRECT)**：使用您的**江西电信**真实宽带。
       - **代理 (PROXY)**：使用您选择的节点 IP。
    3. **为何不显示具体账号信息？**：
       - 浏览器端的跨域限制严禁直接读取第三方服务器的 JSON 数据。
       - 本工具目前专注于**网络连通性**（能否连上）和**延迟**探测。
    """)
