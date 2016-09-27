import ConfigParser
import os
import subprocess

import matplotlib.pyplot as plt
import numpy as np
import time
from lasagne.utils import floatX
from moviepy.video.io.VideoFileClip import VideoFileClip

import resnet50

plt.rcParams['figure.figsize'] = 8, 6
import skimage.transform
try:
    import lasagne
    import theano
except (ImportError,AssertionError) as e:
    print(e.message)

# Load the configuration
config=ConfigParser.SafeConfigParser()
print('Loaded config file from %s' % config.read('%s/config.ini' % os.path.dirname(__file__))[0])

class SceneSegmenter(object):


    def __init__(self):

        self.extractor_function, self.mean_value  = self.get_feature_extraction_function()
        self.shot_segmenter = config.get('paths', 'video_segmentation')

    def extract_features(self, images):

        start = time.time()
        images = [self.prep_image(image) for image in images] # need to paralleize
        print("Transforming images for %d iamges took %.3fs" % (len(images),time.time()-start))

        start = time.time()
        features = self.extractor_function(images)
        print("Extracting features for %d iamges took %.3fs" % (len(features),time.time()-start))
        return features

    def get_feature_extraction_function(self, feature_layer = 'fc1000'):

        '''
        Get feature extraction function
        @param feature_layer: a layer name (see resnet50.py).
        @return: theano function that extract features
        '''
        print('Load weights and compile model...')

        # Build model
        net=resnet50.build_model(batch_size=50)

        # Set the weights (takes some time)
        mean = resnet50.set_weights(net,config.get('paths','resnet_weight_file'))

        features = lasagne.layers.get_output(net[feature_layer], deterministic=True)
        features_fn = theano.function([net['input'].input_var], features, allow_input_downcast = True)

        return features_fn, mean

    def get_scene_boundaries(self, video, filename, name):

        #extract key freames from shots
        start = time.time()
        subprocess.call([self.shot_segmenter, filename])
        print("Extracting shots for %.3fs iamges took %.3fs" % (video.duration,time.time()-start))

         # extract shot boundry
        path = os.path.join(config.get('paths', 'temp'), name + '_shots.txt')

        shots = [line.split(' ') for line in open(path)]
        images = self.extract_keyframes(path, shots, video)

        return self.extract_features(images)

    def extract_keyframes(self, path, shots, video):
        images = []
        for i, shot in enumerate(shots):
            for j, frame in enumerate(shot[2:]):
                t = frame / video.fps
                dst = '%s/frame_%d.%d.jpeg' % (path, i, j)
                video.save_frame(dst, t)
                images.append(dst)

        return images

    def prep_image(self, fname):

        ext = fname.split('.')[-1]
        im = plt.imread(fname, ext)
        h, w, _ = im.shape
        if h < w:
            im = skimage.transform.resize(im, (256, w*256/h), preserve_range=True)
        else:
            im = skimage.transform.resize(im, (h*256/w, 256), preserve_range=True)
        h, w, _ = im.shape
        im = im[h//2-112:h//2+112, w//2-112:w//2+112]
        rawim = np.copy(im).astype('uint8')
        im = np.swapaxes(np.swapaxes(im, 1, 2), 0, 1)
        im = im[::-1, :, :]
        im = im - self.mean_value
        return rawim, floatX(im[np.newaxis])


def test(vid):
    import glob

    ss = SceneSegmenter()
    video = VideoFileClip(vid)

    features = ss.get_scene_boundaries(video, vid, os.path.basename(vid).split('.')[0])


    for feature in features:
        print feature

if __name__ == "__main__":
    from sys import argv
    test(argv[1], argv[2])




