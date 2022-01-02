from requests import post, get
from PIL import Image
from inky.inky_uc8159 import Inky
import hitherdither

inky = Inky()
saturation = 0.8
thresholds = [64, 64, 64]
url = "http://api.chriswb.dev/"

palette = hitherdither.palette.Palette(
    inky._palette_blend(saturation, dtype='uint24'))

query = """{lastfm{nowplaying{title artist image nowplaying}}}
"""

headers = {"Content-Type": "application/json"}

response = post(url, json={'query': query}, headers=headers)

if response.status_code == 200:
    json = response.json()
    track = json['data']['lastfm']['nowplaying']
    if track['nowplaying'] == True:
        bg = Image.new("P", (inky.WIDTH, inky.HEIGHT))
        img = Image.open(get(track['image'], stream=True).raw)
        # image_dithered = hitherdither.ordered.bayer.bayer_dithering(image, palette, thresholds, order=8)
        image_dithered = hitherdither.ordered.cluster.cluster_dot_dithering(
            img, palette, thresholds, order=8)
        CENTERED_IMG = inky.HEIGHT / 2
        bg.paste(image_dithered, (0, int(CENTERED_IMG)))
        inky.set_image(bg)
        inky.show()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(
        response.status_code, query))
