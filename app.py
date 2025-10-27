# from flask import Flask, render_template, request
# import http.client
# import urllib.parse
# import json

# app = Flask(__name__)

# # =========================
# # 🔹 Fetch Amazon Data (Reverted Original Logic)
# # =========================
# def fetch_amazon_data(query):
#     conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")

#     headers = {
#         'x-rapidapi-key': "ed181d4595msh6bb9094843920d3p1e6e2ajsna502f04a8e64",
#         'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
#     }

#     encoded_query = urllib.parse.quote(query)
#     conn.request("GET", f"/search?query={encoded_query}&country=US", headers=headers)

#     res = conn.getresponse()
#     data = res.read()
#     decoded_data = data.decode("utf-8")

#     try:
#         response_data = json.loads(decoded_data)
#         if "data" in response_data and "products" in response_data["data"]:
#             return response_data["data"]["products"]
#         else:
#             print("⚠️ Amazon API returned no products.")
#             return []
#     except json.JSONDecodeError:
#         print("❌ Failed to parse Amazon API response as JSON")
#         print(decoded_data[:500])
#         return []


# # =========================
# # 🔹 Fetch Walmart Data (New API - Working)
# # =========================
# def fetch_walmart_data(query):
#     conn = http.client.HTTPSConnection("walmart2.p.rapidapi.com")

#     headers = {
#         'x-rapidapi-key': "7baeb12c8emsh9e0d44e7386000ap143ac7jsn3a8ebde0d12e",
#         'x-rapidapi-host': "walmart2.p.rapidapi.com"
#     }

#     encoded_query = urllib.parse.quote(query)
#     endpoint = f"/searchV2?query={encoded_query}"

#     conn.request("GET", endpoint, headers=headers)
#     res = conn.getresponse()
#     data = res.read()
#     decoded_data = data.decode("utf-8")

#     try:
#         response_data = json.loads(decoded_data)
#         items = response_data.get("itemsV2", [])

#         products = []
#         for item in items:
#             name = item.get("name", "No name available")
#             price = item.get("priceInfo", {}).get("currentPrice", {}).get("priceDisplay", "N/A")
#             image = item.get("imageInfo", {}).get("thumbnailUrl", "")
#             link = "https://www.walmart.com" + item.get("selectedProduct", {}).get("canonicalUrl", "#")
#             seller = item.get("sellerName", "Unknown seller")
#             rating = item.get("averageRating", "N/A")

#             products.append({
#                 "name": name,
#                 "price": price,
#                 "image": image,
#                 "link": link,
#                 "seller": seller,
#                 "rating": rating
#             })

#         return products

#     except json.JSONDecodeError:
#         print("❌ JSON decode error in Walmart response")
#         print(decoded_data[:500])
#         return []


# # =========================
# # 🔹 Flask Route
# # =========================
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     amazon_results = []
#     walmart_results = []
#     query = ""

#     if request.method == 'POST':
#         query = request.form['query']
#         amazon_results = fetch_amazon_data(query)
#         walmart_results = fetch_walmart_data(query)

#     return render_template('index.html', amazon=amazon_results, walmart=walmart_results, query=query)


# # =========================
# # 🔹 Run the Flask App
# # =========================
# if __name__ == '__main__':
#     app.run(debug=True)





























from flask import Flask, render_template, request
import http.client
import urllib.parse
import json

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
# 🔹 Walmart Data Fetch Function
# ============================
def fetch_walmart_data(query):
    conn = http.client.HTTPSConnection("walmart2.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "7baeb12c8emsh9e0d44e7386000ap143ac7jsn3a8ebde0d12e",
        'x-rapidapi-host': "walmart2.p.rapidapi.com"
    }

    encoded_query = urllib.parse.quote(query)
    endpoint = f"/searchV2?query={encoded_query}"

    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")

    try:
        response_data = json.loads(decoded_data)

        # ✅ Correct field from Walmart2 API
        if "itemsV2" in response_data:
            items = response_data["itemsV2"]

            # Normalize Walmart data into your expected structure
            normalized_products = []
            for item in items:
                price_info = item.get("priceInfo", {})
                current_price = None
                if isinstance(price_info.get("currentPrice"), dict):
                    current_price = price_info["currentPrice"].get("priceDisplay")
                elif isinstance(price_info.get("currentPrice"), (str, float, int)):
                    current_price = price_info["currentPrice"]

                normalized_products.append({
                    "title": item.get("name"),
                    "image": item.get("imageInfo", {}).get("thumbnailUrl"),
                    "link": f"https://www.walmart.com{item.get('canonicalUrl')}" if item.get("canonicalUrl") else None,
                    "price": {
                        "currentPrice": current_price,
                        "originalPrice": None
                    },
                    "ratings": item.get("averageRating"),
                    "reviewsCount": item.get("numberOfReviews"),
                    "shippingMessage": item.get("badges", {}).get("groups", [{}])[0].get("text") if item.get("badges") else None
                })
            return normalized_products

        return []

    except json.JSONDecodeError:
        print("❌ JSON decode error in Walmart response")
        print(decoded_data[:500])
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
