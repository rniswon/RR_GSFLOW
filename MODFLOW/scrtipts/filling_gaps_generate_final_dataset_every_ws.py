import numpy as np
from sklearn import svm
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

data_original = pd.read_csv('Pumping_temp_pop.csv')#

data = data_original.copy()
data.PumpingRate[data.PumpingRate>270] = np.NAN # filter out large values, possibly wrong
Water_systems = data.WS.unique()
no_data_ws = []
for iws, ws in enumerate(Water_systems):
        curr_ws_data = data[data.WS == ws]
        xx = curr_ws_data.groupby(['Year', 'Month']).sum()
        xx.POP.plot()
        plt.close()
        loc_0_value = curr_ws_data['PumpingRate'] <= 0
        loc_estimate = np.logical_or(curr_ws_data.PumpingRate.isna().values , curr_ws_data.Year < 0)
        loc_nan = curr_ws_data.PumpingRate.isna()
        data2 = curr_ws_data[np.logical_not(loc_estimate)]
        if data2.shape[0] == 0:
                no_data_ws.append(ws)
                continue
        cols = ['TEMP', 'Pop_service', 'WS']
        X =data2.loc[:,cols]
        y = data2.loc[:, ['PumpingRate']]

        X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.0, random_state=135) #ss = 135
        ## tree
        if 1:
                from sklearn import tree
                clf = tree.DecisionTreeRegressor(min_samples_leaf = 5, min_weight_fraction_leaf= 0.0, random_state=135 )

                clf = clf.fit(X_train, y_train)


        if 0:
                from sklearn.neural_network import MLPRegressor
                #‘identity’
                #'relu'
                clf = MLPRegressor( hidden_layer_sizes=(6,), activation='relu', solver='adam', alpha=0.001)
                clf.fit(X_train, y_train)

        # find data to fill
        X_to_estimate =curr_ws_data.loc[loc_estimate,cols]
        if X_to_estimate.shape[0] == 0:
                curr_ws_data.loc[:,'Wieght'] = curr_ws_data.shape[0]
                all_data.append(curr_ws_data)
                continue

        ypredict = clf.predict(X_to_estimate)
        #curr_ws_data.loc[loc_estimate, 'PumpingRate'] = ypredict
        try:
                loc_es = np.where(loc_estimate.values)[0]
                curr_ws_data.loc[loc_estimate, 'PumpingRate'] = ypredict
                #curr_ws_data.loc[curr_ws_data.index[loc_es], 'PumpingRate'] = ypredict
        except:
                pass
        nvalues_estimated = float(np.sum(loc_estimate))
        data_setsize = float(curr_ws_data.shape[0])
        Wieght = 100.0 * (data_setsize - nvalues_estimated)/data_setsize
        curr_ws_data.loc[:, 'Wieght'] = data_setsize

        if iws == 0:
                all_data = [curr_ws_data]
        else:
                all_data.append(curr_ws_data)

data = pd.concat(all_data)
if False:
        data.to_csv('Pumping_temp_pop_filled_AF_per_month.csv')

## Evaluate
Filled = data.groupby(['Year']).sum()
data3 = data_original.copy()
data3.loc[data3['PumpingRate'].isna().values, ['PumpingRate']] = 0
Nofill = data3.groupby(['Year']).sum()

plt.plot(Nofill.index, Nofill.PumpingRate.values, label = 'Before Filling')
plt.plot(Filled.index, Filled.PumpingRate.values, Label = 'After Filling')
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

# count Nan per year
data4 = data.copy()
data4[loc_0_value]
data4['FlagNan'] = 0
data4.loc[loc, ['FlagNan']] = 1
data4 = data4[loc_0_value]
NanCount = data4.groupby(['Year']).mean()

pass