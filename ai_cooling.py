# -*- coding: utf-8 -*-
"""AI_Cooling.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CdsC3CYeDsINRqF1Btu8JwpzQs2bNUoD
"""

# Commented out IPython magic to ensure Python compatibility.
!pip install matplotlib seaborn pandas numpy

# %matplotlib inline

import pandas as pd
import numpy as np

np.random.seed(42)

num_samples = 1000

time_of_day = pd.date_range("2024-01-01", periods=num_samples)
outdoor_temp = np.random.normal(18, 5, num_samples).clip(5, 35)
humidity = np.random.uniform(30, 80, num_samples)
occupancy = np.random.choice([0, 1], num_samples, p=[0.4, 0.6])
user_pref_temp = np.random.normal(21.5, 2, num_samples).clip(18, 25)
indoor_temp_before = np.random.normal(22, 3, num_samples).clip(15, 30)

energy_before = np.where(
    occupancy == 1,
    2.5 + np.random.normal(1, 0.5, num_samples),
    1.2 + np.random.normal(0.4, 0.2, num_samples)
)

energy_after = energy_before - np.random.uniform(0.2, 1.0, num_samples)

energy_after = np.maximum(energy_after, 0.5)

df = pd.DataFrame({
    "Time_of_Day": time_of_day,
    "Outdoor_Temp_C": outdoor_temp,
    "Occupancy": occupancy,
    "User_Pref_Temp_C": user_pref_temp,
    "Indoor_Temp_Before_C": indoor_temp_before,
    "Humidity_Percentage": humidity,
    "Energy_Consumption_Before_kWh": energy_before,
    "Energy_Consumption_After_kWh": energy_after
})


csv_path = "/ai_cooling_data.csv"
df.to_csv(csv_path, index=False)

csv_path

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_style("whitegrid")

file_path = "ai_cooling_data.csv"
try:
    df = pd.read_csv(file_path, parse_dates=['Time_of_Day'], dayfirst=True)
    print("✅ Data Loaded Successfully!")
except FileNotFoundError:
    print(f"❌ Error: File '{file_path}' not found.")
    exit()
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit()

display(df.head())

if df["Occupancy"].dtype == "object":
    df["Occupancy"] = df["Occupancy"].map({"Yes": 1, "No": 0})

plt.figure(figsize=(12, 6))
sns.histplot(df['Energy_Consumption_Before_kWh'], bins=30, kde=True, label='Before AI', color='blue', alpha=0.6)
sns.histplot(df['Energy_Consumption_After_kWh'], bins=30, kde=True, label='After AI', color='red', alpha=0.6)
plt.legend()
plt.xlabel("Energy Consumption (kWh)")
plt.ylabel("Frequency")
plt.title("🔋 Energy Consumption: Before vs After AI Optimization", fontsize=14)
plt.show()

numeric_df = df.select_dtypes(include=['number'])
plt.figure(figsize=(10, 6))
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("📈 Feature Correlation Heatmap", fontsize=14)

sns.set_style("whitegrid")
plt.rcParams.update({"font.size": 12})

plt.figure(figsize=(12, 8))
df.hist(figsize=(12, 8), bins=30, color="#1f77b4", edgecolor="black", alpha=0.7)
plt.suptitle("📊 Feature Distributions", fontsize=16, fontweight="bold")
plt.show()

df["Time_of_Day"] = pd.to_datetime(df["Time_of_Day"], errors="coerce")

df.fillna(df.select_dtypes(include=['number']).mean(), inplace=True)

for col in df.select_dtypes(include=['object']).columns:
    df[col].fillna(df[col].mode()[0], inplace=True)

df["Time_of_Day"].fillna(method="ffill", inplace=True)

#!pip install gradio

import gradio as gr

def plot_relationship(feature_x, feature_y):
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x=feature_x, y=feature_y, hue="Occupancy", alpha=0.7)
    plt.title(f"Relationship: {feature_x} vs {feature_y}")
    plt.grid(True)
    plt.tight_layout()
    return plt
feature_list = df.select_dtypes(include=["number"]).columns.tolist()
gr.Interface(
    fn=plot_relationship,
    inputs=[gr.Dropdown(feature_list, label="Feature X"), gr.Dropdown(feature_list, label="Feature Y")],
    outputs=gr.Plot(),
    title="📊 Interactive Feature Relationship Explorer",
).launch(debug=True)

from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
df['Occupied'] = encoder.fit_transform(df['Occupancy'])

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

df["Time_of_Day"] = pd.to_datetime(df["Time_of_Day"], errors="coerce")
df["Time_of_Day"] = df["Time_of_Day"].dt.hour * 3600 + df["Time_of_Day"].dt.minute * 60 + df["Time_of_Day"].dt.second

num_cols = ["Outdoor_Temp_C", "Time_of_Day", "User_Pref_Temp_C"]

df[num_cols] = scaler.fit_transform(df[num_cols])

display(df.head())

df['Optimal_Indoor_Temperature'] = np.where(
    df['Occupancy'] == 1,
    df['User_Pref_Temp_C'] - (df['Outdoor_Temp_C'] - 25) * 0.1,
    df['User_Pref_Temp_C'] + 2
)

df['Optimal_Indoor_Temperature'] = df['Optimal_Indoor_Temperature'].clip(18, 26)

df.head()

print(df.head())
print(df.info())

from sklearn.model_selection import train_test_split

