from youtubesearchpython import VideosSearch








def parse_views(views_str):
    """Parses the views string from YouTube and converts it to an integer.
    Example:
    5,909 views -> 5909
    """
    if views_str is None or views_str.lower() == 'no':
        return 0
    
    # Remove the "views" part and any commas
    views_str = views_str.replace("views", "").replace(",", "").strip()
    
    try:
        return int(float(views_str))
    except ValueError:
        return 0  # Return 0 if we can't parse the views string


    

def fetch_youtube_videos(Destination, Preferences, MIN_VIEWS, Max_results):
    """ 
    Fetches relevant YouTube videos based on the search term and user preferences.
    
    Parameters:
    - destination (str): The travel destination (e.g., "Paris, France").
    - preferences (list): List of user-selected preferences (e.g., ["food", "history", "nature"]).
    - max_results (int): The maximum number of videos to fetch.
    - MIN_VIEWS (int): The minimum number of views a video must have to be included in the results.
    Returns:
    - videos (list): List of dictionaries containing video details with views parsed as integers.
    """

    
    # Combine preferences into a search query
    preference_query = " ".join(Preferences)
    search_query = f"{Destination} travel guide {preference_query}"

    # Initialize videoSearch
    video_search = VideosSearch(search_query, limit=Max_results)

    # Execute search
    search_result = video_search.result()

    videos = []
    for video in search_result['result']:
        views_str = video['viewCount']['text']
        views = parse_views(views_str)
        print(f"Parsed views: {views}")

        # Filter out videos with fewer than MIN_VIEWS
        if views < MIN_VIEWS:
            continue  # Skip the video

        video_data = {
            'Title': video['title'],
            'url': video['link'],
            'Duration': video['duration'],
            'Views': views,
            'Channel': video['channel']['name'],
        }
        videos.append(video_data)

    return videos





