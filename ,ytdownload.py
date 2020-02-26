#!/usr/bin/python

import re
import sys
from argparse import ArgumentParser
from os import chdir, getcwd, makedirs
from pathlib import Path

import youtube_dl
from bs4 import BeautifulSoup
from pyperclip import paste
from requests import get

singleVideoRegex = re.compile("youtu.be\/(.*)|v=(.*)")


def validLink(link):
    return "https://www.youtube.com/" in link or "https://youtu.be" in link


def singleVideo(link):
    res = singleVideoRegex.search(link)
    if res is None:
        return False
    if res.group(1) is not None:
        return len(res.group(1)) != 0
    if res.group(2) is not None:
        return len(res.group(2)) != 0


def parseArgs3():
    parser = ArgumentParser()
    parser.add_argument("link", nargs="?", help="link to download")
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="use this flag for audio-only extraction.",
    )
    return parser.parse_args()


def main():
    args = parseArgs3()
    searchLink = paste() if args.link is None else args.link

    if not validLink(searchLink):
        print(f"Pasted link:'{searchLink}' is not supported youtube link!")
    else:
        header = {
            "'User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
        }
        downloaded = get(searchLink, headers=header)
        downloaded.raise_for_status()

        if downloaded.status_code == 200:
            downloadLinks = []
            if singleVideo(searchLink):
                downloadLinks.append(searchLink)
            else:
                maxLinks = sys.argv[1] if len(sys.argv) > 1 else 5
                soup = BeautifulSoup(downloaded.text, "html.parser")
                links = soup.findAll("a", attrs={"aria-hidden": "true"})

                for index, link in enumerate(links):
                    downloadLink = f"https://www.youtube.com{link.get('href')}"
                    downloadLinks.append(downloadLink)
                    if index + 1 == maxLinks:
                        break
            if len(downloadLinks) != 0:
                outdir = f"{Path.home()}/Downloads/yt/"
                cwd = getcwd()
                makedirs(outdir, exist_ok=True)
                chdir(outdir)
                ydl_opts = {}
                if args.audio_only:
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }
                        ],
                    }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    for i, downloadLink in enumerate(downloadLinks):
                        print(f"downloading {i}/{len(downloadLinks)}")
                        ydl.download([downloadLink])
                chdir(cwd)


if __name__ == "__main__":
    main()
