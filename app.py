import streamlit as st
import time
import pandas as pd
from collections import defaultdict

# ==================== 1. 多语言字典（已改为纯英文版） ====================
LANGUAGES = {
    "English": {
        "title": "IPTVNator Web Batch Tester v1.8.1 (Client-Side) --Author susan, WhatsApp: +8615573857383",
        "username": "Username",
        "password": "Password",
        "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test from My Local Network",
        "result_label": "Test Results",
        "warning": "Please fill in all fields!",
        "testing": "Testing directly from your browser...",
        "header_server": "Server",
        "header_status": "Status",
        "header_info": "Details",
        "your_ip": "Your Public IP",
        "client_note": "✅ Detection now runs from your local network (real home broadband / mobile / VPN)"
    }
}

# ==================== 2. Streamlit 配置 ====================
st.set_page_config(page_title="IPTVNator Client Tester", layout="wide", page_icon="📺")

lang_choice = st.sidebar.selectbox("Language", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.title(t["title"])
st.markdown("---")

# 显示当前访问者 IP（服务器端获取，仅供参考）
@st.cache_data(ttl=3600)
def get_public_ip():
    try:
        import requests
        return requests.get("https://ifconfig.me/ip", timeout=5).text.strip()
    except:
        return "Unknown"

current_ip = get_public_ip()

st.sidebar.subheader(t["your_ip"])
st.sidebar.code(current_ip, language="bash")
st.sidebar.caption(t.get("client_note", "Detection from client browser"))

# ==================== 3. 输入区域 ====================
col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input(t["username"])
    with c2:
        password = st.text_input(t["password"], type="password")
   
    servers_text = st.text_area(t["servers"], height=250,
                                placeholder="http://example.com:8080\nhttps://iptv.example.com")

with col_info:
    st.info(f"""
    **Important Tips:**
    - Detection will run **directly from your browser** using your local network (home broadband, 4G/5G, VPN, etc.)
    - Supports HTTP/HTTPS, automatically adds http:// prefix
    - Browser concurrent limit: about 6-10 simultaneous requests
    - Recommended: Do not test more than 50 servers at once
    - WhatsApp: **+8615573857383**
    """)

# ==================== 4. 核心：JavaScript 客户端检测 ====================
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not username or not password or not servers_text.strip():
        st.error(t["warning"])
    else:
        servers = [s.strip() for s in servers_text.splitlines() if s.strip()]
       
        if not servers:
            st.error("No valid server addresses!")
            st.stop()

        # 注入 JavaScript 进行客户端批量检测
        js_code = f"""
        <script>
        async function testIPTV() {{
            const username = "{username.replace('"', '\\"')}";
            const password = "{password.replace('"', '\\"')}";
            const servers = {servers};
           
            const results = [];
            const progressContainer = document.createElement('div');
            progressContainer.innerHTML = `
                <h3>{t.get("testing", "Testing...")}</h3>
                <div id="progress" style="width:100%; background:#333; height:20px; border-radius:10px; overflow:hidden;">
                    <div id="bar" style="width:0%; height:100%; background:linear-gradient(90deg, #00ff00, #00cc00); transition:width 0.3s;"></div>
                </div>
                <p id="status" style="margin-top:10px; font-family:monospace;"></p>
            `;
            document.body.appendChild(progressContainer);
            const bar = document.getElementById('bar');
            const status = document.getElementById('status');

            for (let i = 0; i < servers.length; i++) {{
                let server = servers[i];
                if (!server.startsWith('http')) server = 'http://' + server;
                server = server.replace(/\\/$/, '');
                const baseUrl = `${{server}}/player_api.php?username=${{encodeURIComponent(username)}}&password=${{encodeURIComponent(password)}}`;
                const startTime = Date.now();

                try {{
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 12000);
                    const resp = await fetch(baseUrl, {{
                        method: 'GET',
                        headers: {{ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }},
                        signal: controller.signal
                    }});
                    clearTimeout(timeoutId);
                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

                    let detail = '';
                    let statusText = '❌ Fail';

                    if (resp.ok) {{
                        try {{
                            const data = await resp.json();
                            if (data.user_info) {{
                                const ui = data.user_info;
                                const exp = ui.exp_date;
                                const expDate = exp && !isNaN(exp) ? new Date(exp * 1000).toISOString().split('T')[0] : 'Never';
                                detail = `Status: ${{ui.status || 'Active'}} | Exp: ${{expDate}} | ${{elapsed}}s`;
                                statusText = '✅ Active';
                            }} else {{
                                detail = `Login Failed | ${{elapsed}}s`;
                            }}
                        }} catch(e) {{
                            detail = `Invalid JSON | ${{elapsed}}s`;
                        }}
                    }} else {{
                        detail = `HTTP ${{resp.status}} | ${{elapsed}}s`;
                    }}
                    results.push({{Server: server, Status: statusText, Details: detail}});
                }} catch (err) {{
                    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                    let msg = err.name === 'AbortError' ? 'Timeout' : 'Error/Unreachable';
                    results.push({{Server: server, Status: '❌ Error', Details: `${{msg}} | ${{elapsed}}s`}});
                }}

                const percent = Math.round(((i + 1) / servers.length) * 100);
                bar.style.width = percent + '%';
                status.textContent = `Testing: ${{i+1}}/${{servers.length}} (${{percent}}%)`;
            }}

            let html = `
                <h3>${t["result_label"]}</h3>
                <table style="width:100%; border-collapse:collapse; margin-top:15px;">
                    <thead>
                        <tr style="background:#1e1e1e;">
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_server"]}</th>
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_status"]}</th>
                            <th style="padding:12px; border:1px solid #444; text-align:left;">${t["header_info"]}</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            results.forEach(r => {{
                const color = r.Status.includes('✅') ? '#00ff00' : '#ff4444';
                html += `
                    <tr>
                        <td style="padding:10px; border:1px solid #444;">${r.Server}</td>
                        <td style="padding:10px; border:1px solid #444; color:${color}; font-weight:bold;">${r.Status}</td>
                        <td style="padding:10px; border:1px solid #444; font-family:monospace;">${r.Details}</td>
                    </tr>
                `;
            }});

            html += `</tbody></table><br><p style="color:#00cc00; text-align:center; font-weight:bold;">WhatsApp: +8615573857383</p>`;

            const resultDiv = document.createElement('div');
            resultDiv.innerHTML = html;
            document.body.appendChild(resultDiv);

            window.scrollTo(0, document.body.scrollHeight);
        }}

        testIPTV();
        </script>
        """

        st.components.v1.html(js_code, height=800, scrolling=True)
        st.success("✅ Client-side detection started! All requests are made from your local network. WhatsApp: +8615573857383")
