from flask import Blueprint,request,render_template,session,redirect,url_for
from flask.wrappers import Response
from src.utils.common.data_helper import load_data
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
from src.utils.common.plotly_helper import PlotlyHelper
from src.preprocessing.preprocessing_helper import Preprocessing
from src.utils.common.project_report_helper import ProjectReports
import pandas as pd
import numpy as np
from logger.logger import Logger
from src.eda.eda_helper import EDA
from pandas_profiling import ProfileReport
from src.constants.constants import TWO_D_GRAPH_TYPES
import plotly.figure_factory as ff
import json
import plotly
from src.utils.common.common_helper import immutable_multi_dict_to_str
import pdfkit 
import os

log = Logger()
log.info(log_type='INFO', log_message='Check Configuration Files')
app_eda = Blueprint('eda',__name__)


@app_eda.route('/eda/<action>')
def eda(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action=="data-summary":
                    ProjectReports.insert_record_eda('Redirect To Data Summary')
                    log.info(log_type='Data Summary', log_message='Redirect To Data Summary!')
                    summary=EDA.five_point_summary(df)
                    data=summary.to_html()
                    dtypes=EDA.data_dtype_info(df)
                    return render_template('eda/5point.html',data=data,dtypes=dtypes.to_html(),count=len(df),column_count=df.shape[1])
                elif action=="profiler":
                    ProjectReports.insert_record_eda('Redirect To Profile Report')
                    log.info(log_type='Profile Report', log_message='Redirect To Profile Report')
                    return render_template('eda/profiler.html',action=action)
                
                elif action=="show":
                    ProjectReports.insert_record_eda('Redirect To Show Dataset')
                    log.info(log_type='Show Dataset', log_message='Redirect To Eda Show Dataset!')
                    data=EDA.get_no_records(df,100)
                    data=data.to_html()
                    topselected=True
                    bottomSelected=False
                    selectedCount=100
                    return render_template('eda/showdataset.html',data=data,length=len(df),
                                           bottomSelected=bottomSelected,topselected=topselected,action=action,selectedCount=selectedCount,columns=df.columns)
                elif action=="missing":
                    ProjectReports.insert_record_eda('Redirect To Missing Value')
                    log.info(log_type='Missing Value Report', log_message='Redirect To Eda Show Dataset!')
                    df=EDA.missing_cells_table(df)
                    
                    graphJSON =  PlotlyHelper.barplot(df, x='Column',y='Missing values')
                    pie_graphJSON = PlotlyHelper.pieplot(df, names='Column',values='Missing values',title='Missing Values')
                    
                    data=df.drop('Column', axis=1, inplace=True)
                    data=df.to_html()
                    return render_template('eda/missing_values.html',action=action,data=data,barplot=graphJSON,pieplot=pie_graphJSON)
                
                elif action=="outlier":
                    ProjectReports.insert_record_eda('Redirect To Outlier')
                    log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    df = EDA.z_score_outlier_detection(df)
                    graphJSON = PlotlyHelper.barplot(df, x='Features', y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(
                        df.sort_values(by='Total outliers', ascending=False).loc[:10, :], names='Features',
                        values='Total outliers', title='Top 10 Outliers')
                    data=df.to_html()
                    return render_template('eda/outliers.html',data=data,method='zscore',action=action,barplot=graphJSON,pieplot=pie_graphJSON)
                
                
                elif action=="correlation":
                    ProjectReports.insert_record_eda('Redirect To Correlation')
                    pearson_corr=EDA.correlation_report(df,'pearson')
                    persion_data=list(np.around(np.array(pearson_corr.values),2))
                    fig = ff.create_annotated_heatmap(persion_data, x=list(pearson_corr.columns),
                                                      y=list(pearson_corr.columns), colorscale='Viridis')
                    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return render_template('eda/correlation.html',data=graphJSON,columns=list(pearson_corr.columns),action=action,method='pearson')
                
                elif action=="plots":
                    ProjectReports.insert_record_eda('Plots')
                    return render_template('eda/plots.html',columns=list(df.columns),
                                           graphs_2d=TWO_D_GRAPH_TYPES,action=action,x_column="",y_column="")
                else:
                    return render_template('eda/help.html')
            else:
                return 'Hello'

        else:
            return redirect(url_for('/'))
    except Exception as e:
        ProjectReports.insert_record_eda(e)
        print(e)


@app_eda.route('/eda/<action>', methods=['POST'])
def eda_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "show":
                    range = request.form['range']
                    optradio = request.form['optradio']
                    columns_for_list = df.columns
                    columns = request.form.getlist('columns')
                    log.info(log_type='Show Dataset', log_message='Redirect To Eda Show Dataset!')
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Show', input=input_str)
                    
                    if len(columns)>0:
                        df=df.loc[:,columns]
                        
                    data=EDA.get_no_records(df,int(range),optradio)
                    data=data.to_html()
                    topselected=True if optradio=='top' else False
                    bottomSelected=True if optradio=='bottom' else False
                    return render_template('eda/showdataset.html',data=data,length=len(df),
                                           bottomSelected=bottomSelected,topselected=topselected,action=action,selectedCount=range,columns=columns_for_list)
                elif action=="profiler":
                    ProjectReports.insert_record_eda('Download  Profile Report')
                    log.info(log_type='Profile Report', log_message='Download  Profile Report')
                    
                    pr = ProfileReport(df, explorative=True, minimal=True,
                                       correlations={"cramers": {"calculate": False}})
                    pr.to_widgets()
                    filename = os.path.join(os.path.join('src', 'project_reports'), f"{session.get('pid')}.html")
                    pr.to_file(filename)
                    with open(filename) as fp:
                        content = fp.read()
                        
                    return Response(
                        content,
                        mimetype="text/csv",
                        headers={"Content-disposition": "attachment; filename=report.html"})
                
                elif action=="correlation":
                    method = request.form['method']
                    columns = request.form.getlist('columns')

                    input_str = immutable_multi_dict_to_str(request.form,True)
                    ProjectReports.insert_record_eda('Redirect To Correlation', input=input_str)
                    
                    if method is not None:
                        # df=df.loc[:,columns]
                        _corr = EDA.correlation_report(df, method)
                        if len(columns) == 0:
                            columns = _corr.columns

                        _corr = _corr.loc[:, columns]
                        _data = list(np.around(np.array(_corr.values), 2))
                        fig = ff.create_annotated_heatmap(_data, x=list(_corr.columns),
                                                          y=list(_corr.index), colorscale='Viridis')
                        # fig = ff.create_annotated_heatmap(_data, colorscale='Viridis')
                        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template('eda/correlation.html', data=graphJSON,
                                               columns=list( df.select_dtypes(exclude='object').columns), action=action, method=method)
                    else:
                        return render_template('eda/help.html')

                elif action == "outlier":
                    method = request.form['method']
                    lower = 25
                    upper = 75
                    if method == "iqr":
                        lower = request.form['lower']
                        upper = request.form['upper']
                        df = EDA.outlier_detection_iqr(df, int(lower), int(upper))
                    else:
                        df=EDA.z_score_outlier_detection(df)

                    input_str = immutable_multi_dict_to_str(request.form,True)
                    ProjectReports.insert_record_eda('Redirect To Outlier', input=input_str)
                    
                    graphJSON =  PlotlyHelper.barplot(df, x='Features',y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(df.sort_values(by='Total outliers',ascending=False).loc[:9,:], names='Features',values='Total outliers',title='Top 10 Outliers')    

                    log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    data = df.to_html()
                    return render_template('eda/outliers.html', data=data, method=method, action=action, lower=lower,
                                           upper=upper, barplot=graphJSON, pieplot=pie_graphJSON)

                elif action == "plots":
                    """All Polots for all kind of features????"""
                    selected_graph_type = request.form['graph']
                    x_column = request.form['xcolumn']
                    y_column = request.form['ycolumn']
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Plot', input=input_str)
                    
                    if selected_graph_type=="Scatter Plot":
                        graphJSON =  PlotlyHelper.scatterplot(df, x=x_column,y=y_column,title='Scatter Plot')                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    
                    elif selected_graph_type=="Pie Chart":
                        graphJSON =  PlotlyHelper.scatterplot(df, x=x_column,y=y_column,title='Scatter Plot')                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                    elif selected_graph_type=="Bar Graph":
                        graphJSON =  PlotlyHelper.barplot(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    
                    elif selected_graph_type=="Histogram":
                        graphJSON =  PlotlyHelper.histogram(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                    elif selected_graph_type=="Line Chart":
                        graphJSON =  PlotlyHelper.line(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                        
                    return render_template('eda/plots.html',selected_graph_type=selected_graph_type,
                                           columns=list(df.columns),graphs_2d=TWO_D_GRAPH_TYPES,
                                           action=action,graphJSON=graphJSON,x_column=x_column,y_column=y_column)

                else:
                    return render_template('eda/help.html')
            else:
                """Manage This"""
                pass

        else:
            return redirect(url_for('/'))
    except Exception  as e:
        ProjectReports.insert_record_eda(e)
            
