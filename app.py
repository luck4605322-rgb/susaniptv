import streamlit as st
import time
import pandas as pd

# ==================== 1. 多语言字典（新增欧美语言 + WhatsApp） ====================
LANGUAGES = {
    "简体中文": {
        "title": "IPTVNator 网页批量检测工具 v1.8（客户端检测）--作者susan, WhatsApp: +8615573857383",
        "username": "用户名", 
        "password": "密码", 
        "servers": "服务器地址（一行一个）",
        "start_btn": "🚀 从我的本地网络开始批量检测", 
        "result_label": "检测结果", 
        "warning": "请填写完整信息！",
        "testing": "正在从您的浏览器直接检测...",
        "header_server": "服务器", 
        "header_status": "状态", 
        "header_info": "详细信息",
        "your_ip": "您的公网 IP", 
        "client_note": "✅ 检测现在从您的本地网络发起（真实家宽/流量/VPN）"
    },
    "English": {
        "title": "IPTVNator Web Batch Tester v1.8 (Client-Side) --Author susan, WhatsApp: +8615573857383",
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
    },
    "Español": {
        "title": "Probador Masivo IPTV v1.8 (Detección del Cliente) --Autor susan, WhatsApp: +8615573857383",
        "username": "Usuario", 
        "password": "Contraseña", 
        "servers": "Direcciones del servidor (una por línea)",
        "start_btn": "🚀 Iniciar prueba masiva desde mi red local", 
        "result_label": "Resultados de la prueba", 
        "warning": "¡Por favor complete toda la información!",
        "testing": "Probando directamente desde su navegador...",
        "header_server": "Servidor", 
        "header_status": "Estado", 
        "header_info": "Detalles",
        "your_ip": "Su IP Pública", 
        "client_note": "✅ La detección ahora se ejecuta desde su red local (fibra / móvil / VPN real)"
    },
    "Français": {
        "title": "Testeur IPTV Batch v1.8 (Côté Client) --Auteur susan, WhatsApp: +8615573857383",
        "username": "Nom d'utilisateur", 
        "password": "Mot de passe", 
        "servers": "Adresses des serveurs (une par ligne)",
        "start_btn": "🚀 Lancer le test depuis mon réseau local", 
        "result_label": "Résultats du test", 
        "warning": "Veuillez remplir toutes les informations !",
        "testing": "Test en cours directement depuis votre navigateur...",
        "header_server": "Serveur", 
        "header_status": "Statut", 
        "header_info": "Détails",
        "your_ip": "Votre IP Publique", 
        "client_note": "✅ Le test s'exécute maintenant depuis votre réseau local (fibre / mobile / VPN réel)"
    },
    "Deutsch": {
        "title": "IPTV Batch Tester v1.8 (Client-Seite) --Autor susan, WhatsApp: +8615573857383",
        "username": "Benutzername", 
        "password": "Passwort", 
        "servers": "Serveradressen (eine pro Zeile)",
        "start_btn": "🚀 Batch-Test von meinem lokalen Netzwerk starten", 
        "result_label": "Testergebnisse", 
        "warning": "Bitte füllen Sie alle Felder aus!",
        "testing": "Testet direkt von Ihrem Browser aus...",
        "header_server": "Server", 
        "header_status": "Status", 
        "header_info": "Details",
        "your_ip": "Ihre öffentliche IP", 
        "client_note": "✅ Die Prüfung läuft jetzt von Ihrem lokalen Netzwerk (echtes Breitband / Mobil / VPN)"
    },
    "Português": {
        "title": "Testador IPTV em Lote v1.8 (Lado do Cliente) --Autor susan, WhatsApp: +8615573857383",
        "username": "Nome de usuário
