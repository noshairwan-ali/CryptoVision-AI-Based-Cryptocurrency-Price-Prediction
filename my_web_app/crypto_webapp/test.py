# # import requests
# # from textblob import TextBlob
# # import os

# # # Replace with your actual Twitter Bearer Token
# # BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKFc1wEAAAAAlUmcbmqMw3xB1ebS1GUI2PPdMng%3D92K16QDYhsqnQBAgRAP0i98x9A87lEnGXbJ3AQoaBu15xEkeJh"

# # def get_coin_sentiment(coin_name):
# #     query = f"{coin_name} lang:en -is:retweet"
# #     url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=20&tweet.fields=text"

# #     headers = {
# #         "Authorization": f"Bearer {BEARER_TOKEN}"
# #     }

# #     response = requests.get(url, headers=headers)
# #     tweets = response.json()

# #     if "data" in tweets:
# #         print(f"\n📌 Recent Sentiment for {coin_name}:\n")
# #         for tweet in tweets["data"]:
# #             text = tweet["text"]
# #             sentiment = TextBlob(text).sentiment.polarity
# #             sentiment_type = (
# #                 "Positive" if sentiment > 0 else
# #                 "Negative" if sentiment < 0 else
# #                 "Neutral"
# #             )
# #             print(f"Tweet: {text}")
# #             print(f"Sentiment Score: {sentiment:.2f} → {sentiment_type}")
# #             print("-" * 60)
# #     else:
# #         print(f"No recent tweets found for {coin_name}.")

# # # Example usage
# # get_coin_sentiment("Ethereum")

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# create the app context
app = create_app()
with app.app_context():
    # Replace these values as needed
    email = "admin@example.com"
    username = "admin"
    password = "adminpass"

    # Create new admin user
    admin_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        is_admin=True
    )

    # Add to database
    db.session.add(admin_user)
    db.session.commit()
    print("✅ Admin user added successfully.")

# from app import create_app
# from app.models import User
# from app import db

# app = create_app()
# with app.app_context():
#     users = User.query.all()
#     for user in users:
#         print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")

# from app import create_app, db
# from app.models import Coin

# coins = {
#     'Bitcoin': 'BTC-USD',
#     'Ethereum': 'ETH-USD',
#     'BNB': 'BNB-USD',
#     'XRP': 'XRP-USD',
#     'Solana': 'SOL-USD',
#     'Cardano': 'ADA-USD',
#     'Polkadot': 'DOT-USD',
#     'Dogecoin': 'DOGE-USD',
#     'Litecoin': 'LTC-USD',
#     'Shiba Inu': 'SHIB-USD'
# }

# app = create_app()
# with app.app_context():
#     for name, ticker in coins.items():
#         if not Coin.query.filter_by(name=name).first():
#             db.session.add(Coin(name=name, coin_id=ticker))
#     db.session.commit()
#     print("✅ All coins with tickers added.")
