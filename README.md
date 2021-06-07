This is an example SAYN project. It shows you how to implement and use SAYN for data processing and modelling.

For more details, you can see the documentation here: https://173tech.github.io/sayn/

DAG of this project:
![ETL](/dag.png)


Quick Overview:

To run this project you will need your Facebook Messenger data in JSON format, you can get request it by doing the following:
- Settings & Privacy > Settings > Your Facebook Information > Download Your Information 
- Change format to JSON and click Create File (this can take a while depending on your date range and media quality)

Once you have the data:
- Copy the folder called `inbox` inside the `messages` subfolder and paste it inside the `python` folder of the project
- Rename the `inbox` folder to `messenger_data`
- Rename the file `sample_settings` to `settings` (this can be found in the root of the project)

Note: If you have a large amount of chat data you should only select a subset of your data to avoid longer load times for certain tasks

This project is made up of 9 tasks shown in the above diagram.

Specific Task Requirements:

wordcloud
- `facebook_name` parameter should be changed to your name on facebook

photo_mosaic
- `user_data` parameter should be set to name of the folder with the chat data (usually looks like FriendName_chatId)

link_chart_race
- Requires `ImageMagick` to be installed, link: link: https://imagemagick.org/

youtube_playlists
- Requires a YouTube Channel
- Requires Google's OAuth 2.0 authorisation credentials, more details here: https://developers.google.com/youtube/v3/guides/auth/client-side-web-apps
- Once you have the credentials, add them to the `sample_secrets` folder and rename the file to `client_secrets`, rename `sample_secrets` folder to `secrets`
- `user` parameter should be set to name of the folder with the chat data (usually looks like FriendName_chatId)


SAYN uses 2 key files to control the project:
  - settings.yaml: individual settings which are not shared
  - project.yaml: project settings which are shared across all collaborators on the project

SAYN code is stored in 3 main folders:
  - tasks: where the SAYN tasks are defined. Each YAML file in this folder represents a task group.
  - sql: code for SQL tasks
  - python: code for python tasks

SAYN uses some key commands for run:
  - sayn run: run the whole project
    - -p flag to specify a profile when running sayn: e.g. sayn run -p prod
    - -t flag to specify tasks to run: e.g. sayn run -t task_name
    - -t group:group_name to specify a task group to run: e.g. sayn run -t group:group_name
  - sayn compile: compiles the code (similar flags apply)
  - sayn --help for full detail on commands
