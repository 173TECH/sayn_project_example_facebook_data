import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sayn import PythonTask
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, get_single_color_func


class RenderCloud(PythonTask):

    def word_cloud(self, name, text, stopwords, b_colour = "white", c_colour = "black", show=False):
        """Word cloud generating function"""

        # attempt to find a compatible mask

        try:
            mask = np.array(Image.open(f"python/img/masks/{name}_mask.png"))
        except:
            mask = None

        color_func1 = get_single_color_func('deepskyblue')

        wordcloud = WordCloud(stopwords=stopwords
                              , max_words=100
                              , mask=mask
                              , background_color = b_colour
                              , contour_width=3
                              , contour_color= c_colour
                              , color_func = color_func1).generate(text)

        # store wordcloud image in "python/img"

        wordcloud.to_file(f"python/img/{name}_wordcloud.png")

        # declare show=True if you want to show wordclouds

        if show:
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()


    def setup(self):
        self.set_run_steps(
            [
                "Grouping texts",
                "Generating clouds"
            ]
        )
        return self.success()


    def run(self):

        with self.step("Grouping texts"):

            table = self.parameters["user_prefix"] + self.task_parameters["table"]

            df = pd.DataFrame(self.default_db.read_data(f"SELECT * FROM {table} WHERE type = 'Generic' AND content != 'no_data'"))
            full_text = " ".join(article for article in df.content)

            sources = df.groupby("sender_name")
            grouped_texts = sources.content.sum()


        with self.step("Generating clouds"):

            stopwords = STOPWORDS.update(self.parameters["stopwords"])
            self.info("Generating facebook_wordcloud.png")
            self.word_cloud("facebook", full_text, stopwords)

            # Source specific wordclouds

            for group, text in zip(grouped_texts.keys(), grouped_texts):
                self.info(f"Generating {group}_wordcloud.png")
                self.word_cloud(group, text, stopwords)


        return self.success()
