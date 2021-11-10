TWO_D_GRAPH_TYPES = ["Bar Graph", "Histogram", "Scatter Plot", "Pie Chart", "Line Chart"]
encoding_list = ["Label/Ordinal Encoder", "One Hot Encoder", "Hash Encoder", "Target Encoder"]
scaling_list = ["Standard Scaler", "Min Max Scaler", "Max Abs Scaler", "Robust Scaler"]
FEATURE_SELECTION_METHODS_CLASSIFICATION = ["Find Constant Features", "Mutual Info Classification",
                                            "Extra Trees Classifier", "Correlation", "Forward Selection",
                                            "Backward Elimination"]
dimenstion_reduction_list = ["PCA"]

NUMERIC_MISSING_HANDLER = ['Mean', 'Median', 'Arbitrary Value', 'Interpolate']
OBJECT_MISSING_HANDLER = ['Mode', 'New Category', 'Select Exist']

SUPPORTED_DATA_TYPES = ['object', 'int64', 'float64', 'bool', 'datetime64', 'category', 'timedelta']
ENCODING_TYPES = ['One Hot Encoder', 'Label/Ordinal Encoder', 'Hash Encoder', 'Binary Encoder', 'Base N Encoder',
                  'Target Encoder']
SUPPORTED_SCALING_TYPES = ['MinMax Scaler', 'Standard Scaler', 'Max Abs Scaler', 'Robust Scaler',
                           'Power Transformer Scaler']
PROJECT_TYPES = [
    {"id": 1, "name": "Regression"},
    {"id": 2, "name": "Classification"},
    {"id": 3, "name": "Clustering"}
]