X = df.drop(columns=['Optimal_Indoor_Temperature'])
y = df['Optimal_Indoor_Temperature']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set: {X_train.shape}, Testing set: {X_test.shape}")

from sklearn.linear_model import LinearRegression

model = LinearRegression()

model.fit(X_train, y_train)

print("Model Coefficients:", model.coef_)
print("Model Intercept:", model.intercept_)

from sklearn.metrics import mean_absolute_error, r2_score

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"R² Score: {r2:.2f}")

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)

import pandas as pd
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)

X_train_scaled.head()

def calculate_energy(indoor_temp, outdoor_temp, humidity, occupancy, k=0.5):
    base = k * abs(indoor_temp - outdoor_temp)
    humidity_penalty = 0.05 * (humidity - 50)
    occupancy_load = 0.3 * occupancy
    return np.clip(base + humidity_penalty + occupancy_load, 0.5, None)

df['Energy_Consumption_Before_kWh'] = calculate_energy(
    df['Indoor_Temp_Before_C'], df['Outdoor_Temp_C'], df['Humidity_Percentage'], df['Occupancy']
)

df['Energy_Consumption_After_kWh'] = calculate_energy(
    df['Optimal_Indoor_Temperature'],
    df['Outdoor_Temp_C'],
    df['Humidity_Percentage'],
    df['Occupancy']
)
df['Energy_Savings (%)'] = (
    (df['Energy_Consumption_Before_kWh'] - df['Energy_Consumption_After_kWh'])
    / df['Energy_Consumption_Before_kWh'] * 100
)

avg_savings = df['Energy_Savings (%)'].mean()
print(f"Average Energy Savings with AI: {avg_savings:.2f}%")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X = df[['Outdoor_Temp_C', 'Time_of_Day', 'Occupancy', 'User_Pref_Temp_C']]
y = df['Optimal_Indoor_Temperature']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

df['Hour'] = pd.to_datetime(df['Time_of_Day']).dt.hour
df['Hour_Sin'] = np.sin(2 * np.pi * df['Hour'] / 24)
df['Hour_Cos'] = np.cos(2 * np.pi * df['Hour'] / 24)
df.drop('Hour', axis=1, inplace=True)

#!pip install xgboost

from xgboost import XGBRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

numeric_features = ['Outdoor_Temp_C', 'User_Pref_Temp_C', 'Hour_Sin', 'Hour_Cos']
categorical_features = ['Occupancy']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', 'passthrough', categorical_features)
    ]
)

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', XGBRegressor(random_state=42))
])

X = df.drop(columns=['Optimal_Indoor_Temperature'])
y = df['Optimal_Indoor_Temperature']

train_size = int(len(X) * 0.8)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

df = df.apply(pd.to_numeric, errors='coerce')

from sklearn.impute import SimpleImputer

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ]), numeric_features),
        ('cat', 'passthrough', categorical_features)
    ]
)

#!pip uninstall -y scikit-learn
# !pip install scikit-learn==1.3.1

df.fillna(df.mean(), inplace=True)

pipeline.fit(X_train, y_train)

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
print(f"MAE with XGBoost: {mae:.2f}°C")

from sklearn.model_selection import GridSearchCV
param_grid = {
    'model__n_estimators': [100, 200],
    'model__learning_rate': [0.01, 0.1],
    'model__max_depth': [3, 5]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='neg_mean_absolute_error')
grid_search.fit(X_train, y_train)

print(f"Best Params: {grid_search.best_params_}")

print("Features used during training:", X_train.columns)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', XGBRegressor())
])

pipeline.fit(X_train, y_train)

df['Predicted Optimal Temperature (°C)'] = pipeline.predict(X)

def estimate_energy_use(actual_temp, optimal_temp):
    return abs(actual_temp - optimal_temp) * 0.5

df['Energy_Consumption_Before_kWh'] = df.apply(
    lambda row: estimate_energy_use(row['Indoor_Temp_Before_C'], row['User_Pref_Temp_C']), axis=1
)

df['Energy_Consumption_After_kWh'] = df.apply(
    lambda row: estimate_energy_use(row['Predicted Optimal Temperature (°C)'], row['User_Pref_Temp_C']), axis=1
)

df['Energy Savings (kWh)'] = df['Energy_Consumption_Before_kWh'] - df['Energy_Consumption_After_kWh']

df[['Indoor_Temp_Before_C', 'Predicted Optimal Temperature (°C)',
    'Energy_Consumption_Before_kWh', 'Energy_Consumption_After_kWh', 'Energy Savings (kWh)']].head()

sns.set_style("whitegrid")

plt.figure(figsize=(10, 5))
plt.plot(df.index, df['Energy_Consumption_Before_kWh'], label="Before AI", linestyle="dashed", color="red")
plt.plot(df.index, df['Energy_Consumption_After_kWh'], label="After AI", color="green")
plt.xlabel("Time")
plt.ylabel("Energy Consumption (kWh)")
plt.title("Energy Consumption Before vs After AI Adjustment")
plt.legend()
plt.show()

total_savings = df['Energy Savings (kWh)'].sum()
total_before = df['Energy_Consumption_Before_kWh'].sum()
savings_percentage = (total_savings / total_before) * 100

print(f"🔥 Total Energy Saved: {total_savings:.2f} kWh")
print(f"⚡ Savings Percentage: {savings_percentage:.2f}%")

!apt-get install git