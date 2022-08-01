import time
from flask import render_template, redirect, request, jsonify
from app import app
from app.forms import video as formVideo
import clipplexAPI

@app.route("/")
def home():
    return redirect("/instant_video.html")

@app.route("/instant_snapshot.html", methods=["GET"])
def instant_snapshot():
    return render_template("instant_snapshot.html", title="Instant Snapshot", images=clipplexAPI.Utils.get_images_in_folder())

@app.route("/get_instant_snapshot", methods=["GET"])
def get_instant_snapshot():
    server_data = clipplexAPI.ServerInfo("jonike") #DEBUG
    snapshot = clipplexAPI.Snapshot(server_data.media_path, server_data.current_media_time_str, server_data.media_fps)
    snapshot._download_frames()
    return "Files downloaded"

@app.route("/get_current_stream", methods=["GET", "POST"])
def get_current_stream():
    username = request.args.get("username")
    try:
        server = clipplexAPI.ServerInfo(username)
    except:
        return {"message": f"No session running for user {username}"}
    return {"file_path": str(server.media_path), "username": username, "current_time": server.current_media_time_str, "media_title": server.media_title}

@app.route("/instant_video.html", methods=["GET"])
def timed_video():
    form = formVideo()
    return render_template("instant_video.html", form=form, title="Instant Video", videos=clipplexAPI.Utils.get_videos_in_folder())

@app.route("/create_video", methods=["POST"])
def create_video():
    args = request.args
    _pad_time = clipplexAPI.Utils()._pad_time
    start = f"{_pad_time(args.get('start_hour'))}:{_pad_time(args.get('start_minute'))}:{_pad_time(args.get('start_second'))}"
    end = f"{_pad_time(args.get('end_hour'))}:{_pad_time(args.get('end_minute'))}:{_pad_time(args.get('end_second'))}"
    result = get_instant_video(args.get('username'), start, end)
    return jsonify(result)

def get_instant_video(username, start, end):
    server_data = clipplexAPI.ServerInfo(username)
    clip_time = clipplexAPI.Utils().calculate_clip_time(start, end)
    media_name = server_data.media_title.replace(" ", "")
    file_name = f"{username}_{media_name}_{int(time.time())}"
    current_media_time = server_data.current_media_time_str
    print(f"Creating video of {clip_time} seconds starting at {start} for user {username} for file {server_data.media_path}")
    video = clipplexAPI.Video(server_data, start, clip_time, file_name)
    video.extract_video()
    return {"result":"success"}

@app.route("/quick_add_time_to_start_time", methods=["POST"])
def quick_add_time_to_start_time():
    start_time = request.args.get("start_time")
    time_to_add = int(request.args.get("time_to_add"))
    return clipplexAPI.Utils().add_time(start_time, time_to_add)

@app.route("/remove_file", methods=["POST"])
#@login_required
def remove_file():
    video_path = request.args.get("file_path")
    if clipplexAPI.Utils().delete_file(video_path):
        return redirect("/instant_video.html")
    else:
        return "Problem downloading the file"

@app.route("/streamable_upload", methods=["POST"])
def streamable_upload():
    file_path = request.args.get("file_path")
    upload = clipplexAPI.Utils().streamable_upload(file_path)
    return upload

@app.route("/login.html", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/signin", methods=["POST"])
def signin():
    token = request.get_json()['token']
    valid_login, user_details, user_group = check_credentials(token=token)
    print(valid_login, user_details, user_group)

def check_credentials(token=None):
    """Verifies credentials for username and password.
    Returns True and the user group on success or False and no user group"""
    plex_login = plex_user_login(token=token)
    
    if plex_login is not None:
        return True, plex_login[0], plex_login[1]