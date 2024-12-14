import os
import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy import SpotifyOAuth

# Getting the user's prefer date to travel to.
user_music_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

# extracting the year that user entered
song_year = user_music_date.split("-")[0]

# billboard link due to that user's date that entered
billboard_link = f"https://www.billboard.com/charts/hot-100/{user_music_date}/"

# specifying user-agent in header's request for preventing related request errors
request_header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# requesting to billboard webpage to get the whole of html elements.
response = requests.get(url=billboard_link, headers=request_header)
response.raise_for_status()
billboard_html = response.text

# getting song titles and artist names using beautifulsoup through billboard webpage
soup = BeautifulSoup(billboard_html, "html.parser")
title_tags = soup.select(selector="div ul li ul li h3")
artist_tags = soup.select(selector="div ul li ul li span")

# extracting relevant data that we want from title_tags and artist_tags
song_titles = [content.get_text().replace("\n", "").replace("\t", "") for content in title_tags]
song_artists_unextracted = [content.get_text().replace("\n", "").replace("\t", "") for content in artist_tags]
extracted_song_artists = [content for content in song_artists_unextracted if
                          content.isnumeric() == False and content != "-"]

# checking if our song_titles is not empty if so it means that the user entered a date that billboard webpage does
# not have any content for that which also means the user entered a wrong date
if len(song_titles) != 0:

    # Working with Spotipy API
    # Authenticating to Spotify using OAuth way
    scope = "playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # holding the user id
    my_user_id = os.environ.get("SPOTIFY_USER_ID")

    counter = 0
    song_urls = []

    for item_index in range(len(song_titles)):
        song_link = None
        counter += 1

        # saving track name, artist name from the data that we scrap from billboard webpage
        track_name = song_titles[item_index].title()
        track_artist = extracted_song_artists[item_index].title()

        # our search query string by filtering it by track name, artist name and track released year
        search_query = f"track: {track_name} artist: {track_artist} year: {song_year}"

        print(counter)
        result = sp.search(q=search_query)
        for index in range(len(result["tracks"]["items"])):
            # getting the artist name, song name and song release year from the data the spotify api gave us using
            # search query method
            artist_name = result["tracks"]["items"][index]["album"]["artists"][0]["name"].title()
            song_name = result["tracks"]["items"][index]["name"].title()
            song_release_year = result["tracks"]["items"][index]["album"]["release_date"].split("-")[0]

            # checking our track name, track artist and year against the search query's artist name, song name and
            # song release year through some if else statements to narrow down search query to most releavent query.
            if artist_name == track_artist and song_name == track_name and song_release_year == song_year:
                song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                break

            else:
                if track_name == song_name and song_release_year == song_year:
                    song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                    break
                elif song_release_year == song_year and artist_name == track_artist:
                    song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                    break
                elif artist_name == track_artist and track_name == song_name:
                    song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                    break
                else:
                    if track_name == song_name:
                        song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                        break
                    elif song_release_year >= song_year or song_release_year <= song_year:
                        song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                        break
                    elif artist_name == track_artist:
                        song_link = result["tracks"]["items"][index]["external_urls"]["spotify"]
                        break
                    else:
                        # if we could not find any relevant query for our song we set the song_link to None
                        song_link = None
                        print(f"We Couldn't find any related song to that specific song: {track_name}")

        song_urls.append(song_link)

    # using for loop and temp_song_urls list to loop through song_urls list and remove items that are None and just
    # keep the one's that are url
    temp_song_urls = []
    for link in song_urls:
        if song_urls != None:
            temp_song_urls.append(link)
    song_urls = temp_song_urls

    # creating a playlist
    playlist_info = sp.user_playlist_create(user=my_user_id, name=f"{song_year} Billboard 100")

    # adding our song_urls list items into the playlist that we created
    playlist_id = playlist_info["id"]
    sp.user_playlist_add_tracks(user=my_user_id, playlist_id=playlist_id, tracks=song_urls)
    print("\n")
    print("-----------------------------------------------------------------------------")
    print("                                    Done!                                    ")
    print("-----------------------------------------------------------------------------")
else:
    print("We couldn't Find any related content to that specific date.\nPlease Try again!")
