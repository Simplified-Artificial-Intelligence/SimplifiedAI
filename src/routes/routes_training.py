from flask import Blueprint, redirect, url_for, render_template, request, session, send_file
from src.constants.model_params import DecisionTreeRegressor_Params, LinearRegression_Params, Ridge_Params, \
    Lasso_Params, ElasticNet_Params, RandomForestRegressor_Params, SVR_params, AdabootRegressor_Params, \
    GradientBoostRegressor_Params, Params_Mappings
from src.constants.model_params import KmeansClustering_Params, DbscanClustering_Params, AgglomerativeClustering_Params
from src.constants.model_params import LogisticRegression_Params, SVC_Params, KNeighborsClassifier_Params, \
    DecisionTreeClassifier_Params, RandomForestClassifier_Params, GradientBoostingClassifier_Params, \
    AdaBoostClassifier_Params
from src.model.custom.classification_models import ClassificationModels
from src.model.custom.regression_models import RegressionModels
from src.model.custom.clustering_models import ClusteringModels
from src.constants.constants import REGRESSION_MODELS, CLASSIFICATION_MODELS, CLUSTERING_MODELS
import os
from src.utils.common.common_helper import get_param_value, load_project_model, read_config, save_project_model
from src.utils.common.data_helper import load_data, update_data, get_filename, csv_to_json, to_tsv, csv_to_excel
from src.model.auto.Auto_classification import ModelTrain_Classification
from src.model.auto.Auto_regression import ModelTrain_Regression
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
from loguru import logger
from from_root import from_root
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_squared_log_error
from src.utils.common.project_report_helper import ProjectReports

app_training = Blueprint('training', __name__)

config_args = read_config("./config.yaml")

log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")


@app_training.route('/model_training/<action>', methods=['GET'])
def model_training(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                """Check If Project type is Regression or Classificaion and target Columns is not Selected"""
                if session['project_type'] != 3 and session['target_column'] is None:
                    return redirect('/target-column')

                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'auto_training':
                    logger.info('Redirect To Auto Training Page')
                    ProjectReports.insert_record_ml('Redirect To Auto Training Page')
                    return render_template('model_training/auto_training.html', project_type=session['project_type'],
                                           target_column=session['target_column'])
                elif action == 'custom_training':
                    logger.info('Redirect To Custom Training Page')
                    ProjectReports.insert_record_ml('Redirect To Custom Training Page')
                    try:
                        if session['project_type'] == 2:
                            return render_template('model_training/classification.html', action=action,
                                                   models=CLASSIFICATION_MODELS)
                        elif session['project_type'] == 1:
                            return render_template('model_training/regression.html', action=action,
                                                   models=REGRESSION_MODELS)
                        elif session['project_type'] == 3:
                            return render_template('model_training/clustering.html', action=action,
                                                   models=CLUSTERING_MODELS)
                        else:
                            return render_template('model_training/custom_training.html')
                    except Exception as e:
                        print(e)
                        return render_template('model_training/custom_training.html')
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))
    except Exception as e:
        logger.error('Error in Model Training')
        ProjectReports.insert_record_ml('Error in Model Training', '', '', 0, str(e))


