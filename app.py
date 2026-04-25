import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import requests
import threading
import time
from collections import defaultdict

# ==================== 多国语言字典 ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 批量检测工具 v1.6",
        "username": "用户名:",
        "password": "密码:",
        "servers": "服务器地址（一行一个）:",
        "example": "填入示例",
        "start_btn": "🚀 开始批量检测",
        "lang_label": "界面语言 / Language:",
        "result_label": "检测结果（实时）:",
        "footer": "v1.6 本地EXE版 • 不受CORS限制 • 结果更真实",
        "warning": "请填写服务器列表、账号和密码！",
        "running": "🚀 开始检测 {0} 个服务器...",
        "only_first": "   → 只对第一个成功登录的服务器检测直播/电影数量和语言分类\n\n",
        "single": "   → 将检测直播数量、电影数量和常用语言分类\n\n",
        "detecting": "[{0}/{1}] 检测中: {2}\n",
        "complete": "✅ 批量检测完成！共检测 {0} 个服务器。",
        "http_error": "❌ HTTP错误 {0} | 耗时 {1}s",
        "no_userinfo": "❌ 登录失败（无 user_info） | 耗时 {0}s",
        "timeout": "❌ 超时 (>15s)",
        "conn_fail": "❌ 连接失败 (服务器不可达或被阻挡)",
        "unknown": "❌ 未知错误: {0}",
        "available": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | 直播: {3}个 | 电影: {4}个{5}",
        "no_resource": "✅ 可用 | 耗时 {0}s | 状态: {1} | 过期: {2} | （资源已检测过其他服务器）",
        "lang_stats": " | 语言: {0}"
    },
    "English": {
        "title": "IPTVNator Batch Tester v1.6",
        "username": "Username:",
        "password": "Password:",
        "servers": "Server Addresses (one per line):",
        "example": "Load Example",
        "start_btn": "🚀 Start Batch Test",
        "lang_label": "Interface Language:",
        "result_label": "Test Results (Live):",
        "footer": "v1.6 Local EXE • No CORS Limitation • More Accurate Results",
        "warning": "Please fill in servers, username and password!",
        "running": "🚀 Testing {0} servers...",
        "only_first": "   → Only first successful server checks live/movies/languages\n\n",
        "single": "   → Will check live count, movie count and languages\n\n",
        "detecting": "[{0}/{1}] Testing: {2}\n",
        "complete": "✅ Batch test completed! Tested {0} servers.",
        "http_error": "❌ HTTP Error {0} | Time {1}s",
        "no_userinfo": "❌ Login failed (no user_info) | Time {0}s",
        "timeout": "❌ Timeout (>15s)",
        "conn_fail": "❌ Connection failed (unreachable or blocked)",
        "unknown": "❌ Unknown error: {0}",
        "available": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | Live: {3} | Movies: {4}{5}",
        "no_resource": "✅ Available | Time {0}s | Status: {1} | Exp: {2} | (Resources checked on another server)",
        "lang_stats": " | Languages: {0}"
    },
    # 西班牙语和法语保持原样（如果你需要可告诉我补充）
    "Español": {**LANGUAGES["English"], "title": "Herramienta de Prueba IPTVNator v1.6", "footer": "..."},
    "Français": {**LANGUAGES["English"], "title": "Outil de Test IPTVNator v1.6", "footer": "..."},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
}

LANGUAGE_MAP = {
    "english": "English", "eng": "English", "arabic": "Arabic", "ara": "Arabic",
    "chinese": "Chinese", "中文": "Chinese", "spanish": "Spanish", "french": "French",
    "german": "German", "italian": "Italian", "russian": "Russian", "turkish": "Turkish",
}

def get_language_stats(categories):
    from collections import defaultdict
    lang_count = defaultdict(int)
    for cat in categories or []:
        if not isinstance(cat, dict):
            continue
        name = str(cat.get("category_name", "")).lower()
        for key, lang in LANGUAGE_MAP.items():
            if key in name:
                lang_count[lang] += 1
                break
        else:
            if any(w in name for w in ["international", "world", "global", "sport", "news"]):
                lang_count["International"] += 1
    return dict(lang_count)

def test_single_server(server, username, password, result_text, trans, check_resources=True):
    if not server.startswith(("http://", "https://")):
        server = "http://" + server
    server = server.rstrip("/")
    
    base_url = f"{server}/player_api.php?username={username}&password={password}"
    
    start_time = time.time()
    session = requests.Session()
    
    try:
        resp = session.get(base_url, headers=HEADERS, timeout=15, allow_redirects=True)
        elapsed = round(time.time() - start_time, 2)
        
        if resp.status_code != 200:
            result = trans["http_error"].format(resp.status_code, elapsed)
            result_text.insert(tk.END, f"{server} → {result}\n\n")
            result_text.see(tk.END)
            return result, False
        
        data = resp.json()
        if not isinstance(data, dict) or "user_info" not in data:
            result = trans["no_userinfo"].format(elapsed)
            result_text.insert(tk.END, f"{server} → {result}\n\n")
            result_text.see(tk.END)
            return result, False
        
        ui = data.get("user_info", {})
        status = ui.get("status", "Unknown")
        exp = ui.get("exp_date", "永久")
        if str(exp).isdigit():
            exp = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(exp)))
        
        if check_resources:
            # 检测直播和电影数量
            live_c = vod_c = 0
            try:
                r = session.get(f"{base_url}&action=get_live_streams", headers=HEADERS, timeout=12)
                if r.status_code == 200 and isinstance(r.json(), list):
                    live_c = len(r.json())
            except:
                pass
            try:
                r = session.get(f"{base_url}&action=get_vod_streams", headers=HEADERS, timeout=12)
                if r.status_code == 200 and isinstance(r.json(), list):
                    vod_c = len(r.json())
            except:
                pass
            
            # 语言分类
            lang_info = ""
            try:
                r = session.get(f"{base_url}&action=get_live_categories", headers=HEADERS, timeout=10)
                if r.status_code == 200:
                    cats = r.json()
                    if isinstance(cats, list):
                        stats = get_language_stats(cats)
                        if stats:
                            parts = [f"{k}({v})" for k, v in sorted(stats.items(), key=lambda x: -x[1])]
                            lang_info = trans["lang_stats"].format(", ".join(parts[:8]))
            except:
                pass
            
            result = trans["available"].format(elapsed, status, exp, live_c, vod_c, lang_info)
        else:
            result = trans["no_resource"].format(elapsed, status, exp)
        
        result_text.insert(tk.END, f"{server} → {result}\n\n")
        result_text.see(tk.END)
        return result, True
        
    except requests.exceptions.Timeout:
        result = trans["timeout"]
    except requests.exceptions.ConnectionError:
        result = trans["conn_fail"]
    except Exception as e:
        result = trans["unknown"].format(str(e)[:100])
    
    result_text.insert(tk.END, f"{server} → {result}\n\n")
    result_text.see(tk.END)
    return result, False

