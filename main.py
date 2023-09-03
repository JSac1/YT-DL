import os
import shutil

import pytube
from pytube.cli import on_progress
import tkinter
import easygui
import moviepy.editor as mp
import music_tag

import threading

import ffmpeg
import requests

__version__ =  "v1.1"

root = tkinter.Tk()
root.title("YouTube-Downloader")
# icon = tkinter.PhotoImage(file="icon.png")
# root.iconphoto(False, icon)
root.geometry("300x170")

tkinter.Grid.rowconfigure(root, 0, weight=1)
tkinter.Grid.columnconfigure(root, 0, weight=3)

tkinter.Grid.rowconfigure(root, 2, weight=3)
tkinter.Grid.rowconfigure(root, 1, weight=1)
tkinter.Grid.rowconfigure(root, 3, weight=3)
tkinter.Grid.rowconfigure(root, 4, weight=3)
tkinter.Grid.rowconfigure(root, 5, weight=3)
tkinter.Grid.rowconfigure(root, 6, weight=3)
tkinter.Grid.rowconfigure(root, 7, weight=3)


def mode_select(url, audio_only=False, save_as_webm=False, download_progressive=False):

    modeSelect(url, audio_only, save_as_webm, download_progressive)

def help_message():
    easygui.msgbox(title="Help", ok_button="Back", msg="""Put a YouTube video URL and click download. YouTube Playlist also supported. Videos downloaded from a playlist are placed on a separate folder. If a video is age-restricted, you will be prompted to allow the application to use your account (Oauth) to download the video.

Options:
Audio Only - Downloads the audio of the video only.
Save as WEBM - Download the video/audio in their original format.
Use Progressive streams - Downloads a already processed video. Does not work with Audio Only.


Progressive vs Adaptive Streams
Adaptive Streams separates the video and the audio of the stream. They usually are high quality. Using this is slow since the files are manually merged.

Progressive streams are already processed streams that usually only supports 720p and 360p with a lower quality. Using this is fast since it's already processed
""")

