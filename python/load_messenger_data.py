import json
import unicodedata as ud
from os import listdir
from datetime import datetime
from urllib.parse import urlsplit
import pandas as pd
from sayn import PythonTask



class LoadData(PythonTask):
    def convert_time(self, x, format):
        """Converts milliseconds timestamp to seconds"""
        return datetime.fromtimestamp(x / 1000).strftime(format)

    def try_get_value(self, x, column):
        """Unpacks columns with dictionary rows"""
        try:
            return x.get(column)
        except:
            pass

    def try_fix_emoji(self, x):
        """Fixes reaction emojis for easier visualisation"""
        try:
            return str(x).encode("latin1").decode("utf8")
        except:
            pass

    def setup(self):
        self.set_run_steps(["Process Data", "Load logs_chat_data", "Load Additional Tables"])
        return self.success()

    def run(self):

        with self.step("Process Data"):

            table = (
                self.project_parameters["user_prefix"] + self.task_parameters["table"]
            )

            users = [i for i in listdir("data/") if i != ".DS_Store"]

            for user in users:
                files = [
                    f"data/{user}/" + m
                    for m in listdir(f"data/{user}")
                    if m.startswith("message_")
                ]

                for file in files:
                    with open(file) as text:
                        data = json.load(text)
                        text.close()
                    temp_df = pd.DataFrame(data["messages"])
                    temp_df["chat_with"] = user
                    try:
                        main_df = main_df.append(temp_df, ignore_index=True)
                    except NameError:
                        main_df = temp_df

            # Anonymise friends (remove when released)
            # main_df.loc[main_df.sender_name != "Tim Sugaipov", "sender_name"] = main_df[
            #     "chat_with"
            # ]

            # Convert UNIX timestamps
            main_df["created_dt"] = main_df["timestamp_ms"].apply(
                self.convert_time, args=("%Y-%m-%d",)
            )
            main_df["created_ts"] = main_df["timestamp_ms"].apply(
                self.convert_time, args=("%Y-%m-%d %H:%M:%S",)
            )

            #  Unpack and process json parts of the data
            full_df = main_df.copy()
            json_columns = [
                "share",
                "photos",
                "reactions",
                "sticker",
                "gifs",
                "files",
                "videos",
                "audio_files",
            ]
            columns_to_drop = [column for column in full_df.columns if column in json_columns]

            if "share" in columns_to_drop:
                main_df["share_link"] = main_df["share"].apply(
                    self.try_get_value, args=("link",)
                )
                main_df["share_text"] = main_df["share"].apply(
                    self.try_get_value, args=("share_text",)
                )
            main_df = main_df.drop(columns=columns_to_drop)
            main_df["content"] = main_df["content"].fillna("")
            main_df.loc[
                main_df["content"].str.contains("https:", case=False), "type"
            ] = "Share"
            main_df["content"] = main_df["content"].apply(self.try_fix_emoji)

        with self.step("Load logs_chat_data"):
            if main_df is not None:

                main_df.to_sql(
                    table, self.default_db.engine, if_exists="replace", index=False
                )

        with self.step("Load Additional Tables"):
            base_columns = [
                    "chat_with",
                    "sender_name",
                    "timestamp_ms",
                    "created_ts",
                    "created_dt",
            ]

            for i in columns_to_drop:

                if i == "share":
                    full_df["share_link"] = full_df["share"].apply(
                        self.try_get_value, args=("link",)
                    )
                    full_df["share_text"] = full_df["share"].apply(
                        self.try_get_value, args=("share_text",)
                    )
                    full_df["share_host"] = full_df["share_link"].apply(
                        lambda x: urlsplit(x).hostname
                    )
                    columns_to_keep = base_columns + [i, "share_link", "share_text", "share_host"]
                elif i == "sticker":
                    full_df["sticker_link"] = full_df["sticker"].apply(
                        self.try_get_value, args=("uri",)
                    )
                    columns_to_keep = base_columns + [i, "sticker_link"]
                else:
                    full_df = full_df.explode(i, ignore_index=True)
                    if i != "reactions":
                        full_df[i + "_link"] = full_df[i].apply(
                            self.try_get_value, args=("uri",)
                        )
                        columns_to_keep = base_columns + [i, i + "_link"]
                    else:
                        full_df[i + "_type"] = full_df[i].apply(
                            self.try_get_value, args=("reaction",)
                        )
                        full_df[i + "_type"] = full_df[i + "_type"].apply(
                            self.try_fix_emoji
                        )
                        full_df[i + "_actor"] = full_df[i].apply(
                            self.try_get_value, args=("actor",)
                        )
                        columns_to_keep = base_columns + [i, "reactions_type", "reactions_actor"]

                full_df[i] = full_df[i].astype(str)
                data_to_write = full_df.loc[full_df[i] != "nan", columns_to_keep]
                self.info(f"Loading Table: {i}")
                data_to_write.to_sql(
                    i, self.default_db.engine, if_exists="replace", index=False
                )

        return self.success()
