from dataclasses import dataclass, field
from googleapiclient.discovery import build
import html
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
import os

os.environ['WDM_LOG_LEVEL'] = '0'


@dataclass()
class YouTubeComments:
    _api_service_name: str = field(default="youtube", init=False)
    _api_version: str = field(default="v3", init=False)
    developer_key: str = "<api key>"

    youtube = build(_api_service_name.default, _api_version.default, developerKey=developer_key)

    @staticmethod
    def get_video_basic_info(video_url: str):
        title, likes, views = "", "", ""
        i = 0
        while i < 3:
            options = Options()
            options.headless = True
            options.add_argument("--mute-audio")
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            with driver:
                driver.get(video_url)
                driver.implicitly_wait(3)

                driver.implicitly_wait(30)
                title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
                likes = driver.find_element_by_xpath(
                    '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a').text

                views_raw = driver.find_element_by_xpath('//*[@id="count"]/ytd-video-view-count-renderer/span[1]').text
                views = re.sub('[^0-9]', '', views_raw)

            if all([title, views, likes]):
                print("Done")
                break
            i += 1

        return title, likes, views

    def get_comments(self, video_url: str, max_results=50) -> dict:
        video_id = video_url.replace("https://www.youtube.com/watch?v=", "").split("&t=")[0].split("&list=")[0]
        print(f"Getting commnents for video: {video_url}, max results: {max_results}")

        comments_list = []
        likes_list = []
        published_at_list = []

        next_page_token = None
        max_res_reached = False
        comment_number = 0

        while True:
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                if comment_number < max_results:
                    comment = html.unescape(item['snippet']['topLevelComment']['snippet']['textDisplay'].replace("<br>", ""))
                    likes = item['snippet']['topLevelComment']['snippet']['likeCount']
                    published_at = item['snippet']['topLevelComment']['snippet']['publishedAt']

                    comments_list.append(comment)
                    likes_list.append(likes)
                    published_at_list.append(published_at)

                    comment_number += 1
                else:
                    max_res_reached = True
                    break

            try:
                next_page_token = response['nextPageToken']
            except KeyError:
                next_page_token = None
            print(f"Comments: {comment_number}/{max_results}")

            if not next_page_token or max_res_reached:
                break

        data = {
            "Date": published_at_list,
            "Likes": likes_list,
            "Comments": comments_list,
        }

        print("Done")
        return data


if __name__ == '__main__':
    ytc = YouTubeComments()
    print(ytc.get_video_basic_info("https://www.youtube.com/watch?v=N0Rycff1p3Q"))
