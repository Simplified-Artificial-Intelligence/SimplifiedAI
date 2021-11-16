import json
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from src.eda.eda_helper import EDA
from loguru import logger
import os
from from_root import from_root
from src.utils.common.common_helper import read_config

config_args = read_config("./config.yaml")

log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")


class PlotlyHelper:
    @staticmethod
    def barplot(df, x, y):
        try:
            fig = px.bar(df, x=x, y=y)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("BarPlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def pieplot(df, names, values, title=''):
        try:
            fig = px.pie(df, names=names, values=values, title=title)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("PiePlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def scatterplot(df, x, y, title=''):
        try:
            fig = px.scatter(df, x=x, y=y, title=title)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("ScatterPlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def histogram(df, x, bin=20):
        try:
            fig = px.histogram(df, x=x, nbins=bin)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("Histogram Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def line(df, x, y, bin=20):
        try:
            fig = px.line(df, x=x, y=y)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("linePlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def boxplot(df, x, y):
        try:
            fig = px.box(df, x=x, y=y)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("BoxPlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def distplot(x, y):
        try:
            hist_data = [x]
            group_labels = [y]  # name of the dataset
            fig = ff.create_distplot(hist_data, group_labels)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("DistPlot Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)

    @staticmethod
    def heatmap(df, x):
        try:
            print(df[x])
            pearson_corr = EDA.correlation_report(df[x], 'pearson')
            persion_data = list(np.around(np.array(pearson_corr.values), 2))
            print(pearson_corr)
            fig = ff.create_annotated_heatmap(persion_data, x=list(pearson_corr.columns),
                                              y=list(pearson_corr.columns), colorscale='Viridis')
            # fig = ff.create_annotated_heatmap(persion_data, x=list(x),
            #                                   y=list(y), colorscale='Viridis')
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            logger.info("Heatmap Implemented!")
            return graphJSON
        except Exception as e:
            logger.error(e)
