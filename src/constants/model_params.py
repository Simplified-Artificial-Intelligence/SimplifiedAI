from numpy.core.numeric import False_


LinearRegression_Params=[
    {"name":"fit_intercept","type":"select","values":[True,False],"type":"select","dtype":"bbolean"},
    {"name":"positive","type":"select","values":[False,True],"type":"select","dtype":"bbolean"}
]

Ridge_Params=[{"name":"alpha", "type":"input", "values":1.0, "dtype":"float", "accept_none":False},
              {"name":"fit_intercept", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"normalize", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"copy_X", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"max_iter", "type":"input", "values":"", "dtype":"int", "accept_none":True},
              {"name":"tol", "type":"input", "values":0.001, "dtype":"float", "accept_none":False},
              {"name":"solver", "type":"select", "values":["auto", "svd", "cholesky", "lsqr", "sparse_cg", "sag", "saga", "lbfgs"], "dtype":"string", "accept_none":False},
              {"name":"postive", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"random_state", "type":"input", "values":"", "dtype": "int", "accept_none":True}]
              
Lasso_Params=[{"name":"alpha", "type":"input", "values":1.0, "dtype":"float", "accept_none":False},
              {"name":"fit_intercept", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"precompute", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
              {"name":"copy_X", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
              {"name":"max_iter", "type":"input", "values":1000, "dtype":"int", "accept_none":False},
              {"name":"tol", "type":"input", "values":0.0001, "dtype":"float", "accept_none":False},
              {"name":"warm_start", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
              {"name":"positive", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
              {"name":"random_state", "type":"input", "values":"", "dtype": "int", "accept_none":True},
              {"name":"selection", "type":"select", "values":["cyclic", "random", "auto"], "dtype":"string", "accept_none":False}]
              
ElasticNet_Params=[{"name":"alpha", "type":"input", "values":1.0, "dtype":"float", "accept_none":False},
                   {"name":"l1_ratio", "type":"input", "values":0.5, "dtype":"float", "accept_none":False},
                   {"name":"fit_intercept", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
                   {"name":"precompute", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
                   {"name":"max_iter", "type":"input", "values":1000, "dtype":"int", "accept_none":False},
                   {"name":"copy_X", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
                   {"name":"tol", "type":"input", "values":0.0001, "dtype":"float", "accept_none":False},
                   {"name":"warm_start", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
                   {"name":"positive", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
                   {"name":"random_state", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                   {"name":"selection", "type":"select", "values":["cyclic", "random"], "dtype":"string", "accept_none":False}]

DecisionTreeRegressor_Params=[{"name":"criterion", "type":"select", "values":["squared_error", "friedman_mse", "absolute_error", "poisson"], "dtype":"string", "accept_none":False},
                              {"name":"splitter", "type":"select", "values":["best", "random"], "dtype":"string", "accept_none":False},
                              {"name":"max_depth", "type":"input", "values":"", "dtype":"int", "accept_none":True},
                              {"name":"min_samples_split", "type":"input", "values":2, "dtype":"float", "accept_none":False},
                              {"name":"min_samples_leaf", "type":"input", "values":1, "dtype":"float", "accept_none":False},
                              {"name":"min_weight_fraction_leaf", "type":"input", "values":0.0, "dtype":"float", "accept_none":False},
                              {"name":"max_features", "type":"select", "values":["auto","sqrt","log2"]},
                              {"name":"random_state", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                              {"name":"max_leaf_nodes", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                              {"name":"min_impurity_decrease", "type":"input", "values":0.0, "dtype": "float", "accept_none":False},
                              {"name":"ccp_alpha", "type":"input", "values":0.0, "dtype": "float", "accept_none":False}]

RandomForestRegressor_Params=[{"name":"n_estimators", "type":"input", "values":100, "dtype":"int", "accept_none":False},
                              {"name":"criterion", "type":"select", "values":["squared_error", "absolute_error", "poisson"], "dtype":"string", "accept_none":False},
                              {"name":"max_depth", "type":"input", "values":"", "dtype":"int", "accept_none":True},
                              {"name":"min_samples_split", "type":"input", "values":2, "dtype":"float", "accept_none":False},
                              {"name":"min_samples_leaf", "type":"input", "values":1, "dtype":"float", "accept_none":False},
                              {"name":"min_weight_fraction_leaf", "type":"input", "values":0.0, "dtype":"float", "accept_none":False},
                              {"name":"max_features", "type":"select", "values":["auto","sqrt","log2"]},
                              {"name":"max_leaf_nodes", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                              {"name":"min_impurity_decrease", "type":"input", "values":0.0, "dtype": "float", "accept_none":False},
                              {"name":"bootstrap", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
                              {"name":"oob_score", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
                              {"name":"n_jobs", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                              {"name":"random_state", "type":"input", "values":"", "dtype": "int", "accept_none":True},
                              {"name":"verbose", "type":"input", "values":0, "dtype":"int", "accept_none":False},
                              {"name":"warm_start", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
                              {"name":"ccp_alpha", "type":"input", "values":0.0, "dtype": "float", "accept_none":False},
                              {"name":"max_samples", "type":"input", "values":"", "dtype": "float", "accept_none":True}]
                              

                              
SVR_params=[{"name":"kernel", "type":"select", "values":["rbf", "linear", "poly", "sigmoid", "precomputed"], "dtype":"string", "accept_none":False},
            {"name":"degree", "type":"input", "values":3, "dtype":"int", "accept_none":False},
            {"name":"gamma", "type":"input", "values":["scale", "auto"], "dtype":"string", "accept_none":False},
            {"name":"coef0", "type":"input", "values":0.0, "dtype":"float", "accept_none":False},
            {"name":"tol", "type":"input", "values":0.001, "dtype":"float", "accept_none":False},
            {"name":"C", "type":"input", "values":1.0, "dtype":"float", "accept_none":False},
            {"name":"epsilon", "type":"input", "values":0.1, "dtype":"float", "accept_none":False},
            {"name":"shrinking", "type":"select", "values":["True", "False"], "dtype":"boolean", "accept_none":False},
            {"name":"cache_size", "type":"input", "values":200, "dtype":"float", "accept_none":False},
            {"name":"verbose", "type":"select", "values":["False", "True"], "dtype":"boolean", "accept_none":False},
            {"name":"max_iter", "type":"input", "values":-1, "dtype":"int", "accept_none":False}]
            
            
AdabootRegressor_Params = [{"name":"base_estimator", "type":"input", "values":"", "dtype":"object", "accept_none":True},
                           {"name":"n_estimators", "type":"input", "values":50, "dtype":"int", "accept_none":False},
                           {"name":"learning_rate", "type":"input", "values":1.0, "dtype":"float", "accept_none":False},
                           {"name":"loss", "type":"select", "values":['linear', 'square', 'exponential'], "dtype":"string", "accept_none":False},
                            {"name":"random_state", "type":"input", "values":"", "dtype":"int", "accept_none":True}]


GradientBoostRegressor_Params = [
                            {"name":"loss","type":"select","values":['squared_error','absolute_error', 'huber', 'quantile'], "dtype":"string", "accept_none":False},
                            {"name":"learning_rate","type":"input","values":"0.1", "dtype":"float", "accept_none":False},
                            {"name":"n_estimators","type":"input","values":"100", "dtype":"int", "accept_none":False},
                            {"name":"subsample","type":"input","values":"1.0", "dtype":"float", "accept_none":False},
                            {"name":"criterion","type":"select","values":['friedman_mse','squared_error', 'mae', 'mse'], "dtype":"string", "accept_none":False},
                            {"name":"min_samples_split","type":"input","values":"2", "dtype":"float", "accept_none":False},
                            {"name":"min_samples_leaf","type":"input","values":"1", "dtype":"float", "accept_none":False},
                            {"name":"min_weight_fraction_leaf","type":"input","values":"0.0", "dtype":"float", "accept_none":False},
                            {"name":"max_depth","type":"input","values":"3", "dtype":"int", "accept_none":False},
                            {"name":"min_impurity_decrease","type":"input","values":"0.0", "dtype":"float", "accept_none":False},
                            {"name":"init","type":"select","values":['squared_error','absolute_error', 'huber', 'quantile'], "dtype":"string", "accept_none":True},
                            {"name":"random_state","input":"int","values":"", "dtype":"int", "accept_none":True},
                            {"name":"max_features","type":"select","values":['auto','sqrt', 'log2'], "dtype":"string", "accept_none":False},
                            {"name":"alpha","type":"input","values":"0.9", "dtype":"float", "accept_none":False},
                            {"name":"verbose","type":"input","values":"0", "dtype":"int", "accept_none":False},
                            {"name":"max_leaf_nodes","type":"input","values":"", "dtype":"int", "accept_none":True},
                            {"name":"warm_start","type":"select","values":[False,True], "dtype":"boolean", "accept_none":False},
                            {"name":"validation_fraction","type":"input","values":"0.1", "dtype":"float", "accept_none":False},
                            {"name":"n_iter_no_change","type":"input","values":"", "dtype":"int", "accept_none":True},
                            {"name":"tol","type":"input","values":"0.0001", "dtype":"float", "accept_none":False},
                            {"name":"ccp_alpha","type":"input","values":"0.0", "dtype":"float", "accept_none":False}]


Params_Mappings={
    "true":True,
    "false":False
}