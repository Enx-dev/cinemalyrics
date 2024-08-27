import requests
import requests_cache
import json
import pandas as pd


def process_info(info):
    target_element = {}
    target_element_list = [
        "budget",
        "revenue",
        "production_companies",
        "production_countries",
        "runtime",
    ]
    for key in target_element_list:
        if type(info[key]) is list:
            local_list = []
            for item in info[key]:
                local_list.append(item["name"])
            target_element[key] = local_list
        else:
            target_element[key] = info[key]
    return target_element


def get_info(movie_id, session):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9"
            ".eyJhdWQiOiJkMDY5OTU2OTQ0YWQ5YzRmOTkyZDgyZjkzZjA"
            "5OTU3MyIsInN1YiI6IjY2MGQ5MWM1OWM5N2JkMDE3Y2E3MDYw"
            "ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ."
            "iNXODGxzgXAF9f-3fTHLABjsR-_00OfRk_3Y59Gwmbk",
        }
        response = session.get(url, headers=headers)
        info = json.loads(response.text)
        return process_info(info)
    except requests.exceptions.RequestException as e:
        print(e.errno)


#
def get_movies(start_page: int = 1, end_page: int = 30):
    session = requests_cache.CachedSession("movie")
    page_movies = []
    for i in range(start_page, end_page):
        try:
            url = (
                f"https://api.themoviedb.org/3/discover/movie?include_video=false&language=en-US&page={i}&sort_by"
                f"=popularity.desc"
            )

            headers = {
                "accept": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9"
                ".eyJhdWQiOiJkMDY5OTU2OTQ0YWQ5Y"
                "zRmOTkyZDgyZjkzZjA5OTU3MyIsInN1Yi"
                "I6IjY2MGQ5MWM1OWM5N2JkMDE3Y2E3MDYwZSIs"
                "InNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIj"
                "oxfQ.iNXODGxzgXAF9f-3fTHLABjsR-_00OfRk_3Y59Gwmbk",
            }

            response = session.get(url, headers=headers)
            for item in json.loads(response.text)["results"]:
                movie_item = {**item, **get_info(item["id"], session)}
                page_movies.append(movie_item)
        except requests.exceptions.RequestException:
            print("Something went wrong")
    page_movies = pd.DataFrame(page_movies)
    page_movies = page_movies.drop(
        columns=[
            "backdrop_path",
            "id",
            "original_title",
            "overview",
            "poster_path",
            "video",
            "vote_average",
            "vote_count",
        ]
    )
    return page_movies


def get_genres():
    session = requests_cache.CachedSession("genre_cache")
    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9"
        ".eyJhdWQiOiJkMDY5OTU2OTQ0YWQ5YzRmOTkyZDgyZjkzZjA5OT"
        "U3MyIsInN1YiI6IjY2MGQ5MWM1OWM5N2JkMDE3Y2E3MDYw"
        "ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.iNXODGxzgXAF9f-3fTHLABjsR"
        "-_00OfRk_3Y59Gwmbk",
    }

    response = session.get(url, headers=headers)
    genres = json.loads(response.text)["genres"]
    return genres


def genre_transform(L):
    genres = get_genres()
    new_list = []
    for _id in L:
        new_list.append(int(_id))
    genre_list = [x["name"] for x in genres if x["id"] in new_list]
    return genre_list


def lang_transform(code, codes):
    if code in codes["639-1"].tolist():
        return codes.loc[codes["639-1"].isin([code])][
            "Language name(s) from ISO 639-2[1]"
        ].to_string(index=False)
    else:
        return code
