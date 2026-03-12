import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

# Step 1: Load Data
ticker = 'BNB-USD'
start_date = '2023-01-01'
end_date = '2024-01-01'
df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
df.reset_index(inplace=True)

# Step 2: Feature Engineering
df['OrdinalDate'] = df['Date'].map(datetime.toordinal)
df['LogClose'] = np.log1p(df['Close'])  # Stabilize variance
df['MA_3'] = df['Close'].rolling(window=3).mean()
df['MA_7'] = df['Close'].rolling(window=7).mean()
df['MA_14'] = df['Close'].rolling(window=14).mean()
df['STD_7'] = df['Close'].rolling(window=7).std()
df['Return'] = df['Close'].pct_change()
df['Lag_1'] = df['Close'].shift(1)
df['Lag_2'] = df['Close'].shift(2)
df['Lag_3'] = df['Close'].shift(3)

df.dropna(inplace=True)

# Step 3: Define features and target
features = ['OrdinalDate', 'MA_3', 'MA_7', 'MA_14', 'STD_7', 'Return', 'Lag_1', 'Lag_2', 'Lag_3']
X = df[features]
y = df['LogClose']

# Step 4: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Step 5: Train Model
model = XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Step 6: Evaluate Model
y_pred_log = model.predict(X_test)
y_pred = np.expm1(y_pred_log)
y_test_actual = np.expm1(y_test)

print(f"\n📊 Evaluation for {ticker}:")
print(f"Mean Squared Error (MSE): {mean_squared_error(y_test_actual, y_pred):.2f}")
print(f"Mean Absolute Error (MAE): {mean_absolute_error(y_test_actual, y_pred):.2f}")
print(f"R² Score: {r2_score(y_test_actual, y_pred):.4f}")
