from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
#from pytube import YouTube -- NOT WORKING, USE PYTUBEFIX INSTEAD.
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
import time
import os
import re

# Set up Chrome options for Selenium
chrome_options = Options()

# Run in headless mode (no browser UI)
#chrome_options.add_argument("--headless")

# https://stackoverflow.com/questions/71695438/why-do-i-need-no-sandbox-to-run-selenium-chromedriver-even-with-admin-privil
# These options are useful for limited enviroments like in a Docker container or cloud. If there is any issues with chrome crashing
# or something, check these two out.
#chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--disable-dev-shm-usage")

# Save the downloaded video file's URL into a txt file for duplicate fix.
downloaded_videos_file = 'downloaded_videos.txt'

def load_downloaded_videos():
    """
    Loads the downloaded YouTube video URLs.

    Returns:
    - A set of links.
    """

    # If there is no txt file including the video URLs in the working directory, return an empty set. Otherwise, return a set of URLs
    # included in the txt file with each line as an element.
    if not os.path.exists(downloaded_videos_file):
        return set()
    with open(downloaded_videos_file, 'r') as f:
        return set(line.strip() for line in f)

def save_downloaded_video(video_url):
    """
    Saves the downloaded YouTube video URLs.
    """

    with open(downloaded_videos_file, 'a') as f:
        f.write(video_url + '\n')

def check_title_for_nationality(title, target_nationality):
    """
    Checks video title for nationality.

    Parameters:
    - title: The title of the YouTube video.
    - target_nationality: The nationality filter to apply to video titles.

    Returns:
    - True or False.
    """

    # List of nationalities to skip
    nationality_words = ['American', 'Australian', 'British', 'Scottish', 'Indian', 'Irish', 'Canadian']

    # No more than 1 nationality word on the title.
    # If 'American' and 'British' words are concurrently included, return false.
    for nationality in nationality_words:
        if nationality in title and nationality != target_nationality:
            return False
    return True

def clean_title(title):
    """
    Removes invalid characters from the title to download the audio with no special character errors.

    Parameters:
    - title: The title of the YouTube video.

    Returns:
    - Cleaned title.
    """
    
    # Replace the special characters with '' in the title.
    cleaned_title = re.sub(r'[<>:"/\\|?*]', '', title)
    return cleaned_title

def parse_view_count(view_count_text):
    """
    Parses view count into integer from the search page.

    Parameters:
    - view_count_text: View count of the video in text format.

    Returns:
    - Parsed view_count_text(int).
    """

    # view_count_text: 15K views, 1M views, 947 views etc...
    # Replace the 'views' part with '' and remove any left spaces with strip.
    try:
        view_count_text = view_count_text.replace('views', '').strip()
        if 'K' in view_count_text:
            return int(float(view_count_text.replace('K', '')) * 1000)
        elif 'M' in view_count_text:
            return int(float(view_count_text.replace('M', '')) * 1000000)
        else:
            return int(view_count_text)
    except ValueError:
        return 0

def get_video_links(search_query, target_nationality, max_results=5, min_view_count=1000):
    """
    Gets the video links from YouTube search page.

    Parameters:
    - search_query: Search query for Youtube
    - target_nationality: The nationality filter to apply to video titles.
    - max_results: Max. number of videos to fetch

    Returns:
    - A set of video links.
    """

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.youtube.com')

    # Get the input element with name attribute set to 'search_query', send the query, press enter.
    search_box = driver.find_element(By.NAME, 'search_query')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    # Wait for the page to load
    time.sleep(5)  

    video_links = set()
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while len(video_links) < max_results:
        # Extract video links from the current page using soup, default usage.
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find video links on the current page
        # Find all the elements with id="video-title".
        # Or use this as id=media-item-metadata (only available if you use the mobile version m.youtube.com )
        # a tags that have thumbnail or video-title id are useful.
        for video in soup.find_all(id="video-title"):
            # Raw: Href: /watch?v=82oJt2enz8A&pp=ygUPdmlkZW9nYW1lZHVua2V5"
            # Get the href attribute's value.
            href = video['href']
            print(f'Href: {href}')
            
            # We don't need to check this but just making sure that we are getting a video's href. (For most cases, but sometimes the
            # href value can be a YouTube short's link.)
            if '/watch?v=' in href:
                # Extract video ID and ignore timestamps or extra params like pp.
                video_id = href.split('=')[1].split('&')[0]  
                full_url = f"https://www.youtube.com/watch?v={video_id}"

                # Check the title for the target nationality
                # If there's no title, title=''
                title = video.get('title', '')
                print(f'Title: {title}')
                if check_title_for_nationality(title, target_nationality):
                    # To check the view count of the video, we first find the parent div element that have 'meta' as id. This div elements 
                    # includes the span element that we can get the view count from.
                    parent_div = video.find_parent(id="meta")
                    if parent_div:
                        view_count_span = parent_div.find('span', class_='inline-metadata-item')
                        print(f'View count span: {view_count_span}')
                        print(f'View count span text: {view_count_span.text}')
                        if view_count_span:
                            # Output:
                            # Href: /watch?v=PUBnqS1qcvk&pp=ygUPdmlkZW9nYW1lZHVua2V5
                            # Title: San Andreas
                            # View count span: <span class="inline-metadata-item style-scope ytd-video-meta-block">12M views</span>
                            # View count span text: 12M views
                            view_count = parse_view_count(view_count_span.text)
                            # Only getting the videos that have at least 1K views.
                            if view_count >= min_view_count:
                                video_links.add(full_url)
                                if len(video_links) >= max_results:
                                    break

        # If there are enough video links founded, stop scrolling.
        if len(video_links) >= max_results:
            break
        else:
            # Go to bottom of the page.
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            # Wait for new results to load
            time.sleep(3)  

            # Get new height and check if it's changed.
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                print("Reached the bottom of the page, no more results.")
                break
            last_height = new_height

    driver.quit()
    return video_links

