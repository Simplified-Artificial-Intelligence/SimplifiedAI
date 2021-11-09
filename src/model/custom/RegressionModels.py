import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, RidgeCV, LassoCV, ElasticNet, ElasticNetCV, LassoLars
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVC
from sklearn.metrics import mean_squared_error, r2_score
import pickle

class RegressionModels:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def custom_train_test_split(self,test_size=None,train_size=None,random_state=None,shuffle=True,stratify=None):

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.x, self.y, train_size=train_size, test_size=test_size, random_state=random_state, shuffle=shuffle, stratify=stratify)

    def Linear_Regression(self,fit_intercept=True,normalize=False,copy_X=True,n_jobs=None,v_positive=False):
      
        model = LinearRegression(fit_intercept=fit_intercept, normalize=normalize, copy_X=copy_X, n_jobs=n_jobs) 
        #Training the model
        model.fit(self.X_train, self.y_train)        

        y_pred=model.predict(self.X_test)
        r2=model.score(self.X_test,self.y_test)
        #Evaluating Model
        print("Model Evaluation : ")
        print("coef_ : ", model.coef_)
        print("intercept_ : %.4f" %  model.intercept_)
        print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
        print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
        print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
        print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

        # Plot outputs
        # plt.scatter(self.X_test['pclass'], self.y_test, color="black")
        # plt.plot(self.X_test['pclass'], y_pred, color="blue", linewidth=3)
        # plt.xticks(())
        # plt.yticks(())
        # plt.show()

        #Saving model file
        RegressionModels.save_model(model,"Linear_Regression")

    def Ridge_Regression(self,cv=10, fit_intercept=True, normalize=False,  copy_X=True, max_iter=None, tol=0.001, solver='auto', v_positive=False, random_state=None):

      ridgecv = RidgeCV(alphas=np.random.uniform(0,10,50), cv = cv, normalize=normalize)
      ridgecv.fit(self.X_train,self.y_train)

      model =Ridge(alpha=ridgecv.alpha_,fit_intercept=fit_intercept, normalize=normalize,  copy_X=copy_X, max_iter=max_iter, tol=tol, solver=solver, random_state=random_state  ) 

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      print("coef_ : ", model.coef_)
      print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"Ridge_Regression")

    def Lasso_Regression(self,cv=50, fit_intercept=True, normalize=False, precompute=False, copy_X=True, max_iter=1000, tol=0.0001, warm_start=False, v_positive=False, random_state=None, selection='cyclic'):

      lassocv = LassoCV(alphas=None,cv= cv , max_iter=max_iter, normalize=normalize)
      lassocv.fit(self.X_train, self.y_train)

      model =Lasso(alpha=lassocv.alpha_, fit_intercept=fit_intercept, normalize=normalize, precompute=precompute, copy_X=copy_X, max_iter=max_iter, tol=tol, warm_start=warm_start, positive=v_positive, random_state=random_state, selection=selection )

      #Training the model
      model.fit(self.X_train, self.y_train)     

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      print("coef_ : ", model.coef_)
      print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"Lasso_Regression")

    def ElasticNet_Regression(self,cv=10,alpha=1.0,l1_ratio=0.5,fit_intercept=True,normalize=False):

      elastic = ElasticNetCV(alphas=None, cv = cv )
      elastic.fit(self.X_train, self.y_train)

      model =ElasticNet(alpha=elastic.alpha_ , l1_ratio=elastic.l1_ratio_ ,fit_intercept=fit_intercept,normalize=normalize)

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      print("coef_ : ", model.coef_)
      print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"ElasticNet_Regression")

    def DT_Regression(self,criterion='gini', splitter='best', max_depth=None, min_samples_split=2, min_samples_leaf=1, 
                      min_weight_fraction_leaf=0.0,                       max_features=None, random_state=None, 
                      max_leaf_nodes=None, min_impurity_decrease=0.0, class_weight=None, ccp_alpha=0.0):

      model =DecisionTreeClassifier(criterion=criterion, splitter=splitter, max_depth=max_depth, min_samples_split=min_samples_split, 
                                    min_samples_leaf=min_samples_leaf, min_weight_fraction_leaf=min_weight_fraction_leaf, max_features=max_features, 
                                    random_state=random_state, max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=min_impurity_decrease, 
                                    class_weight=class_weight, ccp_alpha=ccp_alpha)

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      # print("coef_ : ", model.coef_)
      # print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"DT_Regression")

    def RandomForest_Regression(self,n_estimators=100, criterion='gini', max_depth=None, 
                                  min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, 
                                  max_features='auto', max_leaf_nodes=None, min_impurity_decrease=0.0, 
                                  bootstrap=True, oob_score=False, n_jobs=None, random_state=None, 
                                  verbose=0, warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None):
      model =RandomForestClassifier(n_estimators=n_estimators, criterion=criterion, max_depth=max_depth, 
                                  min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf, min_weight_fraction_leaf=min_weight_fraction_leaf, 
                                  max_features=max_features, max_leaf_nodes=max_leaf_nodes, min_impurity_decrease=min_impurity_decrease, 
                                  bootstrap=bootstrap, oob_score=oob_score, n_jobs=n_jobs, random_state=random_state, verbose=verbose,
                                  warm_start=warm_start, class_weight=class_weight, ccp_alpha=ccp_alpha, max_samples=max_samples)

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      # print("coef_ : ", model.coef_)
      # print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"RandomForest_Regression")

    def KNN_Regression(self, n_neighbors=5, weights='uniform', algorithm='auto', leaf_size=30, p=2, metric='minkowski', 
                       metric_params=None, n_jobs=None):
      model =KNeighborsRegressor(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm, leaf_size=leaf_size, 
                                  p=p, metric=metric, metric_params=metric_params, n_jobs=n_jobs)

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      # print("coef_ : ", model.coef_)
      # print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"KNN_Regression")      

    def SVC_Regression(self, C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True, probability=False, tol=0.001, 
                       cache_size=200, class_weight=None, verbose=False, max_iter=- 1, decision_function_shape='ovr', 
                       break_ties=False, random_state=None):
      model =SVC(C=1.0, kernel=kernel, degree=degree, gamma=gamma, coef0=coef0, shrinking=shrinking, probability=probability, tol=tol, 
                 cache_size=cache_size, class_weight=class_weight, verbose=verbose, max_iter=max_iter, decision_function_shape=decision_function_shape,
                 break_ties=break_ties, random_state=random_state)

      #Training the model
      model.fit(self.X_train, self.y_train)

      y_pred=model.predict(self.X_test)
      r2=model.score(self.X_test,self.y_test)
      #Evaluating Model
      print("Model Evaluation : ")
      # print("coef_ : ", model.coef_)
      # print("intercept_ : %.4f" %  model.intercept_)
      print("Score :  %.4f" %  model.score(self.X_test,self.y_test))
      print("Adjusted R2 :  %.4f" %  RegressionModels.adj_r2(self.X_test,self.y_test,r2))
      print("Mean squared error: %.4f" % mean_squared_error(self.y_test, y_pred))
      print("Coefficient of determination: %.4f" % r2_score(self.y_test, y_pred))

      #Saving model file
      RegressionModels.save_model(model,"SVC_Regression") 

    @staticmethod
    def adj_r2(x,y,r2):      
      n = x.shape[0]
      p = x.shape[1]
      adjusted_r2 = 1-(1-r2)*(n-1)/(n-p-1)
      return adjusted_r2

    @staticmethod
    def save_model(model,filename):
        # with open(f'E:/iNeuron/Full Stack Data Science/Internship/Projectathon/artifacts/models'+ '/modelForPrediction.sav', 'wb') as f:
        with open(filename+'modelForPrediction.sav', 'wb') as f:
            pickle.dump(model, f)