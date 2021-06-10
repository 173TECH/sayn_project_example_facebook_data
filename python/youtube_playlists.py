import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from sayn import PythonTask


class AutoPlaylist(PythonTask):
    def get_existing_videos(self, playlist_id, existing_videos=[], nextPageToken=None):
        request = self.youtube.playlistItems().list(
            part="id,snippet",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=nextPageToken,
        )
        response = request.execute()
        playlist_length = int(response["pageInfo"]["totalResults"])
        if len(existing_videos) < playlist_length:
            for item in response["items"]:
                existing_videos.append(item["snippet"]["resourceId"]["videoId"])
            if "nextPageToken" in response.keys():
                self.get_existing_videos(
                    playlist_id, existing_videos, response["nextPageToken"]
                )

        return existing_videos

    def run(self):

        table = self.project_parameters["user_prefix"] + self.task_parameters["table"]
        user = self.task_parameters["user"]
        category = self.task_parameters["category"]
        playlist_name = user + "_" + category
        df = pd.DataFrame(
            self.default_db.read_data(
                f"SELECT DISTINCT video_id FROM {table} WHERE video_id IS NOT NULL AND chat_with = '{user}'"
            )
        )
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "secrets/client_secrets.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes
        )

        creds = flow.run_local_server(port=0)

        # using flow.authorized_session.
        session = flow.authorized_session()
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=creds
        )

        request = self.youtube.playlists().list(part="id, snippet", mine=True)
        response = request.execute()

        check = [
            item["id"]
            for item in response["items"]
            if item["snippet"]["title"] == playlist_name
        ]

        list_of_ids = df["video_id"].to_list()

        if len(check) > 0:
            playlist_id = check[0]
            list_of_ids = list(
                set(list_of_ids) ^ set(self.get_existing_videos(playlist_id))
            )
        else:
            request = self.youtube.playlists().insert(
                part="snippet", body={"snippet": {"title": playlist_name}}
            )
            response = request.execute()
            playlist_id = response["id"]

        list_length = len(list_of_ids)
        print(list_length)

        counter = 0
        category_videos = []

        while counter < list_length:
            if counter + 50 < list_length:
                video_ids = ",".join(list_of_ids[counter : counter + 50])
            else:
                video_ids = ",".join(list_of_ids[counter:list_length])

            request = self.youtube.videos().list(part="topicDetails", id=video_ids)
            response = request.execute()

            for x in response["items"]:
                try:
                    for value in x["topicDetails"]["topicCategories"]:
                        if value.lower().find(category) != -1:
                            category_videos.append(x["id"])
                            break
                except:
                    pass

            counter += 50

        for video in category_videos:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"videoId": video, "kind": "youtube#video"},
                }
            }
            request = self.youtube.playlistItems().insert(part="snippet", body=body)
            try:
                response = request.execute()
            except:
                pass

        return self.success()
