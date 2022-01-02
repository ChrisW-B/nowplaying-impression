# from inky.inky_uc8159 import Inky
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth
import hitherdither
import spotipy
import os

# inky = Inky()
saturation = 0.8
thresholds = [64, 64, 64]


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ['SPOTIFY_CLIENT_ID'],
    client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
    redirect_uri='http://127.0.0.1:5000',
    open_browser=False,
    scope='user-read-currently-playing user-top-read'
))

palette = hitherdither.palette.Palette(
    inky._palette_blend(saturation, dtype='uint24'))


def write_image(image_url):
    bg = Image.new("RGBA", (inky.WIDTH, inky.HEIGHT), (255, 255, 255, 255))
    img = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
    image_dithered = hitherdither.ordered.cluster.cluster_dot_dithering(
        img, palette, thresholds, order=8)
    bg.paste(image_dithered, (150, 94))
    inky.set_image(bg)
    inky.show()


def main():
    now_playing = sp.current_user_playing_track()
    if now_playing['is_playing']:
        print(now_playing['item']['album']['images'][0]['url'])


main()
