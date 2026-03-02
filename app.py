

from flask import Flask, render_template, request
import http.client
import urllib.parse
import json
import requests

app = Flask(__name__)

# ============================
# 🔹 Amazon Data Fetch Function
# ============================
def fetch_amazon_data(query):
    conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "ed181d4595msh6bb9094843920d3p1e6e2ajsna502f04a8e64",
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    encoded_query = urllib.parse.quote(query)
    conn.request("GET", f"/search?query={encoded_query}&country=US", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")

    try:
        response_data = json.loads(decoded_data)
        if "data" in response_data and "products" in response_data["data"]:
            return response_data["data"]["products"]
        return []
    except json.JSONDecodeError:
        print("❌ Failed to parse Amazon API response")
        return []

# ============================
# 🔹 Walmart Data Fetch Function (Updated API with requests)
# ============================
def fetch_walmart_data(query):
    url = "https://realtime-walmart-data.p.rapidapi.com/search"

    querystring = {
        "keyword": query,
        "page": "1",
        "sort": "price_high"
    }

    headers = {
        'x-rapidapi-key': "439c2eeeebmshb8a3324b65fc1adp1ed1adjsnea3faa1113e3",
        'x-rapidapi-host': "realtime-walmart-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise exception for bad status codes
        response_data = response.json()

        # Handle response from the new Walmart API
        products = response_data.get("results", [])

        if not isinstance(products, list):
            return []

        # Normalize Walmart data into your expected structure
        normalized_products = []
        for item in products:
            normalized_products.append({
                "title": item.get("name"),
                "image": item.get("image"),
                "link": item.get("canonicalUrl"),
                "price": {
                    "currentPrice": item.get("price"),
                    "originalPrice": item.get("originalPrice")
                },
                "ratings": item.get("rating"),
                "reviewsCount": item.get("numberOfReviews"),
                "shippingMessage": item.get("availability")
            })
        return normalized_products

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Walmart data: {e}")
        return []
    except json.JSONDecodeError:
        print("❌ JSON decode error in Walmart response")
        return []

# ============================
# 🔹 Flask Route
# ============================
@app.route('/', methods=['GET', 'POST'])
def index():
    amazon_results = []
    walmart_results = []
    query = ""

    if request.method == 'POST':
        query = request.form['query']
        amazon_results = fetch_amazon_data(query)
        walmart_results = fetch_walmart_data(query)

    return render_template('index.html', amazon=amazon_results, walmart=walmart_results, query=query)

# ============================
# 🔹 Run the Flask App
# ============================
if __name__ == '__main__':
    app.run(debug=True)
