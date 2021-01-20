ADX convertver + volume changer (Just a fancy batch script with some logging) by agilly1989

* Inspiration: A fellow called Kuiriel on discord
* Requires: no external libraries BUT needs
* -- ffmpeg.exe 3.2.2 (or similar version - supplied in release)
* -- radx_encode.exe and radx_decode.exe from https://github.com/Isaac-Lozano/radx (supplied in release)
* Written in Python 3.7.9 (but should be forward and back compatible with any Python 3.x)
* exe is made by pyinstaller and may false-positive your antivirus (I know it's triggered Windows Defender a few times)

Uses multithreading to use all it can to speed up everything, so the more cores, the *potentially* better

Usage:

Run it and it'll make "readme - part 2.md", open that as it has more instructions (made for your system)