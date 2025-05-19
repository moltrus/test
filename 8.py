import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

data = pd.read_csv(r'C:\Users\Students\Desktop\mohazzeba\Datasets\BreastCancer.csv')

X = data.iloc[:, :-1]
y = data.iloc[:, -1]

X = X.fillna(X.mean())

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

decision_tree = DecisionTreeClassifier(random_state=42)
decision_tree.fit(X_train, y_train)

y_pred = decision_tree.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of the Decision Tree classifier: {accuracy:.4f}")

plt.figure(figsize=(12, 8))
plot_tree(decision_tree, filled=True,
          feature_names=X.columns, 
          class_names=np.unique(y).astype(str))
plt.title('Decision Tree Visualization')
plt.show()

new_sample = np.array([[15.6, 19.0, 98.0, 650.0, 0.2, 0.5, 0.3, 
                       0.1, 0.7, 0.6]])

new_sample_pred = decision_tree.predict(new_sample)
print(f"The predicted class for the new sample is: {new_sample_pred[0]}")
