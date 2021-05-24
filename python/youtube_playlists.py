import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from sayn import PythonTask

class AutoPlaylist(PythonTask):

    def run(self):

        table = self.project_parameters["user_prefix"]+ self.task_parameters["table"]
        user = self.task_parameters["user"]
        category = self.task_parameters["category"]
        playlist_name = user + "_" + category
        df = pd.DataFrame(self.default_db.read_data(f"SELECT DISTINCT video_id FROM {table} WHERE video_id IS NOT NULL AND chat_with = '{user}'"))
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "secrets/client_secrets.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)

        creds = flow.run_local_server(port=0)

        # using flow.authorized_session.
        session = flow.authorized_session()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=creds)

        request = youtube.playlists().list(
            part="id, snippet",
            mine=True
        )
        response = request.execute()

        check = [item['id'] for item in response["items"] if item["snippet"]["title"] == playlist_name]

        if len(check) > 0:
            playlist_id = check[0]
        else:
            request = youtube.playlists().insert(
                part="snippet",
                body={
                  "snippet": {
                    "title": playlist_name
                  }
                }
            )
            response = request.execute()
            playlist_id = response['id']

        list_of_ids = df['video_id'].to_list()
        list_length = len(list_of_ids)

        counter = 0
        music_videos = []

        while counter < list_length:
            if counter + 50 < list_length:
                video_ids = ",".join(list_of_ids[counter:counter+50])
            else:
                video_ids = ",".join(list_of_ids[counter:list_length])

            request = youtube.videos().list(part="topicDetails",id=video_ids)
            response = request.execute()

            for x in response['items']:
                try:
                    for value in x["topicDetails"]["topicCategories"]:
                        if value.lower().find("music") != -1 :
                            music_videos.append(x['id'])
                            break
                except:
                    pass

            counter+=50

        for video in music_videos:
            body = {
              "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                  "videoId": video,
                  "kind": "youtube#video"
                }
              }
            }
            request = youtube.playlistItems().insert(
            part="snippet",
            body=body)
            try:
                response = request.execute()
            except:
                pass

        return self.success()
