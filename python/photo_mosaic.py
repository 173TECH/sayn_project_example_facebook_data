import random
from sayn import PythonTask
from PIL import Image
from .mosaic_creator import getImages, createPhotomosaic


class RenderMosaic(PythonTask):
    def setup(self):
        self.set_run_steps(["Assigning Parameters", "Generating Mosaic"])
        return self.success()

    def run(self):

        with self.step("Assigning Parameters"):
            target = self.task_parameters["target"]
            user_data = self.task_parameters["user_data"]
            grid = self.task_parameters["grid"]
            output = self.task_parameters["output"]

        with self.step("Generating Mosaic"):

            target_image = Image.open(target)

            # input images
            images = f"python/messenger_data/{user_data}/photos"
            self.info(f"Reading input folder {images}")
            input_images = getImages(images)

            # check if any valid input images found
            if input_images == []:
                self.info(f"No input images found in {images}")
                exit()

            # shuffle list - to get a more varied output?
            random.shuffle(input_images)

            # size of grid
            grid_size = (int(grid[0]), int(grid[1]))

            # output
            output_filename = "mosaic.jpeg"
            if output:
                output_filename = output

            # re-use any image in input
            reuse_images = True

            # resize the input to fit original image size?
            resize_input = True

            self.info("Starting photomosaic creation...")

            # if images can't be reused, ensure m*n <= num_of_images
            if not reuse_images:
                if grid_size[0] * grid_size[1] > len(input_images):
                    self.info("Grid size less than number of images")
                    exit()

            # resizing input
            if resize_input:
                self.info("Resizing images...")
                # for given grid size, compute max dims w,h of tiles
                dims = (
                    int(target_image.size[0] / grid_size[1]),
                    int(target_image.size[1] / grid_size[0]),
                )
                self.info(f"max tile dims: {dims}")
                # resize
                for img in input_images:
                    img.thumbnail(dims)

            # create photomosaic
            mosaic_image = createPhotomosaic(
                target_image, input_images, grid_size, reuse_images
            )

            # write out mosaic
            mosaic_image.save(output_filename, "jpeg")

            self.info(f"Saved output to {output_filename}")

        return self.success()
