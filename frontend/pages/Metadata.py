import streamlit as st

st.title("Metadata Analysis")

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

def show_image_metadata(info_dict):
    for key, value in info_dict.items():
        st.text(f"{key}: {value}")
        # st.write("")

import pikepdf

def get_pdf_metadata(pdf_file):
    with pikepdf.Pdf.open(pdf_file) as pdf:
        return dict(pdf.docinfo)

def show_pdf_metadata(metadata):
    for key, value in metadata.items():
        st.text(f"{key} : {value}")
        st.write("")

pdf = st.file_uploader("Upload a file to analyze its metadata", type=["pdf"])
button_pdf = st.button("Analyze PDF Metadata", type = "primary")



if button_pdf and pdf is not None:
    metadata = get_pdf_metadata(pdf)
    show_pdf_metadata(metadata)

elif button_pdf:
    st.error("Please upload a PDF file first.")

image = st.file_uploader("Upload an image to analyze its metadata", type=["jpeg", "png", "jpg"])
button_image = st.button("Analyze Image Metadata", type = "primary")

if button_image and image is not None:
    metadata = get_image_metadata(image)
    show_image_metadata(metadata)
elif button_image:
    st.error("Please upload an image file first.")