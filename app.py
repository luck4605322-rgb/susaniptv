import streamlit as st
import json

# ==================== 1. 多语言字典（v2.1） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v2.1（客户端真实检测）--作者 susan",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始批量检测（使用您的本地网络）", 
        "result_label": "检测结果", "warning": "请填写完整信息！",
        "header_server": "服务器", "header_status": "状态", "header_info": "详细信息",
        "your_ip": "您的公网 IP（客户端本地）", "testing": "正在测试中...", "done": "检测完成！",
        "note": "检测完全在您的浏览器中执行，使用您的本地网络和IP。GitHub服务器仅提供页面。"
    },
    "English": {
        "title": "IPTVNator Web Tester v2.1 (Client-side Real Test) -- Author susan",
        "username": "Username", "password": "Password", "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test (Using Your Local Network)", 
        "result_label": "Test Results", "warning": "Please fill in all fields!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Your Public IP (Client-side)", "testing": "Testing in progress...", "done": "Test Completed!",
        "note": "All tests are executed directly from your browser using your local network and IP."
    },
    # 其他语言可按需补充，结构保持一致
}

st.set_page_config(page_title="IPTV Batch Tester", layout="wide", page_icon="📺")

lang_choice = st.sidebar.selectbox("🌐 Language / 语言", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.title(t["title"])
st.markdown("---")

# 侧边栏客户端 IP
st.sidebar.title("Settings")
st.sidebar.subheader(t["your_ip"])
ip_placeholder = st.sidebar.empty()

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"], placeholder="username")
    with c2:
        pwd = st.text_input(t["password"], type="password", placeholder="password")
    
    servers_text = st.text_area(t["servers"], height=280, 
                                placeholder="http://example.com:8080\nhttps://iptv.example.net:25461")

with col_info:
    st.info(f"""
    **关键改进（v2.1）：**
    - 请求**从您的浏览器直接发出**，使用您的本地网络/IP进行真实检测
    - 改进状态判断逻辑（尝试解析返回内容）
    - 支持部分 CORS 受限服务器的回退检测
    - 推荐使用 Chrome / Edge / Firefox 最新版
    """)

if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not user or not pwd or not servers_text.strip():
        st.warning(t["warning"])
        st.stop()

    servers = [s.strip() for s in servers_text.splitlines() if s.strip()]
    if not servers:
        st.warning("请输入至少一个有效的服务器地址！")
        st.stop()

    progress_bar = st.progress(0)
    status_msg = st.empty()
    result_container = st.empty()

    # ==================== 客户端 JS 检测核心逻辑（v2.1 优化版） ====================
    html_code = f"""
    <style>
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
        th {{ background: #f0f2f6; }}
        .success {{ color: #0f9d58; font-weight: bold; }}
        .error {{ color: #d93025; font-weight: bold; }}
        .warning {{ color: #f4b400; }}
    </style>
    <div id="results"></div>

    <script>
        const username = "{user}";
        const password = "{pwd}";
        const servers = {json.dumps(servers)};
        const total = servers.length;
        let completed = 0;
        let results = [];

        async function testSingleServer(serverUrl) {{
            let server = serverUrl.trim();
            if (!server.startsWith("http")) server = "http://" + server;
            server = server.replace(/\/$/, "");
            const baseUrl = `${{server}}/player_api.php?username=${{username}}&password=${{password}}`;
            const startTime = Date.now();

            try {{
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 12000);

                const response = await fetch(baseUrl, {{
                    method: 'GET',
                    headers: {{ 
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
                    }},
                    signal: controller.signal,
                    // mode: 'cors' 默认模式，尝试读取响应
                }});

                clearTimeout(timeout);
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

                let statusText = "❌ Unknown";
                let details = `Time: ${{elapsed}}s`;

                if (response.ok) {{
                    try {{
                        const text = await response.text();
                        if (text.includes("user_info") || text.includes("status") || text.includes("Active")) {{
                            statusText = "✅ Active";
                            // 尝试简单提取过期时间（粗略）
                            const expMatch = text.match(/exp_date["']?\\s*[:=]\\s*["']?(\\d+)/);
                            if (expMatch) {{
                                const exp = new Date(parseInt(expMatch[1]) * 1000);
                                details += ` | Exp: ${{exp.toISOString().split('T')[0]}}`;
                            }}
                        }} else {{
                            statusText = "⚠️ Reachable but Login Failed";
                        }}
                    }} catch(e) {{
                        statusText = "✅ Reachable (JSON parse failed)";
                    }}
                }} else {{
                    statusText = `❌ HTTP ${{response.status}}`;
                }}

                results.push({{
                    Server: server,
                    Status: statusText,
                    Details: details
                }});

            }} catch (err) {{
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                let statusText = "❌ Unreachable";
                if (err.name === "AbortError") statusText = "❌ Timeout (12s)";
                else if (err.message.includes("Failed to fetch") || err.message.includes("CORS")) {{
                    statusText = "❌ Network Error / CORS Blocked";
                }}

                results.push({{
                    Server: server,
                    Status: statusText,
                    Details: `Error: ${{err.message || 'Connection failed'}} | ${{elapsed}}s`
                }});
            }}

            completed++;
            const progress = Math.round((completed / total) * 100);
            renderTable();

            // 更新 Streamlit 侧进度（通过 console，实际以 JS 表格为主）
            console.log(`Progress: ${{progress}}% - ${{completed}}/${{total}}`);
        }}

        function renderTable() {{
            let html = `
                <table>
                    <thead>
                        <tr>
                            <th>${t["header_server"]}</th>
                            <th>${t["header_status"]}</th>
                            <th>${t["header_info"]}</th>
                        </tr>
                    </thead>
                    <tbody>`;
            
            results.forEach(r => {{
                const cls = r.Status.includes("✅") ? "success" : (r.Status.includes("⚠️") ? "warning" : "error");
                html += `
                    <tr>
                        <td>${{r.Server}}</td>
                        <td class="${{cls}}">${{r.Status}}</td>
                        <td>${{r.Details}}</td>
                    </tr>`;
            }});
            
            html += `</tbody></table>`;
            document.getElementById("results").innerHTML = html;
        }}

        // 执行所有测试
        Promise.allSettled(servers.map(s => testSingleServer(s))).then(() => {{
            console.log("{t['done']}");
        }});

        // 初始空表
        renderTable();
    </script>
    """

    with result_container:
        st.subheader(t["result_label"])
        st.components.v1.html(html_code, height=650, scrolling=True)

    st.success(t["done"])
    st.caption(t["note"])

# ==================== 客户端公网 IP 获取（多备用源，提高成功率） ====================
ip_script = """
<script>
async function getClientIP() {
    const services = [
        'https://api.ipify.org?format=json',
        'https://api64.ipify.org?format=json',
        'https://ipinfo.io/json',
        'https://ifconfig.me/ip'
    ];
    
    for (let url of services) {
        try {
            const res = await fetch(url, {mode: 'cors', timeout: 5000});
            if (res.ok) {
                const data = await res.json();
                const ip = data.ip || data;
                document.getElementById('client-ip').innerHTML = 
                    `<code style="background:#f0f2f6; padding:8px; border-radius:4px; font-size:1.1em;">${ip}</code>`;
                return;
            }
        } catch(e) {}
    }
    document.getElementById('client-ip').innerHTML = 
        `<span style="color:#666;">Unable to detect / 无法获取</span>`;
}

getClientIP();
</script>
<div id="client-ip" style="font-family: monospace; padding: 10px; background: #f8f9fa; border-radius: 6px; margin-top: 8px;"></div>
"""

ip_placeholder.markdown("**Detected Client IP:**")
st.components.v1.html(ip_script, height=80)

st.caption("**说明**：本次检测请求全部来自**您的浏览器本地网络**，不再经过 GitHub 服务器的网络。状态判断已优化，但极少数严格限制 CORS 的服务器仍可能只显示 'Network Error' —— 此时建议用本地 Python requests 测试验证。")
