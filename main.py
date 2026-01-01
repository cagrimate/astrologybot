import os
import time
import datetime
import random
import math
import ephem
import tweepy
# Yeni kütüphane: google-genai
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Ayarları Yükle
load_dotenv()

# --- API BAĞLANTILARI ---
# Yeni nesil GenAI istemcisi
gen_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

# --- 2. ASTROLOJİ MOTORU (EPHEM) ---
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
    # Stabil model ismi
     MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
    prompt = f"""
    ROLE: Witty, sarcastic Cosmic Oracle.
    TARGET: {sign} ({info['element']})
    PLANETARY DATA: {planetary_context}
    INSTRUCTIONS:
    - Write a short, viral-style tweet about the new year 2026.
    - Start with a direct, sarcastic observation.
    - Include 'Mood:' and 'Task:'.
    - DO NOT use emojis or hashtags.
    - Body text UNDER 160 characters.
    """

    try:
        response = gen_client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                ]
            )
        )
        content = response.text.strip()
        if content:
            return content.replace('"', '').replace('*', '')
    except Exception as e:
        if "429" in str(e):
            print("⏳ Gemini Kotası doldu, mola veriliyor...")
            time.sleep(75)
        else:
            print(f"⚠️ Gemini hatası: {e}")
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
        footer = f"\n\n#{sign} {' '.join(random.sample(HASHTAG_POOL, 2))}"
        tweet_text = f"{header}{content}{footer}"
        
        # Twitter limit kontrolü
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
        
        print(f"📝 TWEET:\n{tweet_text}")
        
        if client:
            try:
                client.create_tweet(text=tweet_text)
                print("✅ Başarıyla paylaşıldı.")
            except Exception as e:
                print(f"⚠️ Twitter Hatası: {e}")
        
        if sign != "Pisces":
            print(f"\n☕ 120 saniye bekleniyor (Kota Koruması)...")
            time.sleep(120)
            print("-" * 40)
    else:
        print(f"❌ {sign} içeriği üretilemedi.")

print("\n🎉 Tüm burçlar tamamlandı.")