class modeSelect:
    def __init__(self, url, audio_only, save_as_webm, download_progressive):
        audio_only = audio_only.get()
        url = url.get()
        save_as_webm = save_as_webm.get()
        download_progressive = download_progressive.get()

        if not audio_only:
            if download_progressive:
                accepted_res = easygui.choicebox(title="Resolution Priority", msg="Pick your desired resolution",
                                                 choices=["720p", "360p", ])
            else:
                accepted_res = easygui.choicebox(title="Resolution Priority", msg="Pick your desired resolution",
                                                 choices=["1080p", "720p", "480p", "360p", "240p", "144p"])

            if accepted_res is None:
                return

        def download_video(video, save_as_webm, output="Videos"):
            # accepted_res = easygui.choicebox(title="Resolution Priority", msg="Pick your desired resolution", choices=["1080p", "720p", "480p", "360p", "240p", "144p"])
            def on_prog(a, b, c):
                print(a.title + f"({a.type})" + ":", str(((a.filesize / 1000000) - (c / 1000000)) / (
                        a.filesize / 1000000)) + f"   | {((a.filesize / 1000000) - (c / 1000000))}/{a.filesize / 1000000}")

            # video = pytube.YouTube(url, on_progress_callback=on_prog, use_oauth=False, allow_oauth_cache=True)
            print(video.title)
            streams = video.streams
            v_streams = []
            a_streams = []
            for stream in streams.filter(progressive=download_progressive,
                                         only_audio=True if not download_progressive else False,
                                         mime_type="audio/webm" if not download_progressive else "audio/mp4"):
                a_streams.append(stream)
            print("--------------------------")
            for stream in streams.filter(progressive=download_progressive,
                                         only_video=True if not download_progressive else False,
                                         mime_type="video/webm" if not download_progressive else "video/mp4",
                                         resolution=accepted_res):
                v_streams.append(stream)

            if len(v_streams) == 0:
                for stream in streams.filter(progressive=download_progressive,
                                             only_video=True if not download_progressive else False,
                                             mime_type="video/webm" if not download_progressive else "video/mp4"): v_streams.append(
                    stream)

            if not os.path.exists("cache"):
                os.mkdir("cache")

            for_download = []

            for stream in v_streams: print(stream)
            print("--------------------------")
            for stream in a_streams:
                print(stream)
            print("--------------------------")
            if not download_progressive:
                print(f"{v_streams[0]}\n{a_streams[-1]}")
            for_download.append(v_streams[0])
            if not download_progressive:
                for_download.append(a_streams[-1])

            def download(stream, output=None):
                if output is None:
                    output = f"cache\\{stream.title}"
                stream.download(output_path=output, filename=f"{stream.title}_{stream.type}.{stream.subtype}", max_retries=10)

            threads = []
            if not download_progressive:
                for stream in for_download:
                    threads.append(threading.Thread(target=download, args=(stream,)))

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                filename = for_download[0].title

                input_video = ffmpeg.input(
                    f'cache\\{for_download[0].title}\\{for_download[0].title}_video.{for_download[0].subtype}')

                input_audio = ffmpeg.input(
                    f'cache\\{for_download[0].title}\\{for_download[0].title}_audio.{for_download[0].subtype}')

                if not os.path.exists(output):
                    os.mkdir(output)

                if save_as_webm:
                    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
                        f'{output}\\{for_download[0].title}.webm').run()
                else:
                    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
                        f'{output}\\{for_download[0].title}.mp4').run()
            else:
                for stream in for_download:
                    download(stream, output)

            print("DONE")

        def download_audio(video, save_as_webm, output="Audios"):
            def on_prog(a, b, c):
                print(a.title + f"({a.type})" + ":", str(((a.filesize / 1000000) - (c / 1000000)) / (
                        a.filesize / 1000000)) + f"   | {((a.filesize / 1000000) - (c / 1000000))}/{a.filesize / 1000000}")

            # video = pytube.YouTube(url, on_progress_callback=on_prog, use_oauth=False, allow_oauth_cache=True)
            print(video.title)
            streams = video.streams
            a_streams = []
            for stream in streams.filter(adaptive=True, only_audio=True, mime_type="audio/webm"):
                a_streams.append(stream)

            if not os.path.exists("cache"):
                os.mkdir("cache")

            for_download = [a_streams[-1]]

            filename = for_download[0].title
            print(for_download)

            a_title: str = stream.title
            a_title = a_title.replace('"', '')
            a_title = a_title[:50]

            if not os.path.exists(f"cache\\{a_title}"):
                os.mkdir(f"cache\\{a_title}")

            def download(stream, output=None):
                if output is None:
                    output = f"cache\\{stream.title}"
                stream.download(output_path=output, filename=f"{stream.title}_{stream.type}.{stream.subtype}")

            thumbnail = requests.get(video.thumbnail_url)
            with open(f"cache\\{a_title}\\thumbnail.jpeg", "wb") as e:
                e.write(thumbnail.content)

            threads = []
            for stream in for_download:
                threads.append(threading.Thread(target=download, args=(stream,)))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            if not save_as_webm:
                clip = mp.AudioFileClip(fr"cache\{a_title}\{a_title}_audio.webm")

                if not os.path.exists(output):
                    os.mkdir(output)

                clip.write_audiofile(f"{output}\\{a_title}.mp3")

                f = music_tag.load_file(f"{output}\\{a_title}.mp3")

                f["artist"] = video.author
                f["title"] = video.title

                art = f["artwork"]

                with open(f"cache\\{a_title}\\thumbnail.jpeg", "rb") as img:
                    f["artwork"] = img.read()
                with open(f"cache\\{a_title}\\thumbnail.jpeg", "rb") as img:
                    f.append_tag('artwork', img.read())

                # art.first.thumbnail([64, 64])
                # art.first.raw_thumbnail([64, 64])

                f.save()
            else:
                shutil.move(f"cache\\{a_title}\\{a_title}_audio.webm", output)
                os.rename(f"{output}\\{a_title}_audio.webm", f"{output}\\{a_title}.webm")

            print("DONE")


        if "?list=" in url or "&list=" in url or "playlist" in url or "watch_videos?" in url:
            def on_prog(a, b, c):
                print(a.title + f"({a.type})" + ":", str(((a.filesize / 1000000) - (c / 1000000)) / (
                        a.filesize / 1000000)) + f"   | {((a.filesize / 1000000) - (c / 1000000))}/{a.filesize / 1000000}")
            playlist = pytube.Playlist(url,)
            urls = [link for link in playlist.video_urls]

            videos_l = []

            for url in urls:
                videos_l.append(pytube.YouTube(url, on_progress_callback=on_prog, use_oauth=True, allow_oauth_cache=True))

            videos_dict = {}
            videos = []

            for video in videos_l:
                videos_dict[str(video.title)] = video

            v_titles = [key for key in videos_dict.keys()]

            if len(v_titles) == 1:
                v_titles.append("------Placeholder------")
                choice = easygui.choicebox(title="Playlist", msg="Select videos to download", choices=v_titles, preselect=1000)
                videos_picked = [choice]
            else:
                videos_picked = easygui.multchoicebox(title="Playlist", msg="Select videos to download", choices=v_titles, preselect=1000)

            if videos_picked is None:
                return

            for v in videos_picked:
                videos.append(videos_dict[v])

            playlist_threads = []

            if not os.path.exists("Playlists"):
                os.mkdir("Playlists")

            if not audio_only:

                for video in videos:
                    download_video(video, save_as_webm, f"Playlists\\{playlist.title}")

                # for url in urls:
                #     playlist_threads.append(threading.Thread(target=download_video, args=(url,save_as_webm, f"Playlists\\{playlist.title}",)))
                #
                # for thread in playlist_threads:
                #     thread.start()
                #
                # for thread in playlist_threads:
                #     thread.join()
                print(f"FINISHED {playlist.title}")
            else:
                for video in videos:
                    download_audio(video, save_as_webm, f"Playlists\\{playlist.title}")
                #     playlist_threads.append(threading.Thread(target=download_audio, args=(url, f"Playlists\\{playlist.title}",)))
                #
                # for thread in playlist_threads:
                #     thread.start()
                #
                # for thread in playlist_threads:
                #     thread.join()
                print(f"FINISHED {playlist.title}")

        else:
            def on_prog(a, b, c):
                print(a.title + f"({a.type})" + ":", str(((a.filesize / 1000000) - (c / 1000000)) / (
                        a.filesize / 1000000)) + f"   | {((a.filesize / 1000000) - (c / 1000000))}/{a.filesize / 1000000}")
            video = pytube.YouTube(url, on_progress_callback=on_prog, use_oauth=True, allow_oauth_cache=True)
            if audio_only:
                download_audio(video, save_as_webm)
            else:
                download_video(video, save_as_webm)


