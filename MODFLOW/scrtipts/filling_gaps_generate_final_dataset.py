import numpy as np
from sklearn import svm
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def run():
        data_original = pd.read_csv('Pumping_temp_pop.csv')#
        data = data_original.copy()
        loc_0_value = data['Pumping'] <= 0
        loc_estimate = np.logical_or(data.Pumping.isna().values , data.Year < 0)
        loc_nan = data.Pumping.isna()
        #data2 = data[data['PumpingRate']>-100000000000]
        #data = data[data['PumpingRate']<1000]

        data2 = data[np.logical_not(loc_estimate)]
        #X =data2.loc[:,['Month', 'Pop_service', 'TEMP']]
        #'Month','Pop_service','TEMP',
        cols = ['TEMP', 'POP', 'WS']
        X =data2.loc[:,cols]
        y = data2.loc[:, ['Pumping']]

        X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.0, random_state=135) #ss = 135


        ## tree
        if 1:
                from sklearn import tree
                clf = tree.DecisionTreeRegressor(min_samples_leaf = 5, min_weight_fraction_leaf= 0.0, random_state=135 )
                clf = clf.fit(X_train, y_train)
# if 0:
#         from sklearn.neural_network import MLPRegressor
#         #‘identity’
#         #'relu'
#         clf = MLPRegressor( hidden_layer_sizes=(6,), activation='relu', solver='adam', alpha=0.001)
#         clf.fit(X_train, y_train)
# find data to fill

        X_to_estimate =data.loc[loc_estimate,cols]
        ypredict = clf.predict(X_to_estimate)
        data.loc[loc_estimate, ['Pumping']] = ypredict
        data['IsData'] = 1
        data.loc[loc_estimate, ['IsData']] = 0
        data.to_csv('Pumping_temp_pop_filled_AF_per_month.csv')

        ## Evaluate
        Filled = data.groupby(['Year']).sum()
        data3 = data.copy()
        data3.loc[loc_nan, ['Pumping']] = 0
        Nofill = data3.groupby(['Year']).sum()
        plt.figure()
        plt.plot(Nofill.index, Nofill.Pumping, label = 'Before Filling')
        plt.plot(Filled.index, Filled.Pumping, Label = 'After Filling')
        plt.legend()
        plt.show()

### Evalue the performance
        plt.figure()
        for i, feature in enumerate(cols):
                plt.subplot(1, 3, i + 1)
                data_evaluate = data2.copy()
                length  = data_evaluate.shape[0]
                min_val = data_evaluate[feature].min()
                max_val = data_evaluate[feature].max()
                values = np.linspace(min_val, max_val, length)
                for ff in cols:
                        data_evaluate[ff] = data_evaluate[ff].mean()
                data_evaluate[feature] = values
                X_to_estimate2 =data_evaluate.loc[:,cols]
                ypredict2 = clf.predict(X_to_estimate2)
                plt.plot(values, ypredict2)
                plt.title(feature)
        plt.show()
        if 0:
                # count Nan per year
                data4 = data.copy()
                data4[loc_0_value]
                data4['FlagNan'] = 1
                data4.loc[loc_nan, ['FlagNan']] = 0
                data4 = data4[loc_0_value]
                NanCount = data4.groupby(['Year']).mean()

        pass