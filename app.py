import streamlit as st
import json

# ==================== 多语言字典 v3.0 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v3.0（客户端检测优化）--作者 susan",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始批量检测（浏览器本地网络）",
        "result_label": "检测结果", "warning": "请填写完整信息！",
        "header_server": "服务器", "header_status": "状态", "header_info": "详细信息",
        "your_ip": "您的公网 IP（浏览器检测）",
        "done": "检测完成！",
        "note": "⚠️ 注意：由于大多数 IPTV 服务器未开启 CORS，部分结果可能仅能判断网络可达性。真实性受浏览器限制。建议结合本地测试验证关键服务器。"
    },
    "English": {
        "title": "IPTVNator Batch Tester v3.0 (Client-side Optimized) -- Author susan",
        "username": "Username", "password": "Password", "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test (Browser Local Network)",
        "result_label": "Test Results", "warning": "Please fill in all fields!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Your Public IP (Browser)",
        "done": "Test Completed!",
        "note": "⚠️ Note: Due to CORS restrictions on most IPTV servers, some results can only indicate network reachability. For critical servers, verify with local Python requests."
    }
}

st.set_page_config(page_title="IPTV Tester v3.0", layout="wide", page_icon="📺")

lang_choice = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.title(t["title"])
st.markdown("---")

st.sidebar.subheader(t["your_ip"])
ip_placeholder = st.sidebar.empty()

col1, col2 = st.columns([2, 1])

with col1:
    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input(t["username"])
    with c2:
        password = st.text_input(t["password"], type="password")
    servers_text = st.text_area(t["servers"], height=250, placeholder="http://yourserver.com:8080\nhttps://another.com:25461")

with col2:
    st.info("""
    **v3.0 主要优化：**
    - 改进状态判断逻辑（尝试读取响应文本）
    - 区分网络错误、HTTP 错误、登录失败
    - 更清晰的颜色标记和超时处理
    - 客户端 IP 多源获取
    """)

if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not username or not password or not servers_text.strip():
        st.error(t["warning"])
        st.stop()

    servers = [line.strip() for line in servers_text.splitlines() if line.strip()]
    
    progress = st.progress(0)
    status_text = st.empty()
    result_area = st.empty()

    html_code = f"""
    <style>
        .table {{ width:100%; border-collapse:collapse; margin:15px 0; }}
        th, td {{ padding:10px; border:1px solid #ddd; text-align:left; }}
        th {{ background:#f0f2f6; }}
        .active {{ color:#0b8a3d; font-weight:bold; }}
        .failed {{ color:#d32f2f; font-weight:bold; }}
        .warning {{ color:#f57c00; }}
        .info {{ color:#1976d2; }}
    </style>
    <div id="result_table"></div>

    <script>
    const username = "{username}";
    const password = "{password}";
    const servers = {json.dumps(servers)};

    let results = [];
    let completed = 0;

    async function testServer(server) {{
        let url = server.trim();
        if (!url.startsWith('http')) url = 'http://' + url;
        url = url.replace(/\/$/, '');
        const apiUrl = `${{url}}/player_api.php?username=${{username}}&password=${{password}}`;
        const start = Date.now();

        try {{
            const controller = new AbortController();
            setTimeout(() => controller.abort(), 15000);

            const resp = await fetch(apiUrl, {{
                method: 'GET',
                headers: {{ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }},
                signal: controller.signal
            }});

            const timeTaken = ((Date.now() - start)/1000).toFixed(2);

            let status = "❌ Unknown";
            let details = `Time: ${{timeTaken}}s`;

            if (resp.ok) {{
                try {{
                    const text = await resp.text();
                    if (text.includes('"user_info"') || text.includes('status') || text.includes('Active')) {{
                        status = "✅ Active";
                        // 粗略尝试提取 exp_date
                        const match = text.match(/"exp_date"\\s*:\\s*["']?(\\d+)/);
                        if (match) {{
                            const exp = new Date(parseInt(match[1]) * 1000);
                            details += ` | Exp: ${{exp.getFullYear()}-${{String(exp.getMonth()+1).padStart(2,'0')}}-${{String(exp.getDate()).padStart(2,'0')}}`;
                        }}
                    }} else {{
                        status = "⚠️ Reachable - Login Failed";
                    }}
                }} catch(e) {{
                    status = "✅ Reachable (content unreadable)";
                }}
            }} else {{
                status = `❌ HTTP ${{resp.status}}`;
            }}

            results.push({{Server: url, Status: status, Details: details}});
        }} catch (e) {{
            const timeTaken = ((Date.now() - start)/1000).toFixed(2);
            let status = "❌ Unreachable";
            if (e.name === "AbortError") status = "❌ Timeout (>15s)";
            else if (e.message.includes("CORS") || e.message.includes("Failed to fetch")) {{
                status = "❌ CORS Blocked / Network Error";
            }}
            results.push({{Server: url, Status: status, Details: `Error: ${{e.message || 'Connection failed'}} | ${{timeTaken}}s`}});
        }}

        completed++;
        progress = Math.round((completed / servers.length) * 100);
        renderTable();
    }}

    function renderTable() {{
        let html = `<table class="table"><thead><tr><th>${t["header_server"]}</th><th>${t["header_status"]}</th><th>${t["header_info"]}</th></tr></thead><tbody>`;
        results.forEach(r => {{
            let cls = r.Status.includes("✅") ? "active" : (r.Status.includes("⚠️") ? "warning" : "failed");
            html += `<tr><td>${{r.Server}}</td><td class="${{cls}}">${{r.Status}}</td><td>${{r.Details}}</td></tr>`;
        }});
        html += `</tbody></table>`;
        document.getElementById("result_table").innerHTML = html;
    }}

    // 并行执行（浏览器会自动限流）
    Promise.allSettled(servers.map(testServer)).then(() => {{
        console.log("检测完成");
    }});

    renderTable(); // 初始表格
    </script>
    """

    with result_area:
        st.subheader(t["result_label"])
        st.components.v1.html(html_code, height=700, scrolling=True)

    st.success(t["done"])
    st.caption(t["note"])

# 客户端 IP 显示（多源）
ip_js = """
<script>
async function fetchIP() {
    const urls = ['https://api.ipify.org?format=json', 'https://api64.ipify.org?format=json', 'https://ifconfig.me/ip'];
    for (let u of urls) {
        try {
            let r = await fetch(u);
            if (r.ok) {
                let data = await r.text();
                let ip = data.trim().replace(/\\n/g, '');
                document.getElementById('clientip').innerHTML = `<code style="font-size:1.1em;">${ip}</code>`;
                return;
            }
        } catch(e){}
    }
    document.getElementById('clientip').innerHTML = '无法获取';
}
fetchIP();
</script>
<div id="clientip" style="background:#f0f2f6; padding:10px; border-radius:6px; font-family:monospace;"></div>
"""
ip_placeholder.markdown("**Detected:**")
st.components.v1.html(ip_js, height=70)

st.caption("**重要提醒**：浏览器安全策略（CORS）是当前主要限制因素。如果重要服务器结果显示 'CORS Blocked' 或 'Reachable but unreadable'，**强烈建议使用本地 Python 脚本**（requests 库）进行最终验证。")
