from io import BytesIO

from base64 import b64encode


def byte_img_to_html(img):
    a = BytesIO(img.read())
    img_data = a.getvalue()
    img_base64 = b64encode(img_data).decode('utf-8')

    return img_base64
