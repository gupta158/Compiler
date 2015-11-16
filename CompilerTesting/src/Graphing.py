import plotly.plotly as py
import plotly.graph_objs as go
import datetime


class LogGrapher():
    def __init__(self, file_name, y_axis_var):
        self.file_name = file_name
        self.y_axis_var = y_axis_var
        self.title = '{} of {}'.format(y_axis_var, file_name)

        self.data = []

        self.layout = go.Layout(
            title=self.title,
            xaxis=dict(
                title='time',
            ),
            yaxis=dict(
                title=y_axis_var,
            )
        )

    def add_trace(self, log_list):
        def convert_time(dt):
            dt_list = [int(d) for d in dt.split()]
            return datetime.datetime(month=dt_list[0],
                                     day=dt_list[1],
                                     year=dt_list[2],
                                     hour=dt_list[3],
                                     minute=dt_list[4],
                                     second=dt_list[5])

        t = [convert_time(d['timestamp']) for d in log_list]

        trace = go.Scatter(
            x=t,
            y=[d[self.y_axis_var] for d in log_list],
            mode='lines+markers',
            name='go.Scatter + dict'
        )

        self.data.append(trace)

    def plot(self):
        fig = go.Figure(data=self.data, layout=self.layout)
        plot_url = py.plot(fig, filename=self.file_name)
