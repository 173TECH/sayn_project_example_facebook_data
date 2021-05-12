import random
import os
import pandas as pd
from PIL import Image
from sayn import PythonTask


class RenderCollage(PythonTask):

    def createImageGrid(self, images, dims, color = None):
        m, n = dims
        width = max([img.size[0] for img in images])
        height = max([img.size[1] for img in images])
        grid_img = Image.new('RGB', (n * width, m * height), color)
        for index in range(len(images)):
            row = int(index / n)
            col = index - n * row
            grid_img.paste(images[index], (col * width, row * height))
        return (grid_img)

    def getImages(self, files):
        images = []
        for file in files:
            filePath = os.path.abspath(file)
            try:
                fp = open(filePath, "r+b")
                im = Image.open(fp).convert("RGBA")
                img = Image.new("RGBA", im.size, "WHITE")
                img.paste(im, (0, 0), im)
                img.convert('RGB')
                img.filename = file
                images.append(img)
                im.load()
                fp.close()
            except Exception as e:
                print(f"{e}\nInvalid image: {file}")
        return (images)

    def run(self):

        images = self.task_parameters["images"]
        resolution = self.task_parameters["resolution"]
        grid = self.task_parameters["grid"]
        output = self.task_parameters["output"]

        df = pd.DataFrame(self.default_db.read_data(f"SELECT * FROM sticker_counts"))
        df["sticker_link"] = df["sticker_link"].str.replace("messages/", "python/img/")

        grid_size = (int(grid[0]), int(grid[1]))

        dims = (int(resolution[0]/grid_size[1]), int(resolution[1]/grid_size[0]))

        self.info(f"max tile dims: {dims}")

        for chat in df.chat_with.unique():
            for name in df.loc[df["chat_with"] == chat, "sender_name"].unique():
                stickers = df.loc[
                (df["chat_with"] == chat)
                & (df["sender_name"] == name)
                , ["sticker_link"]]
                input_images = self.getImages(stickers.sticker_link)
                for img in input_images:
                    img.thumbnail(dims)
                random.shuffle(input_images)
                collage_image = self.createImageGrid(input_images, grid_size, "WHITE")
                collage_image.save(f"{output}{chat}_{name}_collage.png", 'png')

        return self.success()