def get_videos_from_channel(channel_url, max_results=5):
    """
    Fetches video links from a specific YouTube channel.

    Parameters:
    - channel_url: The URL of the YouTube channel.
    - max_results: The maximum number of videos to fetch.
    Return:
    - Set of video URLs.
    """
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(channel_url)

    time.sleep(5)

    video_links = set()
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while len(video_links) < max_results:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for video in soup.find_all(id="video-title-link"):
            href = video['href']
            print(f'Href: {href}')
            # Output:
            # Href: /watch?v=ZlxIMlaQxww
            if '/watch?v=' in href:
                video_id = href.split('=')[1].split('&')[0]
                full_url = f"https://www.youtube.com/watch?v={video_id}"
                
                video_links.add(full_url)
                if len(video_links) >= max_results:
                    break

        
        if len(video_links) >= max_results:
            break
        else:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                print("Reached the bottom of the page, no more results.")
                break
            last_height = new_height

    driver.quit()
    return video_links

def get_videos_from_playlist(playlist_url, max_results=5):
    """
    Fetches video links from a specific YouTube playlist.

    Parameters:
    - channel_url: The URL of the YouTube playlist.
    - max_results: The maximum number of videos to fetch.
    Return:
    - Set of video URLs.
    """

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(playlist_url)

    time.sleep(5)

    video_links = set()
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while len(video_links) < max_results:
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for video in soup.find_all(id="video-title"):
            href = video['href']
            print(f'Href: {href}')
            # Output:
            # Href: /watch?v=KuvDsT4sRzU&list=PLMBTl5yXyrGRl2_kwa3tB2imqkb08_KvD&index=1&pp=iAQB
            if '/watch?v=' in href:
                video_id = href.split('=')[1].split('&')[0]
                full_url = f"https://www.youtube.com/watch?v={video_id}"
                
                video_links.add(full_url)
                if len(video_links) >= max_results:
                    break

        if len(video_links) >= max_results:
            break
        else:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)

            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                print("Reached the bottom of the page, no more results.")
                break
            last_height = new_height

    driver.quit()
    return video_links


def download_audio(video_url, accent_type, output_base_dir='audio_files'):
    # Create a folder with the accent type if it doesn't exist
    output_dir = os.path.join(output_base_dir, accent_type)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Using pytubefix, pytube is not working for some reason. (Default usage)
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        stream = yt.streams.get_audio_only()

        cleaned_title = clean_title(yt.title)

        file_path = stream.download(mp3=True, output_path=output_dir, filename=cleaned_title)
        print(f"Downloaded and saved audio to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def main():
     # Load previously downloaded videos
    downloaded_videos = load_downloaded_videos()
    
    # Search term for the videos
    accent_type = "Scottish"
    # Only getting the audios from the videos that have more than 1000 views and no more than 1 nationality word on the title.
    # British conversation listening, British podcast ?
    # British conversation listening, American conversation listening, Indian english podcast, 
    # The downlaoded videos must have at least 1K views...
    # Pick-out unrelated videos by hand - yes 
    search_query = f"{accent_type} conversation listening"
    channel_url = 'https://www.youtube.com/@TheCriticalDrinker/videos'
    playlist_url = 'https://www.youtube.com/playlist?list=PLCb8I5QEcjJWkanzPMWnyoxSICelVHnsa'
    # Max. number of new videos to download.
    max_new_videos = 1
    # Initial max. results to fetch.
    max_results = 5
    # Video count for each run until we reach the max_nex_videos.
    new_videos_count = 0
    

    while new_videos_count < max_new_videos:
        # Fetch a new set of video links
        video_links = get_videos_from_playlist(playlist_url, max_results=max_results)
        print(f"Found {len(video_links)} video links.")
        
        # Process each video URL
        for video_url in video_links:
            if video_url not in downloaded_videos:
                print(f"Processing new video: {video_url}")

                # Download audio for the video
                download_audio(video_url, accent_type)

                # Save the video URL
                save_downloaded_video(video_url)
                # Add the video URL to the set, to use on this runtime.
                downloaded_videos.add(video_url)  
                new_videos_count += 1
                
                if new_videos_count >= max_new_videos:
                    break
        
        if new_videos_count < max_new_videos:
            print(f"Not enough new videos found, trying again... (New videos founded on this run: {new_videos_count})")
            time.sleep(5)

            # Increase max_results for the next iteration to fetch more videos.
            max_results += 10
        else:
            print(f"Downloaded {new_videos_count} new videos.")

if __name__ == "__main__":
    main()