audio_only = tkinter.BooleanVar()
save_as_webm = tkinter.BooleanVar()
download_progressive = tkinter.BooleanVar()
url = tkinter.StringVar()
title = tkinter.Label(root, text="YouTube URL")
title.grid(row=0, column=0, sticky="NSEW")
a = tkinter.Entry(root, textvariable=url)
a.grid(row=1, column=0, sticky="NSEW")
b = tkinter.Checkbutton(root, text="Audio Only", variable=audio_only, onvalue=True, offvalue=False)
b.grid(row=3, column=0, sticky="NSEW")
c = tkinter.Checkbutton(root, text="Save as WEBM", variable=save_as_webm, onvalue=True, offvalue=False)
c.grid(row=4, column=0, sticky="NSEW")
d = tkinter.Button(root, text="Download",
                   command=lambda: mode_select(url, audio_only, save_as_webm, download_progressive))
d.grid(row=2, column=0, sticky="NSEW")
e = tkinter.Checkbutton(root, text="Use Progressive streams", variable=download_progressive, onvalue=True,
                        offvalue=False)
e.grid(row=5, column=0, sticky="NSEW")
notice = tkinter.Label(root, text="Check console for progress")
notice.grid(row=7, column=0, sticky="NSEW")
help_b = tkinter.Button(root, text="Help", command=help_message)
help_b.grid(row=6, column=0, sticky="NSEW")

root.mainloop()
