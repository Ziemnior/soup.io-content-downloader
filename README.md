Class `SoupDownloader` that provides functionality to download images from specified soup. 

To run it, call `python soup_io_downloader.py` and provide an url to soup (presumably yours or something)

To resume downloading from where you stopped last time, simply copy url from latest `downloading images from` log message and provide it as an argument.

In `Releases`, you can find executables for linux and windows systems, but I do not guarantee that it will work on your OS, as I did not test it 

This version retry mechanism was implemented, so if soup will go 503, the script will timeout for 30s and try again. After 10 failed attempt, it will terminate