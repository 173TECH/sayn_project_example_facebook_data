import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sayn import PythonTask
from PIL import Image, ImageDraw, ImageFont
from wordcloud import WordCloud, STOPWORDS, get_single_color_func


class RenderCloud(PythonTask):
    def load_images(self, images):
        out_images = []
        for i in images:
            img = Image.open(open(i, "rb"))
            out_images.append(img)

        return out_images

    def remove_images(self, images):

        for i in images:
            os.remove(i)

    def create_gif(self, images, chat_and_sender):
        """GIF generating function with image labels and fade transitions"""
        loaded_images = self.load_images(images)
        gif_images = []
        durations = []
        for i in range(1, len(loaded_images) + 1):
            if i == len(loaded_images):
                img1, img2 = loaded_images[-1], loaded_images[0]
                title1, title2 = images[-1][-18:-14], images[0][-18:-14]
            else:
                img1, img2 = loaded_images[i - 1], loaded_images[i]
                title1, title2 = images[i - 1][-18:-14], images[i][-18:-14]
            d1, d2 = ImageDraw.Draw(img1), ImageDraw.Draw(img2)
            font = ImageFont.truetype("OpenSans-Bold.ttf", 50)
            d1.text((0, 0), title1, font=font, fill=(0, 0, 0))
            d2.text((0, 0), title2, font=font, fill=(0, 0, 0))
            gif_images.extend([Image.blend(img1, img2, a / 5) for a in range(0, 6)])
            durations.extend([1000 if t in (0, 5) else 1 for t in range(0, 6)])
        file_path = f"python/img/{chat_and_sender}_timelapse.gif"
        gif_images[0].save(
            file_path,
            save_all=True,
            append_images=gif_images[1:],
            optimize=False,
            duration=durations,
            loop=0,
        )
        self.remove_images(images)

    def word_cloud(
        self,
        name,
        text,
        stopwords,
        b_colour="white",
        c_colour="black",
        show=False,
        sender=None,
    ):
        """Word cloud generating function"""

        # attempt to find a compatible mask

        try:
            if sender == self.task_parameters["facebook_name"]:
                mask = np.array(Image.open(f"python/img/masks/Me_mask.png"))
            else:
                mask = np.array(Image.open(f"python/img/masks/Friend_mask.png"))
        except:
            mask = None

        color_func1 = get_single_color_func("deepskyblue")

        wordcloud = WordCloud(
            stopwords=stopwords,
            max_words=50,
            mask=mask,
            background_color=b_colour,
            contour_width=3,
            contour_color=c_colour,
            color_func=color_func1,
        ).generate(text)

        # store wordcloud image in "python/img"

        wordcloud.to_file(f"python/img/{name}_wordcloud.png")

        # declare show=True if you want to show wordclouds

        if show:
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()

        return wordcloud

    def setup(self):
        self.set_run_steps(["Grouping texts", "Generating clouds"])
        return self.success()

    def run(self):

        with self.step("Grouping texts"):

            table = self.parameters["user_prefix"] + self.task_parameters["table"]

            df = pd.DataFrame(
                self.default_db.read_data(
                    f"SELECT * FROM {table} WHERE type = 'Generic' AND content != 'no_data'"
                )
            )
            full_text = " ".join(article for article in df.content)

            sources = df.groupby(by=["chat_with", "sender_name", "year"])
            grouped_texts = sources.content.sum()

        with self.step("Generating clouds"):

            stopwords = STOPWORDS.update(self.parameters["stopwords"])
            self.info("Generating facebook_wordcloud.png")
            self.word_cloud("facebook", full_text, stopwords)

            # Timelapse wordcloud GIFs

            images = {}

            for group, text in zip(grouped_texts.keys(), grouped_texts):
                chat, sender, year = group
                chat_and_sender = chat + "_" + sender
                name = chat + "_" + sender + "_" + year
                self.info(f"Generating {name}_wordcloud.png")
                self.word_cloud(name, text, stopwords, sender=sender)
                if chat_and_sender in images.keys():
                    images[chat_and_sender].append(f"python/img/{name}_wordcloud.png")
                else:
                    images[chat_and_sender] = [f"python/img/{name}_wordcloud.png"]

            for key in images.keys():
                self.create_gif(images[key], key)

        return self.success()
