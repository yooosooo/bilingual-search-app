from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from googletrans import Translator
from bs4 import BeautifulSoup
import requests

# Replace these with your real credentials
GOOGLE_API_KEY = "AIzaSyArwsCiZ7RvTmRBDIPkUWSdHhmPO09WOms"
CSE_ID = "5664d3e8cd9c247ef"

# Set up Flask app
app = Flask(__name__,
            static_folder='../frontend', # for app.js,
            template_folder='../frontend', # for index.html
)       
CORS(app)

@app.route('/')
def home():
    return send_from_directory(app.template_folder, 'index.html')

# Set up Google Translate
translator = Translator()

def get_page_title(url):
    try:
        headers = { 'User-Agent': 'Mozilla/5.0' }  # Avoid 403 errors
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.title.string.strip() if soup.title else url
    except:
        pass
    return url  # Fallback to URL if anything fails

# Translate English query to Korean
def translate_to_korean(text):
    try:
        result = translator.translate(text, src='en', dest='ko')
        print("📤 Translated:", result.text)
        return result.text
    except Exception as e:
        print("❌ Translation error:", e)
        return "[Translation failed]"

# Perform Google Search via Custom Search API
def search_google(query):
    print(f"🔍 Searching Google for: {query}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": CSE_ID,
        "q": query
    }

    try:
        res = requests.get(url, params=params)
        print("🔵 Request URL:", res.url)
        print("🟡 Status code:", res.status_code)

        results = res.json()
        print("📦 Raw JSON:", results)

        if "items" not in results:
            print("❌ No 'items' found. API may be blocked or misconfigured.")
            return ["[No search results returned]"]

        links = [item["link"] for item in results["items"]]
        return links

    except Exception as e:
        print("❌ Google Search error:", e)
        return ["[Search failed]"]

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')

    print("🟢 Original query:", query)

    # Step 1: Translate to Korean
    translated_query = translate_to_korean(query)

    # Step 1: Translate to Korean
    translated_query = translate_to_korean(query)

    # Step 2: Search both queries
    english_urls = search_google(query)
    korean_urls = search_google(translated_query)

    # Step 3: Scrape page titles
    english_results = [{"title": get_page_title(url), "url": url} for url in english_urls]
    korean_results = [{"title": get_page_title(url), "url": url} for url in korean_urls]

    # Step 4: Send response
    return jsonify({
        "original_query": query,
        "translated_query": translated_query,
        "results": {
            "english": english_results,
            "korean": korean_results
        }
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
