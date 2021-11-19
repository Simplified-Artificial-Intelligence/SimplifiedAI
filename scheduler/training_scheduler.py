from src.utils.common.common_helper import load_project_model, save_project_model
from src.model.custom.classification_models import ClassificationModels
from src.model.custom.regression_models import RegressionModels
from src.model.custom.clustering_models import ClusteringModels
from src.utils.common.project_report_helper import ProjectReports
from flask import session
import schedule
from src.utils.databases.mysql_helper import MySqlHelper


def check_schedule_model():
    # It will on root level
    # sort table data on the basis date and time
    # ascending order
    # start scheduler 1 by 1 after 1 hr
    # train result email
    mysql = MySqlHelper.get_connection_obj()
    query = """ select a.pid ProjectId , a.TargetColumn TargetName, 
                a.Model_Name ModelName, 
                b.Schedule_date, 
                b.schedule_time ,
                a.Model_Trained, 
                b.train_status ,
                b.email, 
                b.deleted
                from tblProjects as a
                join tblProject_scheduler as b on a.Pid = b.ProjectId where b.ProjectId = 'test'"""
    result = mysql.fetch_all(query=query)

    schedule.every()


def training_scheduler_(df, model_name, mysql, logger, date, time):
    ProjectReports.insert_record_ml('Training Schedule')
    target = session['target_column']
    X = df.drop(target, axis=1)
    y = df[target]
    model = load_project_model()
    if model is None:
        pass
    else:
        model_params = {}
        for key, value in model.get_params().items():
            model_params[key] = value
        if model_name == "LinearRegression":
            train_model_fun = RegressionModels.linear_regression_regressor
        elif model_name == "Ridge":
            train_model_fun = RegressionModels.ridge_regressor
        elif model_name == "Lasso":
            train_model_fun = RegressionModels.lasso_regressor
        elif model_name == "ElasticNet":
            train_model_fun = RegressionModels.elastic_net_regressor
        elif model_name == "DecisionTreeRegressor":
            train_model_fun = RegressionModels.decision_tree_regressor
        elif model_name == "RandomForestRegressor":
            train_model_fun = RegressionModels.random_forest_regressor
        elif model_name == "SVR":
            train_model_fun = RegressionModels.support_vector_regressor
        elif model_name == "AdaBoostRegressor":
            train_model_fun = RegressionModels.ada_boost_regressor
        elif model_name == "GradientBoostingRegressor":
            train_model_fun = RegressionModels.gradient_boosting_regressor
        elif model_name == "LogisticRegression":
            train_model_fun = ClassificationModels.logistic_regression_classifier
        elif model_name == "SVC":
            train_model_fun = ClassificationModels.support_vector_classifier
        elif model_name == "KNeighborsClassifier":
            train_model_fun = ClassificationModels.k_neighbors_classifier
        elif model_name == "DecisionTreeClassifier":
            train_model_fun = ClassificationModels.decision_tree_classifier
        elif model_name == "RandomForestClassifier":
            train_model_fun = ClassificationModels.random_forest_classifier
        elif model_name == "AdaBoostClassifier":
            train_model_fun = ClassificationModels.ada_boost_classifier
        elif model_name == "GradientBoostClassifier":
            train_model_fun = ClassificationModels.gradient_boosting_classifier
        elif model_name == "KMeans":
            train_model_fun = ClusteringModels.kmeans_clustering
        elif model_name == "DBSCAN":
            train_model_fun = ClusteringModels.dbscan_clustering
        elif model_name == "AgglomerativeClustering":
            train_model_fun = ClusteringModels.agglomerative_clustering
        else:
            return 'Non-Implemented Action'

        trained_model = train_model_fun(X, y, True, **model_params)

        """Save Final Model"""
        save_project_model(trained_model, 'model.pkl')
        query = f'''Update tblProjects Set Model_Trained=1 Where Id="{session.get('pid')}"'''
        mysql.update_record(query)
        logger.info('Final Training Done')
        ProjectReports.insert_record_ml('Final Training Done')
