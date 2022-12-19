from inky.inky_uc8159 import Inky
from PIL import Image, ImageFont, ImageDraw
from spotipy.oauth2 import SpotifyOAuth
import hitherdither
import spotipy
import os
import requests
import math


inky = Inky()
saturation = 0.5
thresholds = [64, 64, 64]
gutter_size = 5

index_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", 32)
title_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", 16)
body_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", 14)

palette = hitherdither.palette.Palette(
    inky._palette_blend(saturation, dtype='uint24'))


def get_wrapped_text(text: str, font: ImageFont.ImageFont,
                     line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)


def draw_now_playing(title, artist, album_name, album_art_url):
    bg = Image.new("RGBA", (inky.WIDTH, inky.HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)

    img = Image.open(requests.get(
        album_art_url, stream=True).raw).convert("RGB")
    img.thumbnail((inky.HEIGHT, inky.HEIGHT), Image.ANTIALIAS)
    image_dithered = hitherdither.ordered.bayer.bayer_dithering(
        img, palette, thresholds, order=2)
    bg.paste(image_dithered, (0, 0))

    line_broken_title = get_wrapped_text(title, title_font, line_length=140)
    artist_w, artist_h = body_font.getsize(artist)

    # Determine text size using a scratch image.
    tmp_img = Image.new("RGBA", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp_img)
    title_w, title_h = tmp_draw.textsize(line_broken_title, title_font)

    draw.text((img.width + gutter_size, 10),
              line_broken_title, 'Black', title_font)
    detail_start_y = title_h + 20
    draw.text((img.width + gutter_size, detail_start_y),
              artist, 'Black', body_font)
    draw.text((img.width + gutter_size, detail_start_y + artist_h + 5),
              album_name, 'Black', body_font)

    inky.set_image(bg)
    inky.show()


def draw_grid(entries):
    bg = Image.new("RGBA", (inky.WIDTH, inky.HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(bg)

    album_block_size = int(inky.HEIGHT / 3)

    for i, entry in enumerate(entries):
        x = i % 4
        y = math.floor(i / 4)
        img = Image.open(requests.get(entry['image'], stream=True).raw).convert("RGB")
        img.thumbnail((album_block_size, album_block_size), Image.ANTIALIAS)
        image_dithered = hitherdither.ordered.bayer.bayer_dithering(img, palette, thresholds, order=2)
        bg.paste(image_dithered, (x * album_block_size, y * album_block_size))
        draw.text(((x * album_block_size) + 2, (y * album_block_size) + 2), str(i + 1), font=index_font, fill='White', stroke_width=2, stroke_fill='Black')

    inky.set_image(bg)
    inky.show()


def simplify_track(track):
    return {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'image': track['album']['images'][0]['url']
    }

def simplify_artist(artist):
    return {
       'artist': artist['name'],
       'image': artist['images'][0]['url']
    }

def main():
    scope = 'user-read-currently-playing user-top-read'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))
    now_playing = sp.current_user_playing_track()
    if now_playing and now_playing['is_playing']:
        draw_now_playing(
            title=now_playing['item']['name'],
            artist=now_playing['item']['artists'][0]['name'],
            album_name=now_playing['item']['album']['name'],
            album_art_url=now_playing['item']['album']['images'][0]['url']
        )
    else:
        # most_played_tracks = sp.current_user_top_tracks(
        #    limit=12, time_range='short_term')
        most_played_artists = sp.current_user_top_artists(
            limit=12, time_range='medium_term')
        # draw_grid(list(map(simplify_track, most_played_tracks['items'])))
        draw_grid(list(map(simplify_artist, most_played_artists['items'])))


main()
