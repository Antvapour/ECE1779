#from wand.image import Image
#import os
#from wand.display import display

#def resize_photo():
#    for filename in os.listdir(r"./Users/gaowenhuan/Desktop/A1_wenhuan/app/static"):
#
#        with Image(filename=filename) as img:
              with img.clone() as image:
                size = image.width if image.width < image.height else image.height
                image.crop(width=size, height=size, gravity='center')
                image.resize(256, 256)

                image.format = 'jpeg'

#         return（）



