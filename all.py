import praw
import subprocess
import os
import json
import time
import random
import requests

# YOU CAN CREATE A REDDIT APP WITH THEIR API HERE: https://www.reddit.com/prefs/apps


reddit = praw.Reddit(
    client_id='PurUrRedditClientIDHere', # YOU NEED TO ADD YOUR CLIENT ID!
    client_secret='PurUrRedditClientSecretHere', # YOU NEED TO ADD YOUR CLIENT SECRET!
    user_agent='script:media_downloader:v1.0 (by u/YourRedditUser)' # YOU NEED TO ADD YOUR REDDIT USER!
)

script_directory = os.path.dirname(os.path.abspath(__file__))
video_directory = os.path.join(script_directory, "Videos")
image_directory = os.path.join(script_directory, "Pictures")
gif_directory = os.path.join(script_directory, "Gifs")
archive_file = os.path.join(script_directory, "archive.json")

os.makedirs(video_directory, exist_ok=True)
os.makedirs(image_directory, exist_ok=True)
os.makedirs(gif_directory, exist_ok=True)

def load_existing_links():
    if os.path.exists(archive_file):
        with open(archive_file, 'r') as f:
            return json.load(f)
    return []

def save_links(links):
    with open(archive_file, 'w') as f:
        json.dump(links, f, indent=2)

def download_video(post_url, output_filename):
    command = ['yt-dlp', post_url, '-o', output_filename]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(f"Downloaded: {output_filename}")
        return True
    elif result.returncode == 1:
        print(f"Error downloading video: {result.stderr.decode()}")
        return False
    return False

def download_image(image_url, output_filename):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded image: {output_filename}")
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def download_gif(gif_url, output_filename):
    return download_image(gif_url, output_filename)

def download_media(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    existing_links = load_existing_links()

    existing_set = {(entry['url'], entry['filename']) for entry in existing_links}

    downloaded_count = 0
    last_submission = None

    while True:
        new_posts = subreddit.new(limit=100, params={'after': last_submission})
        new_posts_list = list(new_posts)

        if not new_posts_list:
            print("All the media in this subreddit have already been downloaded.")
            break

        for submission in new_posts_list:
            if submission.is_video:
                post_url = submission.url
                output_filename = os.path.join(video_directory, f"{submission.id}.mp4")

                if (post_url, output_filename) in existing_set:
                    print(f"Already downloaded: {post_url}")
                    continue

                if submission.media['reddit_video']['duration'] < 180:
                    if download_video(post_url, output_filename):
                        new_entry = {'url': post_url, 'filename': output_filename}
                        existing_links.append(new_entry)
                        save_links(existing_links)
                        downloaded_count += 1

            else:
                image_url = submission.url

                if any(image_url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                    output_filename = os.path.join(image_directory, f"{submission.id}.png")
                    if (image_url, output_filename) not in existing_set and download_image(image_url, output_filename):
                        new_entry = {'url': image_url, 'filename': output_filename}
                        existing_links.append(new_entry)
                        save_links(existing_links)
                        downloaded_count += 1

                elif image_url.endswith('.gif'):
                    output_filename = os.path.join(gif_directory, f"{submission.id}.gif")
                    if (image_url, output_filename) not in existing_set and download_gif(image_url, output_filename):
                        new_entry = {'url': image_url, 'filename': output_filename}
                        existing_links.append(new_entry)
                        save_links(existing_links)
                        downloaded_count += 1

        last_submission = new_posts_list[-1].fullname

    if downloaded_count == 0:
        print("No new media was downloaded.")
    else:
        print(f"Finished downloading {downloaded_count} media files.")

def main():
    subreddit_name = 'UnusualVideos'  # THIS IS WHERE YOU EDIT WHAT SUBREDDIT IT IS SCANNING!
    download_media(subreddit_name)

if __name__ == "__main__":
    main()
