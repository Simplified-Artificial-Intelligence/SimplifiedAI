from numpy.core.numeric import False_


LinearRegression_Params=[
    {"name":"fit_intercept","type":"select","values":[True,False],"type":"select","dtype":"bbolean"},
    {"name":"positive","type":"select","values":[False,True],"type":"select","dtype":"bbolean"}
]

DecisionTreeRegressor_Params=[
    {"name":"criterion","type":"select","values":["squared_error", "friedman_mse", "absolute_error", "poisson"],"dtype":"string","accept_none":False},
    {"name":"splitter","type":"select","values":["best","random"],"dtype":"string","accept_none":False},
    {"name":"max_depth","type":"input","values":"","dtype":"int","accept_none":True},
    {"name":"min_samples_split","type":"input","values":2,"dtype":"int","accept_none":False},
    {"name":"min_samples_leaf","type":"input","values":1,"dtype":"int","accept_none":False},
    {"name":"min_weight_fraction_leaf","type":"input","values":0.0,"dtype":"float","accept_none":False},
    {"name":"max_features","type":"input","values":"","dtype":"int","accept_none":True},
    {"name":"max_leaf_nodes","type":"input","values":"","dtype":"int","accept_none":True},
    {"name":"min_impurity_decrease","type":"input","values":"0.0","dtype":"float","accept_none":False},
    {"name":"ccp_alpha","type":"input","values":0.0,"dtype":"float","accept_none":False}
]


Params_Mappings={
    "true":True,
    "false":False
}