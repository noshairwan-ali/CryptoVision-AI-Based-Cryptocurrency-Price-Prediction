from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User
from .forms import SignupForm, LoginForm

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already exists.')
            return redirect(url_for('main.signup'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully. Please log in.')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form)

from flask import flash

# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and check_password_hash(user.password, form.password.data):
#             login_user(user)
#             flash('Login successful!')
#             return redirect(url_for('main.home'))
#         else:
#             flash('Invalid email or password.')  # This shows below the button
#     return render_template('login.html', form=form)

# Regular user login
# routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, login_required
from werkzeug.security import check_password_hash
from .models import User
from .forms import LoginForm

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not user.is_admin and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash("Invalid user credentials")

    return render_template('login.html', form=form, show_signup=True, page_title="Login to CryptoPredict")

# -------------------------------
# Admin Login
# -------------------------------
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.is_admin and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash("Invalid admin credentials")

    return render_template('login.html', form=form, show_signup=False, page_title="Admin Login")


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

# sentiment page
import requests
from datetime import date
from flask import request, render_template
from flask_login import login_required
from textblob import TextBlob
from . import db
from .models import TweetSentiment, Coin

RAW_TOKEN = "AAAAAAAAAAAAAAAAAAAAAKFc1wEAAAAAlUmcbmqMw3xB1ebS1GUI2PPdMng=92K16QDYhsqnQBAgRAP0i98x9A87lEnGXbJ3AQoaBu15xEkeJh"

@main.route('/sentiment', methods=['GET', 'POST'])
@login_required
def sentiment():
    sentiment_results = []
    today = date.today()
    error_msg = None

    # 🔄 Get coin list from DB
    coin_objs = Coin.query.all()
    coin_names = [c.name for c in coin_objs]
    coin_map = {c.name: c.coin_id for c in coin_objs}  # {'Bitcoin': 'BTC-USD', ...}

    if request.method == 'POST':
        coin = request.form.get('coin')

        if coin not in coin_map:
            error_msg = "Selected coin is not available in the database."
            return render_template('sentiment.html', currencies=coin_names, results=[], error=error_msg)

        # ✅ Check DB cache first
        cached_tweets = TweetSentiment.query.filter_by(coin=coin, date=today).all()

        if cached_tweets:
            for entry in cached_tweets:
                sentiment_results.append({
                    'text': entry.text,
                    'score': entry.score,
                    'type': entry.sentiment
                })
        else:
            # ✅ Live fetch from Twitter API
            query = f"{coin} lang:en -is:retweet"
            url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=20&tweet.fields=text"
            headers = {
                "Authorization": f"Bearer {RAW_TOKEN}"
            }

            response = requests.get(url, headers=headers)
            print("Twitter API raw response:", response.status_code, response.json())

            if response.status_code == 200 and "data" in response.json():
                tweets = response.json()["data"]
                for tweet in tweets:
                    text = tweet['text']
                    sentiment = TextBlob(text).sentiment.polarity
                    sentiment_type = (
                        "Positive" if sentiment > 0 else
                        "Negative" if sentiment < 0 else
                        "Neutral"
                    )

                    # Save to DB
                    db_entry = TweetSentiment(
                        coin=coin,
                        text=text,
                        score=sentiment,
                        sentiment=sentiment_type,
                        date=today
                    )
                    db.session.add(db_entry)
                    sentiment_results.append({
                        'text': text,
                        'score': sentiment,
                        'type': sentiment_type
                    })

                db.session.commit()
            else:
                error_msg = response.json().get("detail", "Unauthorized or Invalid Request")

    return render_template('sentiment.html',
                           currencies=coin_names,
                           results=sentiment_results,
                           error=error_msg)


## prediction page

from flask import render_template
from flask_login import login_required, current_user

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from flask import render_template, request
from flask_login import login_required
from sklearn.ensemble import RandomForestRegressor
from app.models import Coin



@main.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    selected_coin = None
    historical_data = []
    chart_labels = []
    chart_values = []
    predicted_labels = []
    predicted_values = []
    start_date = ''
    end_date = ''
    error_msg = None

    # 🔄 Load coins from DB as dictionary { 'Bitcoin': 'BTC-USD', ... }
    coin_objs = Coin.query.all()
    coin_dict = {coin.name: coin.coin_id for coin in coin_objs}

    if request.method == 'POST':
        selected_coin = request.form.get('coin')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        action = request.form.get('action')

        if selected_coin and selected_coin in coin_dict:
            ticker = coin_dict[selected_coin]
            try:
                if not start_date:
                    start_date = (datetime.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')
                if not end_date:
                    end_date = datetime.now().strftime('%Y-%m-%d')

                df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df.columns]
                df.reset_index(inplace=True)

                closes = []
                ordinals = []

                for _, row in df.iterrows():
                    date_value = pd.to_datetime(row['Date'])
                    close_price = round(row.get(f'Close_{ticker}', row.get('Close', 0)), 2)
                    historical_data.append({
                        'Date': date_value.strftime('%Y-%m-%d'),
                        'Open': round(row.get(f'Open_{ticker}', row.get('Open', 0)), 2),
                        'High': round(row.get(f'High_{ticker}', row.get('High', 0)), 2),
                        'Low': round(row.get(f'Low_{ticker}', row.get('Low', 0)), 2),
                        'Close': close_price,
                        'Volume': int(row.get(f'Volume_{ticker}', row.get('Volume', 0)))
                    })
                    chart_labels.append(date_value.strftime('%Y-%m-%d'))
                    chart_values.append(close_price)
                    ordinals.append(date_value.toordinal())
                    closes.append(close_price)

                if action == "predict" and len(ordinals) > 10:
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    X = np.array(ordinals).reshape(-1, 1)
                    y = np.array(closes)
                    model.fit(X, y)

                    last_date = max(ordinals)
                    for i in range(1, 2):  # You can change this to predict more days
                        future_date = datetime.fromordinal(last_date + i)
                        pred_price = model.predict([[last_date + i]])[0]
                        predicted_labels.append(future_date.strftime('%Y-%m-%d'))
                        predicted_values.append(round(pred_price, 2))

            except Exception as e:
                print("Error fetching data from Yahoo Finance:", e)
                error_msg = "Could not retrieve data. Please try again later."

    return render_template('prediction.html',
                           top_coins=coin_dict.keys(),  # dropdown list from DB
                           selected_coin=selected_coin,
                           historical_data=historical_data,
                           chart_labels=chart_labels,
                           chart_values=chart_values,
                           predicted_labels=predicted_labels,
                           predicted_values=predicted_values,
                           start_date=start_date,
                           end_date=end_date,
                           error=error_msg,
                           zip=zip)



from flask import render_template
from flask_login import login_required, current_user
from .models import User

from app.models import User, Coin

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    user_count = User.query.filter_by(is_admin=False).count()
    coin_count = Coin.query.count()

    return render_template('admin_dashboard.html',
                           user_count=user_count,
                           coin_count=coin_count)


@main.route('/admin/users')
@login_required
def view_users():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin_view_users.html', users=users)


@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    user = User.query.get_or_404(user_id)

    if user.is_admin:
        flash("❌ Cannot delete an admin account.")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"✅ User '{user.username}' deleted.")

    return redirect(url_for('main.view_users'))


from .models import Coin
@main.route('/admin/update_coins', methods=['GET', 'POST'])
@login_required
def update_coins():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    from app.models import Coin  # ✅ Make sure Coin is imported

    if request.method == 'POST':
        coin_name = request.form.get('coin_name').strip()
        coin_id = request.form.get('coin_id').strip()

        if coin_name and coin_id:
            name_exists = Coin.query.filter_by(name=coin_name).first()
            id_exists = Coin.query.filter_by(coin_id=coin_id).first()

            if name_exists or id_exists:
                flash("⚠️ Coin name or ID already exists.")
            else:
                db.session.add(Coin(name=coin_name, coin_id=coin_id))
                db.session.commit()
                flash(f"✅ Coin '{coin_name}' with ID '{coin_id}' added successfully.")

        return redirect(url_for('main.update_coins'))

    coins = Coin.query.order_by(Coin.name).all()
    return render_template('admin_update_coins.html', coins=coins)


from .models import Coin

@main.route('/admin/delete_coin/<int:coin_id>', methods=['POST'])
@login_required
def delete_coin(coin_id):
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    coin = Coin.query.get_or_404(coin_id)
    db.session.delete(coin)
    db.session.commit()
    flash(f"❌ '{coin.name}' removed.")
    return redirect(url_for('main.update_coins'))


from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

@main.route('/admin/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if not current_user.is_admin:
        flash("Access denied.")
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_pwd):
            flash("❌ Current password is incorrect.")
        elif new_pwd != confirm_pwd:
            flash("❌ New passwords do not match.")
        elif len(new_pwd) < 6:
            flash("⚠️ New password must be at least 6 characters.")
        else:
            current_user.password = generate_password_hash(new_pwd)
            db.session.commit()
            flash("✅ Password updated successfully.")
            return redirect(url_for('main.admin_dashboard'))

    return render_template('admin_edit_profile.html')


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if current_user.is_admin:
        flash("Admins do not use this page.")
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        current_pwd = request.form.get('current_password')
        new_pwd = request.form.get('new_password')
        confirm_pwd = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_pwd):
            flash("❌ Current password is incorrect.")
        elif new_pwd != confirm_pwd:
            flash("❌ New passwords do not match.")
        elif len(new_pwd) < 6:
            flash("⚠️ New password must be at least 6 characters.")
        else:
            current_user.password = generate_password_hash(new_pwd)
            db.session.commit()
            flash("✅ Password updated successfully.")

    return render_template('user_profile.html')

