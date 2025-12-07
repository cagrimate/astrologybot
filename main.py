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
    
    # --- YENİ PROMPT BAŞLANGICI ---
   # --- YENİ "KAOS VE ETKİLEŞİM" PROMPTU ---
    prompt = f"""
    ROLE:
    You are a viral Twitter content creator specializing in "Roasted Astrology".
    Your goal is NOT to inform. Your goal is to TRIGGER ENGAGEMENT (Replies, QRTs).
    
    TARGET: {sign} ({info['element']} element)
    CONTEXT: {planetary_context}

    STRATEGY - "THE EMOTIONAL TRIGGER":
    Don't just write a sentence. Attack a specific insecurity or habit of this sign.
    Make them feel "exposed" or "attacked" so they HAVE to reply.

    CHOOSE ONE OF THESE 3 ANGLES RANDOMLY:
    1. The "I Bet You..." -> Bet on a bad habit they are doing right now.
       (e.g., "I bet $50 you're overthinking a text from 3 years ago right now.")
    2. The "Unpopular Opinion" -> Say something controversial about them.
       (e.g., "Unpopular opinion: You aren't mysterious, you're just emotionally unavailable.")
    3. The "Direct Challenge" -> Order them to stop doing something.
       (e.g., "Put the phone down. He's not coming back.")

    MANDATORY ENDING:
    End with a short, direct question to force a reply.
    Examples: "Am I wrong?", "Confess below 👇", "Rate your panic level 1-10."

    OUTPUT FORMAT:
    [The Trigger/Roast]
    
    [The Question/Call to Action]

    RULES:
    - Keep it under 200 characters total.
    - NO emojis in the text (I will add them).
    - NO hashtags (I will add them).
    - English slang: Use words like "Red flag", "Ick", "Trauma dump", "Situationship".
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
