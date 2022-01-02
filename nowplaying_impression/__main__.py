import requests
from PIL import Image
from inky.inky_uc8159 import Inky
import hitherdither

inky = Inky()
saturation = 0.8
thresholds = [64, 64, 64]
url = "http://api.chriswb.dev/"

palette = hitherdither.palette.Palette(
    inky._palette_blend(saturation, dtype='uint24'))

payload = "{\"query\":\"{\\n  lastfm {\\n    nowplaying {\\n      title\\n      artist\\n      image\\n      nowplaying\\n      id\\n    }\\n  }\\n}\\n\"}"
headers = {"Content-Type": "application/json"}

response = requests.request("POST", url, data=payload, headers=headers)

if response.status_code == requests.codes.ok:
    json = response.json()
    track = json['data']['lastfm']['nowplaying']
    if track['nowplaying'] == True:
        bg = Image.new("RGBA", (inky.WIDTH, inky.HEIGHT), (255,255,255,255))
        img = Image.open(requests.get(track['image'], stream=True).raw).convert("RGB")
        # image_dithered = hitherdither.ordered.bayer.bayer_dithering(img, palette, thresholds, order=8)
        image_dithered = hitherdither.ordered.cluster.cluster_dot_dithering(img, palette, thresholds, order=8)
        bg.paste(image_dithered, (150, 94))
        inky.set_image(bg)
        inky.show()
else:
        response.raise_for_status()