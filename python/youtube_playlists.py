import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
from sayn import PythonTask

class AutoPlaylist(PythonTask):

    def run(self):

        table = self.project_parameters["user_prefix"]+ self.task_parameters["table"]
        df = pd.DataFrame(self.default_db.read_data(f"SELECT video_id FROM {table} WHERE video_id IS NOT NULL"))
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

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

        request = youtube.playlists().insert(
            part="snippet",
            body={
              "snippet": {
                "title": "full_playlist_1"
              }
            }
        )

        # request = youtube.playlists().list(part="id, snippet", mine=True)
        response = request.execute()

        playlist_id = response['id']

        for video in df['video_id']:
            body = {
              "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                  "videoId": video,
                  "kind": "youtube#video"
                }
              }
            }
            print(body)
            request = youtube.playlistItems().insert(
            part="snippet",
            body=body)
            try:
                response = request.execute()
            except:
                pass
            print(response)


        return self.success()
