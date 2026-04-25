import streamlit as st
import requests
import time
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# ==================== 1. 多国语言字典（扩展版） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v1.6--作者susan,whatsapp:+8615573857383",
        "username": "用户名", "password": "密码", "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 开始批量检测", "result_label": "检测结果", "warning": "请填写完整信息！",
        "header_server": "服务器", "header_status": "状态", "header_info": "详细信息",
        "your_ip": "您的公网 IP"
    },
    "English": {
        "title": "IPTVNator Web Tester v1.6--Author susan- whatsapp:+8615573857383",
        "username": "Username", "password": "Password", "servers": "Server Addresses (one per line)",
        "start_btn": "🚀 Start Batch Test", "result_label": "Test Results", "warning": "Please fill in all fields!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Your Public IP"
    },
    "日本語": {
        "title": "IPTVNator 一括検知ツール v1.6--Author susan- whatsapp:+8615573857383",
        "username": "ユーザー名", "password": "パスワード", "servers": "サーバーアドレス（1行に1つ）",
        "start_btn": "🚀 一括テスト開始", "result_label": "テスト結果", "warning": "情報をすべて入力してください！",
        "header_server": "サーバー", "header_status": "状態", "header_info": "詳細情報",
        "your_ip": "あなたのパブリックIP"
    },
    "한국어": {
        "title": "IPTVNator 일괄 검사 도구 v1.6--Author susan-whatsapp:+8615573857383",
        "username": "사용자 이름", "password": "비밀번호", "servers": "서버 주소 (한 줄에 하나씩)",
        "start_btn": "🚀 일괄 테스트 시작", "result_label": "테스트 결과", "warning": "모든 정보를 입력하세요!",
        "header_server": "서버", "header_status": "상태", "header_info": "상세 정보",
        "your_ip": "당신의 공인 IP"
    },
    "Español": {
        "title": "Probador de IPTV v1.6--Author susan-whatsapp:+8615573857383",
        "username": "Usuario", "password": "Password", "servers": "Servidores (uno por línea)",
        "start_btn": "🚀 Iniciar prueba", "result_label": "Resultados", "warning": "¡Por favor complete todo!",
        "header_server": "Servidor", "header_status": "Estado", "header_info": "Detalles",
        "your_ip": "Tu IP Pública"
    },
    "Français": {
        "title": "Testeur IPTV v1.6--Author susan-whatsapp:+8615573857383",
        "username": "Utilisateur", "password": "Mot de passe", "servers": "Serveurs (un par ligne)",
        "start_btn": "🚀 Lancer le test", "result_label": "Résultats", "warning": "Veuillez tout remplir !",
        "header_server": "Serveur", "header_status": "Statut", "header_info": "Détails",
        "your_ip": "Votre IP Publique"
    },
    "Deutsch": {
        "title": "IPTV Batch Tester v1.6--Author susan- whatsapp:+8615573857383",
        "username": "Benutzername", "password": "Passwort", "servers": "Serveradressen (eine pro Zeile)",
        "start_btn": "🚀 Batch-Test starten", "result_label": "Testergebnisse", "warning": "Bitte alles ausfüllen!",
        "header_server": "Server", "header_status": "Status", "header_info": "Details",
        "your_ip": "Ihre öffentliche IP"
    }
}

# ==================== 2. 工具函数 ====================
@st.cache_data(ttl=3600)  # 缓存1小时，避免频繁请求
def get_public_ip():
    """获取当前设备的公网IP"""
    try:
        # 使用 ifconfig.me 获取纯文本格式的 IP
        response = requests.get("https://ifconfig.me/ip", timeout=5)
        return response.text.strip()
    except Exception:
        return "Unknown / 无法获取"

def test_single_server(server, username, password, trans):
    if not server.startswith("http"): server = "http://" + server
    server = server.rstrip("/")
    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    start_time = time.time()
    
    try:
        resp = requests.get(base_url, headers=headers, timeout=12)
        elapsed = round(time.time() - start_time, 2)
        
        if resp.status_code != 200:
            return {"Server": server, "Status": "❌ HTTP " + str(resp.status_code), "Details": f"{elapsed}s"}
        
        data = resp.json()
        if "user_info" in data:
            ui = data["user_info"]
            status = ui.get("status", "Unknown")
            exp = ui.get("exp_date", "Never")
            if str(exp).isdigit():
                exp = time.strftime("%Y-%m-%d", time.localtime(int(exp)))
            return {"Server": server, "Status": "✅ Active", "Details": f"Status: {status} | Exp: {exp} | {elapsed}s"}
        return {"Server": server, "Status": "❌ Fail", "Details": "Login Failed"}
    except Exception:
        return {"Server": server, "Status": "❌ Error", "Details": "Timeout/Unreachable"}

# ==================== 3. Streamlit 页面布局 ====================
st.set_page_config(page_title="IPTV Batch Tester", layout="wide", page_icon="📺")

# 获取当前 IP
current_ip = get_public_ip()

# 侧边栏：语言、IP显示和控制
st.sidebar.title("Settings / 设定")
lang_choice = st.sidebar.selectbox("Language / 语言 / 言語", list(LANGUAGES.keys()))
t = LANGUAGES[lang_choice]

st.sidebar.markdown("---")
st.sidebar.subheader(t["your_ip"])
st.sidebar.code(current_ip, language="bash") # 使用代码框显示，方便复制
st.sidebar.caption("Detected connection source IP")

# 主界面
st.title(t["title"])
st.markdown("---")

col_input, col_info = st.columns([2, 1])

with col_input:
    c1, c2 = st.columns(2)
    with c1:
        user = st.text_input(t["username"])
    with c2:
        pwd = st.text_input(t["password"], type="password")
    
    servers_text = st.text_area(t["servers"], height=200, placeholder="http://example.com:8080")

with col_info:
    st.info(f"""
    **Tips:**
    - **Current IP:** `{current_ip}`
    - Use 'http://' or 'https://'
    - Multi-threading is enabled (fast)
    - Results can be sorted by clicking headers
    """)

# 开始按钮
if st.button(t["start_btn"], type="primary", use_container_width=True):
    if not user or not pwd or not servers_text:
        st.warning(t["warning"])
    else:
        servers = [s.strip() for s in servers_text.splitlines() if s.strip()]
        results = []
        
        progress_bar = st.progress(0)
        status_msg = st.empty()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_single_server, s, user, pwd, t) for s in servers]
            for i, f in enumerate(futures):
                results.append(f.result())
                progress_bar.progress((i + 1) / len(servers))
                status_msg.text(f"Testing: {i+1}/{len(servers)}")
        
        st.subheader(t["result_label"])
        df = pd.DataFrame(results)
        df.columns = [t["header_server"], t["header_status"], t["header_info"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.success("Done!")
