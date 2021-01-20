ADX convertver + volume changer (Just a fancy batch script with some logging) by agilly1989
Inspiration: A fellow called Kuiriel on discord
Requires: no external libraries BUT needs
-- ffmpeg.exe 3.2.2 (or similar version - supplied in release)
-- radx_encode.exe and radx_decode.exe from https://github.com/Isaac-Lozano/radx (supplied in release)

Uses multithreading to use all it can to speed up everything, so the more cores, the *potentially* better