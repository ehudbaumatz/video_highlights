from __future__ import unicode_literals

import Queue
import collections
import subprocess
import os
import threading

import time
from flask import Flask

from moviepy.editor import VideoFileClip
import posixpath
import urlparse
# import video2gif

def produce_snips_input_data(video, queue, sentinel, stride):
    '''
    Function to generate sniplets that serve as input to the network
    @return:
    '''
    frames=[]
    for frame_idx, f in enumerate(video.iter_frames()):
        frames.append(f)

        if len(frames)==16: # Extract scores
            # snip = model.get_snips(frames,snipplet_mean,0,True)
            # queue.put((frame_idx,snip))
            frames=frames[stride:] # shift by 'stride' frames

    queue.put(sentinel)

thread = threading.Thread(target=produce_snips_input_data, args=(1, 2, 3, 4))
thread.daemon = True


start=time.time()
thread.start()

thread.join()
print '10'

# import youtube_dl
#
# MIN=2
# class HighlightMeter(object):
#     def __init__(self, score_function):
#         self.score_function = score_function
#
#     def get(self, filename, shot_path, name, time = 5):
#
#         video = VideoFileClip(filename)
#
#         # extract shot boundry
#         shots = [(int(line.split(' ')[0]), int(line.split(' ')[1])) for line in open(shot_path)]
#         shot2segments = collections.OrderedDict()
#         for shot in shots:
#              if shot[1] - shot[0] < MIN * video.fps:
#                 print 'skipped (%d,%d)' % (shot[0], shot[1])
#                 continue
#
#              time = min(time*video.fps, shot[1] - shot[0])
#              segments = range(shot[0], shot[1]-int(time*video.fps), int(video.fps) )
#              shot2segments[shot] =  segments
#              print segments, shot, time
#
#         print 'shot2segments=' +  str(shot2segments)
#         segment2scores = video2gif.get_shot_top_scores(self.score_function,shot2segments, video)
#         print 'segment2scores=' +  str(shot2segments)
#
#         OUT_DIR = '/home/ubuntu/data/tmp/gifs'
#
#         good_gifs, bad_gifs = video2gif.generate_gifs(OUT_DIR, segment2scores, video, name, top_k=6, bottom_k=0)
#         #        mosaics = video2gif.generate_mosaic(OUT_DIR, scores, video, videoid, 480, 853)
#         print good_gifs, bad_gifs
#
#     def youtube_dl(self, url, path):
#         ydl_opts = {'format': 'best[height=480]+best[ext=mp4]/best', 'outtmpl': path}
#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])
#
#     def get_snips_scores(self, predict, video, stride=8):
#         '''
#         Predict scores for segments using threaded loading
#         (see https://github.com/Lasagne/Lasagne/issues/12#issuecomment-59494251)
#
#         NOTE: Segments shorter than 16 frames (C3D input) don't get a prediction
#
#         @param predict: prediction function
#         @param video: moviepy VideoFileClip
#         @param stride: stride of the extraction (8=50% overlap, 16=no overlap)
#         @return: dictionary key: frameidx -> value: score
#         '''
#
#         queue = Queue.Queue(maxsize=50)
#         sentinel = object()  # guaranteed unique reference
#
#         def produce_input_data():
#             '''
#             Function to generate sniplets that serve as input to the network
#             @return:
#             '''
#             frames=[]
#
#             for frame_idx, f in enumerate(video.iter_frames()):
#                 frames.append(f)
#
#                 if len(frames)==16: # Extract scores
#                     snip = model.get_snips(frames,snipplet_mean,0,True)
#                     queue.put((frame_idx,snip))
#                     frames=frames[stride:] # shift by 'stride' frames
#
#             queue.put(sentinel)
#
#         def get_input_data():
#             '''
#             Iterator reading snipplets from the queue
#             @return: (segment,snip)
#             '''
#             # run as consumer (read items from queue, in current thread)
#             item = queue.get()
#             while item is not sentinel:
#                 yield item
#                 queue.task_done()
#                 item = queue.get()
#
#
#         # start producer (in a background thread)
#         thread = threading.Thread(target=produce_input_data)
#         thread.daemon = True
#
#
#         start=time.time()
#         thread.start()
#         print('Score segments...')
#
#         snips = {}
#         max = 0
#         for frame_idx,snip in get_input_data():
#             scores=predict(snip)
#             snips[frame_idx] = scores
#             if max < frame_idx: max = frame_idx
#
#         print("Extracting scores for %d frames took %.3fs" % (max,time.time()-start))
#         return snips
#
#
# if __name__ == '__main__':
#     meter = HighlightMeter(video2gif.get_prediction_function())
#     meter.get('/Users/baumatz/Downloads/highlights/Uq59nbEa0yo.mp4', '/Users/baumatz/Downloads/highlights/Uq59nbEa0yo_shots.txt', 'Uq59nbEa0yo')

