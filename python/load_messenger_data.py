from sayn import PythonTask
from os import listdir
import json
from datetime import datetime
import pandas as pd

class LoadData(PythonTask):

    def setup(self):
        self.set_run_steps(
            [
                "Process Data",
                "Load Data"
            ]
        )
        return self.success()

    def run(self):

        with self.step("Process Data"):

            table = self.project_parameters["user_prefix"]+ self.task_parameters["table"]

            files = ["python/messenger_data/user_1/" + m for m in listdir("python/messenger_data/user_1") if m.startswith("message_")]

            for i, file in enumerate(files):
                with open(file) as text:
                    data = json.load(text)
                    text.close()
                temp_df = pd.DataFrame(data["messages"])
                if i == 0:
                    main_df = temp_df
                else:
                    main_df = main_df.append(temp_df, ignore_index=True)

            main_df = main_df.iloc[:, :5].fillna("no_data")

            main_df.loc[main_df["content"].str.contains("https:", case=False), "type"] = "Share"

        with self.step("Load Data"):
            if main_df is not None:

                main_df.to_sql( table
                           ,self.default_db.engine
                           ,if_exists="replace"
                           ,index=False)

        return self.success()
