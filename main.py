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

# Burç Bilgileri
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

# --- İNGİLİZCE HASHTAG HAVUZU ---
HASHTAG_POOL = [
    "#Astrology", "#Horoscope", "#Zodiac", "#DailyHoroscope", 
    "#ZodiacSigns", "#AstrologyPosts", "#Manifestation", "#Spirituality", 
    "#Energy", "#MoonPhase", "#Universe", "#Vibe", "#Healing", 
    "#Tarot", "#Mindfulness", "#SelfCare"
]

def generate_optimized_tweet(sign, info, planetary_context):
    today = datetime.date.today()
    date_str = today.strftime("%B %d")
    
    MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
    # --- YENİ "ASTROLOJİK İÇGÖRÜ + ETKİLEŞİM" PROMPTU ---
    prompt = f"""
    ROLE:
    You are a trendy, insightful, but sassy Astrologer. 
    You translate boring planetary movements into relatable, real-life drama.
    
    TARGET: {sign} ({info['element']} element)
    REAL-TIME SKY DATA: {planetary_context}

    TASK:
    Write a tweet that connects a specific planetary movement to a real-life situation.

    FORMULA (Follow this structure strictly):
    1. THE ASTRO FACT: Mention a specific planet/aspect from the data (e.g., "Moon in Scorpio", "Mercury squaring Saturn").
    2. THE TRANSLATION: Explain what this does to their mood or life today. Be specific (love, money, anxiety, work).
    3. THE HOOK: Ask a question related to that specific feeling to get a reply.

    TONE GUIDE:
    - Educational but fun. "Spill the tea" vibe.
    - Use phrases like: "Expect to feel...", "This energy is bringing...", "Don't be surprised if..."
    
    OUTPUT EXAMPLES (For tone reference):
    - "Moon is crossing your relationship sector today 🌙. You might feel a sudden urge to start a fight over nothing. Is it valid or are you just bored? Tell me 👇"
    - "With Mercury retrograde in your sign, your ex is likely typing... 💬 Don't answer. Who is the one person you're trying to avoid today?"

    RULES:
    - Length: Under 220 characters.
    - NO hashtags (I will add them).
    - English language.
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

print("🔭 Scanning the sky...")
gunluk_gezegen_konumlari = calculate_daily_transits()
print("-" * 40)

for sign, info in ZODIAC_INFO.items():
    print(f"⚡ Generating for {sign}...")
    
    content = generate_optimized_tweet(sign, info, gunluk_gezegen_konumlari)
    
    if content:
        # --- HASHTAG OLUŞTURMA (İNGİLİZCE) ---
        main_tag = f"#{sign}"
        extra_tags = random.sample(HASHTAG_POOL, 3)
        tags_str = f"{main_tag} {' '.join(extra_tags)}"
        
        # Tweet metnini birleştir (Tip artık content'in içinde geliyor)
        tweet_text = f"{info['symbol']} {sign.upper()} {info['date']}\n\n{content}\n\n{tags_str}"
        
        # Karakter Kontrolü
        print(f"\n📝 TWEET ({len(tweet_text)} chars):\n{tweet_text}\n")
        
        if client:
            try:
                client.create_tweet(text=tweet_text)
                print("✅ Posted.")
                
                wait_time = random.randint(60, 120)
                print(f"☕ Waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except tweepy.errors.Forbidden:
                print("⚠️ Hata: Tweet 280 karakteri geçti (X Premium yoksa kısaltmak gerekebilir).")
            except Exception as e:
                print(f"⚠️ Post failed: {e}")
    else:
        print(f"❌ Failed generation for {sign}.")
    
    print("-" * 40)

print("🎉 All tweets posted.")
