import json
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

class PlotlyHelper():
    @staticmethod
    def barplot(df,x,y):
        try:
             fig = px.bar(df, x=x,y=y)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass
        
    @staticmethod
    def pieplot(df,names,values,title=''):
        try:
            fig = px.pie(df, names=names,values=values,title=title)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
        except Exception as e:
            pass
        
    @staticmethod
    def scatterplot(df,x,y,title=''):
        try:
             fig = px.scatter(df, x=x,y=y,title=title)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass
        
    @staticmethod
    def histogram(df,x,y,bin=20):
        try:
             fig = px.histogram(df, x=x,y=y,nbins=bin)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass
        
    @staticmethod
    def line(df,x,y,bin=20):
        try:
             fig = px.line(df, x=x,y=y)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass
    
    @staticmethod
    def boxplot(df,y):
        try:
             fig = px.box(df, y=y)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass
        
    @staticmethod
    def distplot(x,y):
        try:
             hist_data = [x]
             group_labels = [y] # name of the dataset
             fig = ff.create_distplot(hist_data, group_labels)
             graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
             return graphJSON
        except Exception as e:
            pass