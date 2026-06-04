import streamlit as str
from google import genai
from memory_manager import LocalMemoryManager
import time

# =====================================================================
# 1. AYARLAR VE BAŞLANGIÇ
# =====================================================================
# Kendi API anahtarını buraya yapıştırmayı unutma!
GEMINI_API_KEY = "BURAYA_KENDİ_API_ANAHTARINIZI_YAZIN"

# Yeni Google GenAI istemcisini başlatıyoruz
client = genai.Client(api_key=GEMINI_API_KEY)

str.set_page_config(page_title="Hafızalı Yapay Zeka Asistanı", layout="wide")

if "memory_db" not in str.session_state:
    str.session_state.memory_db = LocalMemoryManager()

if "messages" not in str.session_state:
    str.session_state.messages = [
        {"role": "assistant", "content": "Selam! Ben senin hafızalı yapay zeka asistanınım. Konuştukça seni tanıyacağım ve hiçbir şeyi unutmayacağım. 😊"}
    ]

# =====================================================================
# 2. YAN PANEL (SIDEBAR) - HAFIZA ODASI
# =====================================================================
with str.sidebar:
    str.title("🧠 Yapay Zekanın Hafızası")
    str.subheader("Senin Hakkında Öğrendiklerim:")
    str.write("---")
    
    all_memories = str.session_state.memory_db.get_all_memories()
    
    if all_memories:
        for idx, memory in enumerate(all_memories):
            str.info(f"📌 {memory}")
    else:
        str.write("*Henüz hakkınızda kalıcı bir bilgi öğrenmedim. Sohbet ettikçe burası dolacak!*")

# =====================================================================
# 3. ANA PANEL - CHAT EKRANI
# =====================================================================
str.title("🤖 Akıllı Hafızalı Asistan")
str.caption("Google GenAI ve ChromaDB ile Güçlendirilmiş Yerel Yapay Zeka")

for message in str.session_state.messages:
    with str.chat_message(message["role"]):
        str.write(message["content"])

if user_input := str.chat_input("Mesajınızı yazın..."):
    
    with str.chat_message("user"):
        str.write(user_input)
    str.session_state.messages.append({"role": "user", "content": user_input})
    
    # 1. VERİ TABANINDAN HAFIZA SORGULAMA
    relevant_context = str.session_state.memory_db.get_relevant_context(user_input)
    
    # 2. GEMINI İÇİN SİHİRLİ PROMPT ŞABLONU
    system_prompt = f"""
    Sen hafızası olan, cana yakın ve çok zeki bir yapay zeka asistanısın. 
    Kullanıcıyla Türkçe konuşuyorsun.
    
    Kullanıcı hakkında geçmiş konuşmalardan hatırladığın gerçekler (Bağlam) şunlardır:
    {relevant_context}
    
    Şimdi kullanıcının son mesajına bu bilgilere dayanarak yanıt ver. Eğer hafızanda ilgili bir bilgi varsa bunu doğal bir şekilde cevabında kullan.
    """
    
    # 3. GEMINI'YE İSTEK ATMA VE CEVAP ALMA
    with str.chat_message("assistant"):
        with str.spinner("Düşünüyorum ve hatırlamaya çalışıyorum..."):
            # Bilgisayarında çalışan en güncel modeli çağırdık
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=f"{system_prompt}\n\nKullanıcı: {user_input}"
            )
            
            assistant_response = response.text
            str.write(assistant_response)
            
    str.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # =====================================================================
    # 4. YENİ HAFIZA ANALİZİ
    # =====================================================================
    memory_analyzer_prompt = f"""
    Aşağıdaki kullanıcı cümlesini analiz et. Eğer cümle kullanıcının ismi, yaşı, mesleği, hobileri, kişisel tercihleri (örn: şekersiz kahve severim, yazılımcıyım, kedim var vb.) gibi GELECEKTE HATIRLANMASI GEREKEN kalıcı bir bilgi içeriyorsa, SADECE o bilgiyi özetleyen kısa bir cümle yaz (Örn: 'Kullanıcı kahvesini şekersiz seviyor').
    Eğer cümlede gelecekte hatırlanmaya değer kalıcı kişisel bir bilgi YOKSA, SADECE 'YOK' yaz.
    
    Kullanıcı Cümlesi: "{user_input}"
    """
    
    analyzer_response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=memory_analyzer_prompt
    ).text.strip()
    
    if "YOK" not in analyzer_response.upper() and len(analyzer_response) > 3:
        memory_id = f"mem_{int(time.time())}"
        str.session_state.memory_db.save_information(analyzer_response, memory_id)
        time.sleep(0.5)
        str.rerun()