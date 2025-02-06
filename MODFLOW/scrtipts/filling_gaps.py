import numpy as np
from sklearn import svm
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def run_test():
    data = pd.read_csv('Pumping_temp_pop.csv')
    data = data[data['Pumping']>0]
    #data = data[data['Pumping']<1000]
    data2 = data.dropna()
    X =data2.loc[:,['WS', 'POP', 'TEMP']]
    y = data2.loc[:, ['Pumping']]
    if True:
        for i in range(8):
            plt.subplot(2,4,i+1)
            ss = int(1000*np.random.rand())
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.20, random_state=ss) #ss = 135

            data = []
            ## tree
            from sklearn import tree
            clf = tree.DecisionTreeRegressor(min_samples_leaf = 5)
            #from sklearn.neural_network import MLPRegressor
            #clf = MLPRegressor(hidden_layer_sizes=(100,), activation='relu', solver='adam', alpha=0.001)
            clf = clf.fit(X_train, y_train)
            ypredict = clf.predict(X_test)
            roh = np.corrcoef(y_test.squeeze(), ypredict) [0,1]
            roh= int(roh * 1000) / 1000.0
            plt.scatter(y_test, ypredict)
            plt.plot([0,6000], [0,6000], 'r')
            plt.title(str(roh))
# plt.show()

if False:

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=135)  # ss = 135

    data = []
    ## tree
    from sklearn import tree

    clf = tree.DecisionTreeRegressor(min_samples_leaf=5)
    clf = clf.fit(X_train, y_train)
    ypredict = clf.predict(X_test)
    roh = np.corrcoef(y_test.squeeze(), ypredict)[0, 1]
    roh = int(roh * 1000) / 1000.0
    plt.scatter(y_test, ypredict)
    plt.plot([0, 400], [0, 400], 'r')
    plt.title(str(roh))

    ## multi layer nn
    from sklearn.neural_network import MLPRegressor
    mlp = MLPRegressor( hidden_layer_sizes=(20,), activation='relu', solver='adam', alpha=0.001)
    mlp.fit(X_train, y_train)
    ypredict = mlp.predict(X_test)
    roh = np.corrcoef(y_test.squeeze(), ypredict)[0, 1]
    roh = int(roh * 1000) / 1000.0
    plt.scatter(y_test, ypredict)
    plt.plot([0,400], [0,400], 'r')
    plt.show()
    plt.title(str(roh))

    ## support vector method
    clf = svm.SVR(degree =20)
    clf.fit(X_train, y_train)

    ypredict = clf.predict(X_test)
    plt.scatter(y_test, ypredict)
    roh = np.corrcoef(y_test.squeeze(), ypredict)[0, 1]
    roh = int(roh * 1000) / 1000.0
    plt.scatter(y_test, ypredict)
    plt.plot([0,400], [0,400], 'r')
    plt.show()
    plt.title(str(roh))


    ##
    from sklearn import linear_model
    reg = linear_model.Ridge(alpha=.5)
    reg.fit(X_train,  y_train)
    ypredict = reg.predict(X_test)
    roh = np.corrcoef(y_test.values, ypredict)[0, 1]
    roh = int(roh * 1000) / 1000.0
    plt.scatter(y_test, ypredict)
    plt.plot([0,400], [0,400], 'r')
    plt.show()
    plt.title(str(roh))

    ##
    from sklearn import linear_model
    reg = linear_model.RidgeCV(alphas=[0.1, 1.0, 10.0], cv=3)
    reg.fit(X_train,  y_train)
    ypredict = reg.predict(X_test)
    roh = np.corrcoef(y_test.values.squeeze(), ypredict)[0, 1]
    roh = int(roh * 1000) / 1000.0
    plt.scatter(y_test, ypredict)
    plt.plot([0,400], [0,400], 'r')
    plt.show()
    plt.title(str(roh))

    #
    from sklearn import linear_model
    clf = linear_model.SGDRegressor(max_iter=1000, tol=1e-3)
    clf.fit(X_train,  y_train)
    ypredict = clf.predict(X_test)
    plt.scatter(y_test, ypredict)
    plt.plot([0,200], [0,200], 'r')
    plt.show()

    from sklearn import linear_model
    clf = linear_model.BayesianRidge()
    clf.fit(X_train,  y_train)
    ypredict = clf.predict(X_test)
    plt.scatter(y_test, ypredict)
    plt.plot([0,200], [0,200], 'r')
    plt.show()

    from sklearn import tree
    clf = tree.DecisionTreeRegressor()
    clf = clf.fit(X, y)
    ypredict = clf.predict(X_test)
    plt.scatter(y_test, ypredict)
    plt.plot([0,200], [0,200], 'r')
    plt.show()

    pass


