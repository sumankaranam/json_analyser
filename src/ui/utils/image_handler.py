from PIL import Image, ImageTk
import os
import platform
import subprocess

class ImageHandler:
    @staticmethod
    def create_thumbnail(filepath, size=(150, 150)):
        image = Image.open(filepath)
        image.thumbnail(size)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def open_image(filepath):
        system = platform.system()
        try:
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            raise Exception(f"Failed to open image: {str(e)}")
