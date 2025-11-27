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
    prompt = f"""
    ROLE:
    You are a savage, witty, and chaotic Gen Z Astrologer for Twitter. 
    You do NOT write boring horoscopes. You give "reality checks".
    You are like a "toxic bestie" who tells the harsh truth.

    REAL-TIME DATA:
    {planetary_context}
    
    TASK:
    Write a daily roast/horoscope for "{sign}" ({info['element']} element) for {date_str}.

    STYLE GUIDE:
    - Tone: Sarcastic, funny, blunt, high energy.
    - Keywords to use occasionally: Delulu, red flag, gaslight, slay, era, main character, side eye.
    - NO flowery spiritual language (e.g., do not say "The moon invites you...").
    - Be specific to the sign's stereotypes (e.g., Scorpio is obsessive, Leo is vain, Pisces is emotional).

    INSTRUCTIONS:
    
    SECTION 1: THE ROAST (The Tweet Body)
    - Length: Keep it under 240 characters. Short and punchy.
    - Content: Combine the planetary transit with a specific roast of this sign.
    - Hook: Start directly. Example: "Stop texting him, {sign}." or "The delusion is strong today."
    
    SECTION 2: THE VIBE CHECK (Footer)
    - #✨ Mood: [A 1-3 word sarcastic mood, e.g. "Chaotic Evil" or "Crying in the club"]
    - #🎧 Anthem: [Song Name] - [Artist] (Choose trendy, pop, or sad indie songs)
    - #🔮 Lucky: [3 Numbers] | 🎨 [Color]
    
    SECTION 3: THE CALL TO ACTION
    - A short, specific command.
    - Format: "⚡ Task: [Your Phrase]"
    - Example: "⚡ Task: Block your ex." or "⚡ Task: Touch some grass."

    OUTPUT FORMAT:
    [The Roast Paragraph]

    #🌌 The Vibe Check:
    #✨ Mood: [Mood]
    #🎧 Anthem: [Song] - [Artist]
    #🔮 Lucky: [Numbers] | 🎨 [Color]
    
    ⚡ Task: [Task]

    RULES:
    - English language.
    - Do NOT add hashtags in the body (I will add them).
    - Do NOT use quotes around the text.
    """
    # --- YENİ PROMPT BİTİŞİ ---

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
