from __future__ import unicode_literals

import ConfigParser
import collections
import os

from flask import Flask
from flask_restful import Api, Resource, reqparse
from moviepy.editor import VideoFileClip

import highlights
from highlights.scene_segmenter import SceneSegmenter

app = Flask(__name__)
api = Api(app)

import youtube_dl

MIN=2
# Load the configuration
config=ConfigParser.SafeConfigParser()
print('Loaded config file from %s' % config.read('%s/config.ini' % os.path.dirname(__file__))[0])
class HighlightMeter(Resource):
    def __init__(self, **kwargs):
        self.score_function = kwargs['score_function']
        self.scene_segmenter = SceneSegmenter()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('time', type=int)
        self.parser.add_argument('url', required=True)

    def get(self):
        args = self.parser.parse_args()
        url = args.get('url')
        time = args.get('time')
        if not time: time = 5

        name = url.split('=')[1]
        filename = os.path.join(config.get('paths', 'temp'), name + '.mp4')
        self.youtube_dl(url, filename)
        print url, filename

        video = VideoFileClip(filename)
        video.d
        scenes = self.scene_segmenter.get_scene_boundaries(video, filename, name)

        shot2segments = collections.OrderedDict()
        for scene in scenes:
             if scene[1] - scene[0] < MIN * video.fps:
                print 'skipped (%d,%d)' % (scene[0], scene[1])
                continue

             time = min(time*video.fps, scene[1] - scene[0])
             segments = range(scene[0], scene[1]-int(time*video.fps), int(video.fps) )
             shot2segments[scene] =  segments
             print segments, scene, time

        print 'shot2segments=' +  str(shot2segments)
        segment2scores = highlights.get_shot_top_scores(self.score_function, shot2segments, video)
        print 'segment2scores=' +  str(shot2segments)

        OUT_DIR = '/home/ubuntu/data/tmp/gifs'

        good_gifs, bad_gifs = highlights.generate_gifs(OUT_DIR, segment2scores, video, name, top_k=6, bottom_k=0)
        #        mosaics = video2gif.generate_mosaic(OUT_DIR, scores, video, videoid, 480, 853)
        print good_gifs, bad_gifs

    def youtube_dl(self, url, path):
        ydl_opts = {'format': 'best[height=480]+best[ext=mp4]/best', 'outtmpl': path}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

api.add_resource(HighlightMeter, '/highlight', resource_class_kwargs={ u'score_function': highlights.get_prediction_function()})

if __name__ == '__main__':
    HighlightMeter()
    # app.run()