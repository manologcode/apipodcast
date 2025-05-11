import requests
import os

BASE_URL = "http://localhost:5000" # Replace with your application's base URL (using the exposed port)

def create_podcast(token: str, title: str, description: str, author: str, feed_url_slug: str, image_filepath: str, language: str = "es", category: str = None):
    """
    Creates a new podcast by sending a POST request to the API.

    Args:
        token: The API token for authentication.
        title: The title of the podcast.
        description: A brief description of the podcast.
        author: The author of the podcast.
        feed_url_slug: A unique slug for the podcast feed URL.
        image_filepath: The path to the podcast cover image file.
        language: The language of the podcast (default: "es").
        category: The category of the podcast (optional).

    Returns:
        A dictionary containing the created podcast data if successful, None otherwise.
    """
    url = f"{BASE_URL}/podcasts/"
    files = {'image_file': open(image_filepath, 'rb')}
    data = {
        'title': title,
        'description': description,
        'author': author,
        'feed_url_slug': feed_url_slug,
        'language': language,
    }
    if category:
        data['category'] = category

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating podcast: {e}")
        return None
    finally:
        files['image_file'].close() # Close the file after sending

def create_episode(token: str, podcast_id: int, title: str, description: str, audio_filepath: str, duration: str = None):
    """
    Creates a new episode for a given podcast by sending a POST request to the API.

    Args:
        token: The API token for authentication.
        podcast_id: The ID of the podcast the episode belongs to.
        title: The title of the episode.
        description: A brief description of the episode.
        audio_filepath: The path to the episode's audio file.
        duration: The duration of the episode in HH:MM:SS format (optional).

    Returns:
        A dictionary containing the created episode data if successful, None otherwise.
    """
    url = f"{BASE_URL}/podcasts/{podcast_id}/episodes/"
    files = {'audio_file': open(audio_filepath, 'rb')}
    data = {
        'title': title,
        'description': description,
    }
    if duration:
        data['duration'] = duration

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating episode: {e}")
        return None
    finally:
        files['audio_file'].close() # Close the file after sending

if __name__ == '__main__':
    # Example Usage (replace with actual data and file paths)

    # --- Configure your API Token ---
    API_TOKEN = "your_super_secret_token" # <-- REPLACE WITH YOUR ACTUAL API TOKEN

    # --- Create a Podcast ---
    print("Attempting to create a podcast...")
    podcast_data = create_podcast(
        token=API_TOKEN, # Pass the token
        title="My Awesome New Podcast",
        description="This is a test podcast created via the API client.",
        author="API Client User",
        feed_url_slug="my-awesome-new-podcast",
        image_filepath="podcast_cover.png", # <-- REPLACE WITH ACTUAL IMAGE PATH
        language="en",
        category="Technology"
    )

    if podcast_data:
        print("Podcast created successfully:")
        print(podcast_data)
        created_podcast_id = podcast_data.get("id")

        # --- Create an Episode (requires a created podcast ID) ---
        if created_podcast_id:
            print(f"\nAttempting to create an episode for podcast ID {created_podcast_id}...")
            episode_data = create_episode(
                token=API_TOKEN, # Pass the token
                podcast_id=created_podcast_id,
                title="First Episode",
                description="This is the first episode.",
                audio_filepath="episode_audio.mp3", # <-- REPLACE WITH ACTUAL AUDIO PATH
                duration="00:05:30"
            )

            if episode_data:
                print("Episode created successfully:")
                print(episode_data)
            else:
                print("Failed to create episode.")
        else:
            print("Could not create episode because podcast creation failed.")
    else:
        print("Failed to create podcast.")

    print("\nRemember to replace the placeholder file paths and data in the example usage.")
