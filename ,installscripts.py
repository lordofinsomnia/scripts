#!/usr/bin/python

from os import chmod, getcwd, listdir, remove, stat, symlink
from os.path import exists
from stat import S_IEXEC

for file in listdir(getcwd()):
    if ".py" in file:
        srcFile = f"{getcwd()}/{file}"
        destFile = f"/usr/bin/{file}"
        print(f"processing {file}")
        print("\tcreating symlink.")
        if exists(destFile):
            remove(destFile)
        symlink(srcFile, destFile)
        destFileStat = stat(destFile)
        print("\tmaking executable.")
        chmod(destFile, destFileStat.st_mode | S_IEXEC)
