import praw
import subprocess
import os
import json
import time
import random

# YOU CAN CREATE A REDDIT APP WITH THEIR API HERE: https://www.reddit.com/prefs/apps


reddit = praw.Reddit(
    client_id='PurUrRedditClientIDHere', # YOU NEED TO ADD YOUR CLIENT ID!
    client_secret='PurUrRedditClientSecretHere', # YOU NEED TO ADD YOUR CLIENT SECRET!
    user_agent='script:media_downloader:v1.0 (by u/YourRedditUser)' # YOU NEED TO ADD YOUR REDDIT USER!
)

script_directory = os.path.dirname(os.path.abspath(__file__))
video_directory = os.path.join(script_directory, "Videos")
archive_file = os.path.join(script_directory, "archive.json")

def load_existing_links():
    if os.path.exists(archive_file):
        with open(archive_file, 'r') as f:
            return json.load(f)
    return []

def save_links(links):
    with open(archive_file, 'w') as f:
        json.dump(links, f, indent=2)

def download_video_with_audio(post_url, output_filename):
    command = ['yt-dlp', post_url, '-o', output_filename]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode == 0:
        print(f"Downloaded: {output_filename}")
        return True
    elif result.returncode == 1:
        print(f"Error downloading video: {result.stderr.decode()}")
        return False
    return False

def download_videos(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    existing_links = load_existing_links()

    existing_set = {(entry['url'], entry['filename']) for entry in existing_links}

    downloaded_count = 0
    last_submission = None

    while True:
        new_posts = subreddit.new(limit=100, params={'after': last_submission})
        new_posts_list = list(new_posts)

        if not new_posts_list:
            print("All the videos in this subreddit have already been downloaded.")
            break

        for submission in new_posts_list:
            if submission.is_video:
                post_url = submission.url
                output_filename = os.path.join(video_directory, f"{submission.id}.mp4")

                if (post_url, output_filename) in existing_set:
                    print(f"Already downloaded: {post_url}")
                    continue

                if submission.media['reddit_video']['duration'] < 180:
                    for attempt in range(3):
                        if download_video_with_audio(post_url, output_filename):
                            new_entry = {'url': post_url, 'filename': output_filename}
                            existing_links.append(new_entry)
                            save_links(existing_links)
                            downloaded_count += 1
                            break
                        else:
                            print("Encountered error, retrying...")
                            time.sleep(random.randint(5, 15))

                    else:
                        print(f"Failed to download after multiple attempts: {post_url}")
                        continue

                    time.sleep(random.uniform(1, 3))

        last_submission = new_posts_list[-1].fullname

    if downloaded_count == 0:
        print("No new videos were downloaded.")
    else:
        print(f"Finished downloading {downloaded_count} videos.")

def main():
    subreddit_name = 'UnusualVideos'  # This is where you edit the subreddit
    download_videos(subreddit_name)

if __name__ == "__main__":
    main()
