#!/usr/bin/python

import re
from os import chdir, getcwd, makedirs
from pathlib import Path
from sys import argv

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


searchLink = paste()

if not validLink(searchLink):
    print(f"Pasted link:'{searchLink}' is not supported youtube link!")
else:
    header = {
        "'User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7"
    }
    downladed = get(searchLink, headers=header)
    downladed.raise_for_status()

    if downladed.status_code == 200:
        downloadLinks = []
        if singleVideo(searchLink):
            downloadLinks.append(searchLink)
        else:
            maxLinks = argv[1] if len(argv) > 1 else 5
            soup = BeautifulSoup(downladed.text, "html.parser")
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
            with youtube_dl.YoutubeDL() as ydl:
                for i, downloadLink in enumerate(downloadLinks):
                    print(f"downloading {i}/{len(downloadLinks)}")
                    ydl.download([downloadLink])
            chdir(cwd)