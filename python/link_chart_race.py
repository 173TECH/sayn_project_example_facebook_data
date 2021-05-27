import pandas as pd
import numpy as np
import bar_chart_race as bcr
from sayn import PythonTask

class ChartRace(PythonTask):

    def setup(self):
        return self.success()

    def run(self):

        colours = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
        table = self.project_parameters["user_prefix"]+ self.task_parameters["table"]
        fixed = self.task_parameters["fixed"]
        df = pd.DataFrame(self.default_db.read_data(f"SELECT * FROM {table}"))
        an, ranks = bcr.prepare_long_data(df
                                        , index='created_year'
                                        , columns='share_host'
                                        , values='total_shares'
                                        , steps_per_period=1
                                        , orientation='h'
                                        , sort='desc')
        bcr.bar_chart_race(an
                         , filename='python/img/chart_race.gif'
                         , title='Total Shares by Website'
                         , steps_per_period = 15
                         , period_length = 2000
                         , cmap = 'Set3'
                         , fixed_order= fixed
                         , fixed_max= fixed)
        return self.success()
