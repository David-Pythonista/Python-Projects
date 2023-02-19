import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

#settings = [(0)None, (1)window_size, (2)Coefficient of determination lin, (3)slpoe_lin, (4)None, (5)Coefficient of determination pol, (6)slope pol]

def linear_regression(x_axis,y_axis,settings):

        x_values = np.array(x_axis[:settings[1]]).reshape(-1, 1)
        y_values = np.array(y_axis[(-1)*settings[1]:])

        model = LinearRegression()
        model.fit(x_values, y_values)
        model = LinearRegression().fit(x_values, y_values)
        coef_of_det = model.score(x_values, y_values)

        if coef_of_det > settings[3] and model.coef_> settings[4]:
            return "buy"

        elif coef_of_det > settings[3] and model.coef_< settings[4]:
            return "sell"
        else:
            return


def polynomial_regression(x_axis,y_axis,settings):

        x_values = np.array(x_axis[:settings[1]]).reshape(-1, 1)
        y_values = np.array(y_axis[(-1)*settings[1]:])

        transformer = PolynomialFeatures(degree=2, include_bias=False)
        transformer.fit(x_values)
        x_ = transformer.transform(x_values)
        x_ = PolynomialFeatures(degree=2, include_bias=False).fit_transform(x_values)
        model = LinearRegression().fit(x_, y_values)

        coef_of_det = model.score(x_, y_values)

        if coef_of_det > settings[6] and model.coef_.all() > settings[7]:
            return "buy"

        elif coef_of_det > settings[6] and model.coef_.all() < settings[7]:
            return "sell"
        else:
            return

def fuzzy():
    pass

if __name__ == "__main__":
    pass