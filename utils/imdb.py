import re

from config import Config

from imdb import Cinemagoer

imdb = Cinemagoer()

async def get_poster(query: str, bulk: bool = False, imdb_id: int = False, file: str = None) -> dict:
    if not imdb_id:
        query = (query.strip()).lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1]) 
        else:
            year = None
        movie_id = imdb.search_movie(title.lower(), results=10)
        if not movie_id:
            return None
        if year:
            filtered=list(filter(lambda k: str(k.get('year')) == str(year), movie_id))
            if not filtered:
                filtered = movie_id
        else:
            filtered = movie_id
        movie_id = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movie_id:
            movie_id = filtered
        if bulk:
            return movie_id
        movie_id = movie_id[0].movieID
    else:
        movie_id = query
    
    movie = imdb.get_movie(movie_id)

    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not Config.LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer":list_to_str(movie.get("writer")),
        "producer":list_to_str(movie.get("producer")),
        "composer":list_to_str(movie.get("composer")) ,
        "cinematographer":list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url':f'https://www.imdb.com/title/tt{movie_id}'
    }


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif Config.MAX_LIST_ELM:
        k = k[:int(Config.MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

