# Description
**YoutubeToMp3Fetcher** is a command line utility to download all audios from youtube video playlist and convert them to mp3. It uses youtube API, so to work with this script you need api-key (You can get one from there: https://console.developers.google.com). It also do not creates duplicates of audios, if the same working directory will be specified all files will be synced and script will download and convert only new files in specified playlist.

## Dependencies
Python package dependencieas are listed in 'requirements.txt'. To install it just use 'pip'

```bash
pip install -r requirements.txt
```

The 'pydub' package requires **[ffmpeg](http://www.ffmpeg.org/) or 
[libav](http://libav.org/)** to be installed

Mac (using [homebrew](http://brew.sh)):

```bash
# libav
brew install libav --with-libvorbis --with-sdl --with-theora

####    OR    #####

# ffmpeg
brew install ffmpeg --with-libvorbis --with-ffplay --with-theora
```

Linux (using aptitude):

```bash
# libav
apt-get install libav-tools libavcodec-extra-53

####    OR    #####

# ffmpeg
apt-get install ffmpeg libavcodec-extra-53
```

Windows:

1. Download and extract libav from [Windows binaries provided here](http://builds.libav.org/windows/).
2. Add the libav `/bin` folder to your PATH envvar
3. `pip install pydub`

Information about **ffmpeg and libav** was taken from [pydub](https://github.com/jiaaro/pydub) official github page. You can chek it for more information.

## Usage

Required arguments:

* -k --key : mandatory to access Youtube's data API. You can get one from there: https://console.developers.google.com
* -p --playlist | -s --single : youtube playlist id or video id.

To display the full list of supported arguments, use '-h' or '--help'.

```bash
python youtubesync.py -h
usage: youtubesync.py [-h] -k KEY [-p PLAYLIST | -s SINGLE] [-f FOLDER] [-a ALBUM] [-q | -v | -d]

This script finds all videos from Youtube given playlist, downloads it and converts to mp3.

arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Google Data API key.
  -p PLAYLIST, --playlist PLAYLIST
                        Youtube playlist id to get videos from
  -s SINGLE, --single SINGLE
                        Youtube video id to download
  -f FOLDER, --folder FOLDER
                        Working directory, where to download and store files,
                        absolute path
  -a ALBUM, --album     Album name to save tracks with, also makes sync only with album if exist
  -q, --quiet           Print out minimum result information, errors
  -v, --verbose         Print out detailed information about work progress
  -d, --debug           Print out all messages and details
```

## Example

Download all audios from videos from given playlist to specified folder.

```bash
python youtubesync.py -k ... -p PLblLnDz3Peug_HDuo1mbRrqwCOl1ABa13 -f 'C:\folder\to\download' -a from_youtube -v
```

```bash
python youtubesync.py -k ... -v TpIdb1ErbKk -f 'C:\folder\to\download' -v
```