@app_training.route('/model_training/<action>', methods=['POST'])
def model_training_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            model = None
            range = None
            random_state = None
            if df is not None:
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'custom_training':
                    try:
                        model = request.form['model']
                        range = int(request.form['range'])
                        random_state = int(request.form['random_state'])

                        logger.info('Submitted Custom Training Page')
                        ProjectReports.insert_record_ml('Submitted Custom Training Page',
                                                        f"Model:{model}; Range:{range}; Random_State: {random_state}")

                        target = session['target_column']
                        X = df.drop(target, axis=1)
                        y = df[target]
                        train_model_fun = None

                        X_train, X_test, y_train, y_test = FeatureEngineering.train_test_Split(cleanedData=X,
                                                                                               label=y,
                                                                                               train_size=range / 100,
                                                                                               random_state=random_state)
                        model_params = {}
                        if model == "LinearRegression":
                            Model_Params = LinearRegression_Params
                            train_model_fun = RegressionModels.linear_regression_regressor
                        elif model == "Ridge":
                            Model_Params = Ridge_Params
                            train_model_fun = RegressionModels.ridge_regressor
                        elif model == "Lasso":
                            Model_Params = Lasso_Params
                            train_model_fun = RegressionModels.lasso_regressor
                        elif model == "ElasticNet":
                            Model_Params = ElasticNet_Params
                            train_model_fun = RegressionModels.elastic_net_regressor
                        elif model == "DecisionTreeRegressor":
                            Model_Params = DecisionTreeRegressor_Params
                            train_model_fun = RegressionModels.decision_tree_regressor
                        elif model == "RandomForestRegressor":
                            Model_Params = RandomForestRegressor_Params
                            train_model_fun = RegressionModels.random_forest_regressor
                        elif model == "SVR":
                            Model_Params = SVR_params
                            train_model_fun = RegressionModels.support_vector_regressor
                        elif model == "AdaBoostRegressor":
                            Model_Params = AdabootRegressor_Params
                            train_model_fun = RegressionModels.ada_boost_regressor
                        elif model == "GradientBoostingRegressor":
                            Model_Params = GradientBoostRegressor_Params
                            train_model_fun = RegressionModels.gradient_boosting_regressor
                        elif model == "LogisticRegression":
                            Model_Params = LogisticRegression_Params
                            train_model_fun = ClassificationModels.logistic_regression_classifier
                        elif model == "SVC":
                            Model_Params = SVC_Params
                            train_model_fun = ClassificationModels.support_vector_classifier
                        elif model == "KNeighborsClassifier":
                            Model_Params = KNeighborsClassifier_Params
                            train_model_fun = ClassificationModels.k_neighbors_classifier
                        elif model == "DecisionTreeClassifier":
                            Model_Params = DecisionTreeClassifier_Params
                            train_model_fun = ClassificationModels.decision_tree_classifier
                        elif model == "RandomForestClassifier":
                            Model_Params = RandomForestClassifier_Params
                            train_model_fun = ClassificationModels.random_forest_classifier
                        elif model == "AdaBoostClassifier":
                            Model_Params = AdaBoostClassifier_Params
                            train_model_fun = ClassificationModels.ada_boost_classifier
                        elif model == "GradientBoostingClassifier":
                            Model_Params = GradientBoostingClassifier_Params
                            train_model_fun = ClassificationModels.gradient_boosting_classifier
                        elif model == "KMeans":
                            Model_Params = KmeansClustering_Params
                            train_model_fun = ClusteringModels.kmeans_clustering
                        elif model == "DBSCAN":
                            Model_Params = DbscanClustering_Params
                            train_model_fun = ClusteringModels.dbscan_clustering
                        elif model == "AgglomerativeClustering":
                            Model_Params = AgglomerativeClustering_Params
                            train_model_fun = ClusteringModels.agglomerative_clustering
                        else:
                            return 'Non-Implemented Action'

                        for param in Model_Params:
                            model_params[param['name']] = get_param_value(param, request.form[param['name']])
                        print(model_params)
                        trained_model = train_model_fun(X_train, y_train, True, **model_params)

                        """Save Trained Model"""
                        save_project_model(trained_model)

                        reports = [{"key": "Model Name", "value": model},
                                   {"key": "Data Size", "value": len(df)},
                                   {"key": "Trained Data Size", "value": len(X_train)},
                                   {"key": "Test Data Size", "value": len(X_test)}]

                        scores = []
                        if trained_model is not None:
                            y_pred = trained_model.predict(X_test)
                            scores.append({"key": "r2_score", "value": r2_score(y_test, y_pred)})
                            scores.append({"key": "mean_absolute_error", "value": mean_absolute_error(y_test, y_pred)})
                            scores.append({"key": "mean_squared_error", "value": mean_squared_error(y_test, y_pred)})

                            return render_template('model_training/model_result.html', action=action, status="success",
                                                   reports=reports, scores=scores, model_params=model_params)
                        else:
                            raise Exception("Model Couldn't train, please check parametes")
                    except Exception as e:
                        logger.error('Error Submitted Custom Training Page')
                        ProjectReports.insert_record_ml('Error Submitted Custom Training Page',
                                                        f"Model:{model}; Range:{range}; Random_State: {random_state}",
                                                        '', 0, str(e))
                        if session['project_type'] == 2:
                            return render_template('model_training/classification.html', action=action,
                                                   models=CLASSIFICATION_MODELS, status="error", msg=str(e))
                        elif session['project_type'] == 1:
                            return render_template('model_training/regression.html', action=action,
                                                   models=REGRESSION_MODELS, status="error", msg=str(e))
                        else:
                            return render_template('model_training/clustering.html', action=action,
                                                   models=CLUSTERING_MODELS, status="error", msg=str(e))

                elif action == "auto_training":
                    try:
                        target = session['target_column']
                        if target is None:
                            return redirect(url_for('/target-column'))

                        data_len = len(df)
                        data_len = 10000 if data_len > 10000 else int(len(df) * 0.9)

                        df = df.sample(frac=1).loc[:data_len, :]
                        trainer = None
                        X = df.drop(target, axis=1)
                        y = df[target]
                        X_train, X_test, y_train, y_test = FeatureEngineering.train_test_Split(cleanedData=X,
                                                                                               label=y,
                                                                                               train_size=0.75,
                                                                                               random_state=45)
                        if session['project_type'] == 1:
                            trainer = ModelTrain_Regression(X_train, X_test, y_train, y_test, True)
                            result = trainer.results()
                            result = result.to_html()
                            return render_template('model_training/auto_training.html', status="success",
                                                   project_type=session['project_type'],
                                                   target_column=session['target_column'], train_done=True,
                                                   result=result)
                        elif session['project_type'] == 2:
                            trainer = ModelTrain_Classification(X_train, X_test, y_train, y_test, True)
                            result = trainer.results()
                    except Exception as ex:
                        return render_template('model_training/auto_training.html', status="error",
                                               project_type=session['project_type'],
                                               target_column=session['target_column'], msg=str(ex))
                else:
                    return "Non Implemented Method"
        else:
            logger.critical('DataFrame has no data')
    except Exception as e:
        logger.error('Error in Model Training Submit')
        ProjectReports.insert_record_ml('Error in Model Training', '', '', 0, str(e))


@app_training.route('/train_model', methods=['POST'])
def train_model_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                target = session['target_column']
                X = df.drop(target, axis=1)
                y = df[target]
                model = load_project_model()
                if model is None:
                    return render_template('model_training/model_result.html', action=action, status="error",
                                           msg="Model is not found, please train model again")
                else:
                    for key, vale in model.get_param():
                        exec(key + "=value")

            else:
                return "Non Implemented Method"
        else:
            logger.critical('DataFrame has no data')
    except Exception as e:
        logger.error('Error in Model Training Submit')
        ProjectReports.insert_record_ml('Error in Model Training', '', '', 0, str(e))
