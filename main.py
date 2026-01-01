import os
import time
import datetime
import random
import math
import ephem
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. Ayarları Yükle
load_dotenv()

# --- API BAĞLANTILARI ---
# Model isimlerini en stabil versiyon olan 1.5-flash ve 1.5-pro olarak güncelledik
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    client = tweepy.Client(
        consumer_key=os.getenv("X_CONSUMER_KEY"),
        consumer_secret=os.getenv("X_CONSUMER_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )
    print("✅ Twitter Bağlantısı Başarılı!")
except Exception as e:
    print(f"⚠️ Twitter Bağlantı Hatası: {e}")
    client = None

# --- 2. GÜÇLÜ ASTROLOJİ MOTORU (EPHEM) ---
def get_zodiac_sign(lon_degrees):
    zodiacs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    index = int(lon_degrees / 30)
    return zodiacs[index % 12]

def calculate_daily_transits():
    try:
        observer = ephem.Observer()
        observer.date = datetime.datetime.now()
        planets = {
            "Sun": ephem.Sun(), "Moon": ephem.Moon(), "Mercury": ephem.Mercury(),
            "Venus": ephem.Venus(), "Mars": ephem.Mars(), "Jupiter": ephem.Jupiter(),
            "Saturn": ephem.Saturn(), "Uranus": ephem.Uranus(), "Neptune": ephem.Neptune(),
            "Pluto": ephem.Pluto()
        }
        transit_data = "REAL-TIME SKY DATA:\n"
        for name, body in planets.items():
            body.compute(observer)
            ecl = ephem.Ecliptic(body)
            lon_deg = math.degrees(ecl.lon)
            sign = get_zodiac_sign(lon_deg)
            transit_data += f"- {name}: in {sign}\n"
        return transit_data
    except Exception:
        return "Planetary Data Unavailable."

ZODIAC_INFO = {
    "Aries": {"symbol": "♈", "date": "(Mar 21 - Apr 19)", "element": "Fire"},
    "Taurus": {"symbol": "♉", "date": "(Apr 20 - May 20)", "element": "Earth"},
    "Gemini": {"symbol": "♊", "date": "(May 21 - Jun 20)", "element": "Air"},
    "Cancer": {"symbol": "♋", "date": "(Jun 21 - Jul 22)", "element": "Water"},
    "Leo": {"symbol": "♌", "date": "(Jul 23 - Aug 22)", "element": "Fire"},
    "Virgo": {"symbol": "♍", "date": "(Aug 23 - Sep 22)", "element": "Earth"},
    "Libra": {"symbol": "♎", "date": "(Sep 23 - Oct 22)", "element": "Air"},
    "Scorpio": {"symbol": "♏", "date": "(Oct 23 - Nov 21)", "element": "Water"},
    "Sagittarius": {"symbol": "♐", "date": "(Nov 22 - Dec 21)", "element": "Fire"},
    "Capricorn": {"symbol": "♑", "date": "(Dec 22 - Jan 19)", "element": "Earth"},
    "Aquarius": {"symbol": "♒", "date": "(Jan 20 - Feb 18)", "element": "Air"},
    "Pisces": {"symbol": "♓", "date": "(Feb 19 - Mar 20)", "element": "Water"}
}

HASHTAG_POOL = ["#Astrology", "#Horoscope", "#Zodiac", "#DailyHoroscope", "#Spirituality", "#Energy", "#Vibe", "#Cosmic"]

def generate_optimized_tweet(sign, info, planetary_context):
    # En güvenilir model isimleri
    MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    prompt = f"""
    ROLE: 
    You are a witty, sarcastic, and slightly chaotic Cosmic Oracle. 
    You give 'tough love' and unfiltered cosmic truths. 

    TARGET: {sign} ({info['element']})
    PLANETARY DATA: {planetary_context}

    INSTRUCTIONS:
    - Write a short, viral-style tweet about the new year 2026.
    - Start with a direct, sarcastic observation.
    - Include 'Mood:' and 'Task:'.
    - DO NOT use emojis. DO NOT use hashtags.
    - Body text must be UNDER 160 characters.
    
    FORMAT:
    [Insight]
    Mood: [1-2 words]
    Task: [Short command]
    """

    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, safety_settings=safety_settings)
            content = (response.text or "").strip()
            if content:
                return content.replace('"', '').replace('*', '')
        except Exception as e:
            if "429" in str(e):
                print(f"⏳ Gemini Kotası doldu, 75 saniye zorunlu mola...")
                time.sleep(75)
            else:
                print(f"⚠️ {model_name} hatası: {e}")
            continue
    return None

# --- ANA AKIŞ ---
print(f"\n✨ COSMIC ENGINE STARTING ({datetime.date.today()})\n")
gunluk_gezegen_konumlari = calculate_daily_transits()

zodiac_list = list(ZODIAC_INFO.items())

for i, (sign, info) in enumerate(zodiac_list):
    print(f"⚡ [{i+1}/12] Generating for {sign}...")
    
    content = generate_optimized_tweet(sign, info, gunluk_gezegen_konumlari)
    
    if content:
        header = f"{info['symbol']} {sign.upper()} {info['date']}\n\n"
        main_tag = f"#{sign}"
        extra_tags = random.sample(HASHTAG_POOL, 2)
        footer = f"\n\n{main_tag} {' '.join(extra_tags)}"
        
        tweet_text = f"{header}{content}{footer}"
        
        if len(tweet_text) > 280:
            allowed_content_len = 280 - len(header) - len(footer) - 3
            content = content[:allowed_content_len] + "..."
            tweet_text = f"{header}{content}{footer}"
        
        print(f"📝 TWEET ({len(tweet_text)} chars):\n{tweet_text}")
        
        if client:
            try:
                client.create_tweet(text=tweet_text)
                print("✅ Başarıyla paylaşıldı.")
            except Exception as e:
                print(f"⚠️ Twitter Paylaşım Hatası: {e}")
        
        # Son burç değilse 2 dakika bekle
        if sign != "Pisces":
            wait_seconds = 120 # 2 dakika sabit bekleme
            print(f"\n☕ Kota koruması aktif: Bir sonraki burç ({zodiac_list[i+1][0]}) için 2 dakika bekleniyor...")
            time.sleep(wait_seconds)
            print("-" * 40)
    else:
        print(f"❌ {sign} için içerik üretilemedi.")

print("\n🎉 Tüm burçlar başarıyla işlendi ve paylaşıldı.")
