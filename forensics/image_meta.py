from PIL import Image
from PIL.ExifTags import TAGS

def get_image_metadata(image_file):
# read the image data using PIL
    image = Image.open(image_file)
    # extract other basic metadata
    info_dict = {
    "Filename": image.filename ,
    "Image Size": image.size,
    "Image Height": image.height,
    "Image Width": image.width,
    "Image Format": image.format,
    "Image Mode": image.mode,
    "Image is Animated": getattr(image, "is_animated", False),
    "Frames in Image": getattr(image, "n_frames", 1)
    }
    # extract EXIF data
    exifdata = image.getexif()
    # iterating over all EXIF data fields
    for tag_id in exifdata:
    # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
    # decode bytes
        if isinstance(data, bytes):
            data = data.decode()
        # print(f"{tag:25}: {data}")
        info_dict[tag] = data
    return info_dict

def print_image_metadata(info_dict):
    for key, value in info_dict.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    print_image_metadata(get_image_metadata("metadata.png"))
    print()
    print_image_metadata(get_image_metadata("food.jpg"))
    print()
    print_image_metadata(get_image_metadata("image.jpg"))



