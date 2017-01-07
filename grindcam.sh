#!/bin/bash

OUTFOLDER=${1:-.}
OUT="$OUTFOLDER"/$(date -u +"%Y-%m-%dT%H%M%S.mp4")

mplayer -benchmark ffmpeg://tcp://127.0.0.1:1234?listen > /dev/null &


ffmpeg -y -s 1280x720 -f avfoundation -video_device_index 0 -r 30 -i "default" \
	 -vf "drawtext=fontfile=DejaVuSansMono.ttf: text='%{localtime\:%F %T} f %{n}\\: pts=%{pts \\: hms}': fontcolor=white@0.8: x=7: y=7: box=1: boxcolor=black@0.7: fontsize=32" \
	 -vcodec h264 -preset ultrafast -pix_fmt yuv420p "$OUT" \
	 -flags +global_header -vcodec rawvideo -pix_fmt bgr24  -async 1 -allow_raw_vfw 1 -f matroska tcp://127.0.0.1:1234/

