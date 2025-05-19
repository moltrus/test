import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

boston_df = pd.read_csv(r'C:\Users\Students\Desktop\mohazzeba\Datasets\BostonHousing.csv')
auto_mpg_df = pd.read_csv(r'C:\Users\Students\Desktop\mohazzeba\Datasets\auto-mpg.csv')

boston_df = boston_df.dropna()
auto_mpg_df = auto_mpg_df.dropna()

X_boston = boston_df[['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO',
                      'B', 'LSTAT']]
y_boston = boston_df['MEDV']

X_train_boston, X_test_boston, y_train_boston, y_test_boston = train_test_split(X_boston,
                                                                                y_boston, test_size=0.2, random_state=42)

lin_reg_boston = LinearRegression()
lin_reg_boston.fit(X_train_boston, y_train_boston)

y_pred_boston = lin_reg_boston.predict(X_test_boston)

mse_boston = mean_squared_error(y_test_boston, y_pred_boston)
print(f"Linear Regression MSE on Boston Housing Dataset: {mse_boston}")

plt.figure(figsize=(8, 6))
plt.scatter(y_test_boston, y_pred_boston)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Linear Regression: Actual vs Predicted (Boston Housing)')
plt.show()

X_auto_mpg = auto_mpg_df[['Cylinders', 'Displacement', 'Horsepower', 'Weight', 'Acceleration', 'Model Year']]
y_auto_mpg = auto_mpg_df['MPG']

X_train_auto_mpg, X_test_auto_mpg, y_train_auto_mpg, y_test_auto_mpg = train_test_split(X_auto_mpg,
                                                                                        y_auto_mpg, test_size=0.2, random_state=42)

poly = PolynomialFeatures(degree=2)
X_train_poly = poly.fit_transform(X_train_auto_mpg)
X_test_poly = poly.transform(X_test_auto_mpg)

poly_reg = LinearRegression()
poly_reg.fit(X_train_poly, y_train_auto_mpg)

y_pred_auto_mpg = poly_reg.predict(X_test_poly)

mse_auto_mpg = mean_squared_error(y_test_auto_mpg, y_pred_auto_mpg)
print(f"Polynomial Regression MSE on Auto MPG Dataset: {mse_auto_mpg}")

plt.figure(figsize=(8, 6))
plt.scatter(y_test_auto_mpg, y_pred_auto_mpg)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Polynomial Regression: Actual vs Predicted (Auto MPG)')
plt.show()
