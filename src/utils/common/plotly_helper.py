import json
import plotly
import plotly.express as px
import plotly.figure_factory as ff


class PlotlyHelper():
    @staticmethod
    def barplot(df,x,y,title=''):
        try:
             fig = px.bar(df, x=x,y=y,title=title)
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