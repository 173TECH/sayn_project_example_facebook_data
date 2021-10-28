# SAYN Project Example: Facebook Data Analysis

## Project Description

This is an example [SAYN](https://173tech.github.io/sayn/) project. It shows you how to implement and use SAYN for data processing and modelling.

To run the project, you will need to:

- clone the repository with `git clone https://github.com/173TECH/facebook_data_project.git`.
- rename the `sample_settings.yaml` file to `settings.yaml`.
- install the project dependencies by running the `pip install -r requirements.txt` command from the root of the project folder.
- install `ImageMagick`, details here: https://imagemagick.org/
- use `sayn run` from the root of the project folder to run all SAYN commands.

After a successful run you should see 3 new files in `python/img`, these should be the following:
- sample_Goku_timelapse.gif
- sample_Vegeta_timelapse.gif
- chart_race.gif

## Using Your Own Data

For this you will need your Facebook Messenger data in JSON format, you can get request it by doing the following:
- Settings & Privacy > Settings > Your Facebook Information > Download Your Information 
- Change format to JSON and click Create File (this can take a while depending on your date range and media quality)

Once you have the data:
- You can find the chat data in `messages/inbox` (you should see a collection of folders corresponding to each of your chats).
- Copy and paste the chat folders you are interested into the `data` folder in this project.
- In `tasks/data_science.yaml`, change the `facebook_name` parameter to your full name on Facebook

Note: If you use a large amount of chat data you will experience longer load times for certain tasks

## DAG

![ETL](/dag.png)

This project is made up of 6 tasks shown in the above diagram.

## SAYN Quick Overview

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

For more details on SAYN, you can see:
* the [documentation](https://173tech.github.io/sayn/)
* the [tutorials](https://173tech.github.io/sayn/tutorials/tutorial_part1/)