# ==================== 主窗口 ====================
class IPTVApp:
    def __init__(self):
        self.current_lang = "简体中文"
        self.trans = LANGUAGES[self.current_lang]
        
        self.root = tk.Tk()
        self.root.title(self.trans["title"])
        self.root.geometry("1180x820")
        
        self.title_label = tk.Label(self.root, text=self.trans["title"], font=("微软雅黑", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # 语言切换
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=5)
        tk.Label(lang_frame, text=self.trans["lang_label"]).pack(side="left", padx=5)
        self.lang_var = tk.StringVar(value=self.current_lang)
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=list(LANGUAGES.keys()), state="readonly")
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # 输入区
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=30, pady=10, fill="x")
        
        tk.Label(input_frame, text=self.trans["username"]).grid(row=0, column=0, sticky="w", pady=5)
        self.user_entry = tk.Entry(input_frame, width=70, font=("Consolas", 10))
        self.user_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(input_frame, text=self.trans["password"]).grid(row=1, column=0, sticky="w", pady=5)
        self.pass_entry = tk.Entry(input_frame, width=70, show="*", font=("Consolas", 10))
        self.pass_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(input_frame, text=self.trans["servers"]).grid(row=2, column=0, sticky="nw", pady=5)
        self.server_text = scrolledtext.ScrolledText(input_frame, height=10, width=85, font=("Consolas", 10))
        self.server_text.grid(row=2, column=1, pady=5)
        
        tk.Button(input_frame, text=self.trans["example"], command=self.load_example).grid(row=3, column=1, sticky="e", pady=5)
        
        # 按钮 + 进度条
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)
        self.start_btn = tk.Button(btn_frame, text=self.trans["start_btn"], font=("微软雅黑", 12, "bold"),
                                   bg="#00aa00", fg="white", width=25, height=2, command=self.start_batch_test)
        self.start_btn.pack(side="left", padx=20)
        
        self.progress = ttk.Progressbar(btn_frame, mode="indeterminate", length=500)
        self.progress.pack(side="left", padx=10)
        
        # 结果区
        tk.Label(self.root, text=self.trans["result_label"], font=("微软雅黑", 10)).pack(anchor="w", padx=30)
        self.result_text = scrolledtext.ScrolledText(self.root, height=28, font=("Consolas", 10))
        self.result_text.pack(padx=30, pady=10, fill="both", expand=True)
        
        self.footer_label = tk.Label(self.root, text=self.trans["footer"], fg="gray")
        self.footer_label.pack(pady=8)
        
        self.root.mainloop()
    
    def change_language(self, event=None):
        new_lang = self.lang_var.get()
        if new_lang == self.current_lang:
            return
        self.current_lang = new_lang
        self.trans = LANGUAGES[new_lang]
        self.root.title(self.trans["title"])
        self.title_label.config(text=self.trans["title"])
        self.footer_label.config(text=self.trans["footer"])
        self.start_btn.config(text=self.trans["start_btn"])
        self.result_text.insert(tk.END, f"✅ 语言已切换为 {new_lang}\n\n")
    
    def load_example(self):
        self.server_text.delete("1.0", tk.END)
        self.server_text.insert(tk.END, "http://example.com:8080\nhttp://test.tv:12345")
    
    def start_batch_test(self):
        servers = [s.strip() for s in self.server_text.get("1.0", tk.END).strip().splitlines() if s.strip()]
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not servers or not username or not password:
            messagebox.showwarning("警告", self.trans["warning"])
            return
        
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, self.trans["running"].format(len(servers)) + "\n\n")
        
        def run_tests():
            self.start_btn.config(state="disabled")
            self.progress.start()
            resource_checked = False
            
            for i, server in enumerate(servers, 1):
                self.result_text.insert(tk.END, self.trans["detecting"].format(i, len(servers), server))
                self.result_text.see(tk.END)
                
                check_res = (not resource_checked) and (i == 1 or len(servers) == 1)
                _, success = test_single_server(server, username, password, self.result_text, self.trans, check_res)
                
                if success and not resource_checked:
                    resource_checked = True
                
                time.sleep(0.6)   # 避免请求过快被封
            
            self.progress.stop()
            self.start_btn.config(state="normal")
            self.result_text.insert(tk.END, "\n" + self.trans["complete"].format(len(servers)) + "\n")
            messagebox.showinfo("完成", self.trans["complete"].format(len(servers)))
        
        threading.Thread(target=run_tests, daemon=True).start()

if __name__ == "__main__":
    IPTVApp()
