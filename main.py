import os
import time
import datetime
import random
import math
import ephem
import tweepy
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Ayarları Yükle
load_dotenv()

# --- API BAĞLANTILARI ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    client = tweepy.Client(
        consumer_key=os.getenv("X_CONSUMER_KEY"),
        consumer_secret=os.getenv("X_CONSUMER_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )
    print("✅ Twitter Bağlantısı Başarılı!")
except Exception:
    print("⚠️ Twitter Bağlantı Hatası (Test modu - Tweet atılmayacak)")
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

HASHTAG_POOL = [
    "#Astrology", "#Horoscope", "#Zodiac", "#DailyHoroscope", 
    "#Manifestation", "#Spirituality", "#Energy", "#Vibe", "#Cosmic"
]

def generate_optimized_tweet(sign, info, planetary_context):
    # Model isimlerine dokunulmadı
    MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
    # Prompt ilgi çekici, kısa ve sert (savage) olacak şekilde güncellendi
    # 280 Karakter sınırı için içerik 180 karakterle sınırlandırıldı.
    prompt = f"""
    ROLE: 
    You are a savage, witty, and slightly chaotic Astrologer. You don't give boring advice; you give "harsh truths" and punchy insights.

    TARGET: {sign} ({info['element']})
    SKY DATA: {planetary_context}

    INSTRUCTIONS:
    - Write a high-engagement, scannable tweet.
    - Start with a bold statement or a roast about their current energy.
    - Include a short, weirdly specific task or a "mood check".
    - STRIKT LIMIT: Max 180 characters for the body text. 
    - Use no hashtags and no emojis in your response.
    - Format: 
      [One savage insight]
      Mood: [1-2 words]
      Task: [Short command]
    """

    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            content = (response.text or "").strip()
            if content:
                content = content.replace('"', '')
                return content
        except Exception:
            continue
    return None

# --- ANA AKIŞ ---
print(f"\n✨ COSMIC ENGINE: AI GENERATED TIPS ({datetime.date.today()})\n")

gunluk_gezegen_konumlari = calculate_daily_transits()

for sign, info in ZODIAC_INFO.items():
    print(f"⚡ Generating for {sign}...")
    
    content = generate_optimized_tweet(sign, info, gunluk_gezegen_konumlari)
    
    if content:
        # Karakter sınırı (280) kontrolü
        header = f"{info['symbol']} {sign.upper()} {info['date']}\n\n"
        
        # Hashtag havuzundan tasarruf için 2 tane seçiyoruz
        main_tag = f"#{sign}"
        extra_tags = random.sample(HASHTAG_POOL, 2)
        footer = f"\n\n{main_tag} {' '.join(extra_tags)}"
        
        tweet_text = f"{header}{content}{footer}"
        
        # Sert Karakter Kontrolü (Twitter 280 limit)
        if len(tweet_text) > 280:
            allowed_content_len = 280 - len(header) - len(footer) - 3
            content = content[:allowed_content_len] + "..."
            tweet_text = f"{header}{content}{footer}"
        
        print(f"📝 TWEET ({len(tweet_text)} chars):\n{tweet_text}\n")
        
        if client:
            try:
                client.create_tweet(text=tweet_text)
                print("✅ Posted.")
                wait_time = random.randint(60, 120)
                print(f"☕ Waiting {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                print(f"⚠️ Post failed: {e}")
    else:
        print(f"❌ Failed generation for {sign}.")
    print("-" * 40)

print("🎉 All tweets processed.")
