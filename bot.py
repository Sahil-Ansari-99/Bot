from PIL import Image
import io
import base64
import json
import urllib.request
import numpy as np


class Bot:
    def __init__(self):
        self.HEADER = 64
        self.FORMAT = 'utf-8'
        self.PIC_FORMAT_START = 'P!C'
        self.PIC_FORMAT = '$P!C'
        self.OMDb_KEY = '664efff4'
        self.MOVIE_FORMAT = '!MOVIE'
        self.COMPRESS_FORMAT = '!COMPRESS'
        self.function_map = {self.PIC_FORMAT: self.process_image,
                             self.MOVIE_FORMAT: self.get_movie_details,
                             self.COMPRESS_FORMAT: self.compress_image}

    def process_message(self, msg):
        if msg.startswith(self.PIC_FORMAT_START):
            msg_split = msg.split()
            img_size = msg_split[1]
            return f'GOT SIZE {img_size}'
        if msg.startswith(self.PIC_FORMAT):
            self.process_image(msg, self.PIC_FORMAT)
        if msg.startswith(self.MOVIE_FORMAT):
            return self.function_map.get(self.MOVIE_FORMAT)(msg)
        if ms.startswith(self.COMPRESS_FORMAT):
            return self.function_map.get(self.COMPRESS_FORMAT)(msg)
        return 'RECEIVED'

    def process_image(self, pic, form):
        pic_ = pic[len(form)+1:]
        pic_bytes = io.BytesIO(base64.b64decode(pic_))
        img = Image.open(pic_bytes)
        return img

    def get_movie_details(self, movie):
        movie_ = movie[len(self.MOVIE_FORMAT)+1:]
        movie_arr = movie_.split()
        movie_ = ""
        movie_ += movie_arr[0]
        for i in range(1, len(movie_arr)):
            movie_ += '+'
            movie_ += movie_arr[i]
        print(movie_)
        url = f'http://www.omdbapi.com/?t={movie_}&apikey=664efff4'
        data = json.loads(urllib.request.urlopen(url).read())
        if data['Response'] == 'False':
            return 'Please check spelling'
        return self.build_movie_rating(data)

    def build_movie_rating(self, data):
        attr_list = ['Title', 'Released', 'Runtime', 'Genre', 'Actors', 'Plot', 'Awards', 'imdbRating']
        res = ""
        for obj in attr_list:
            res += obj + ': '
            res += data[obj]
            res += '\n'
        return res

    def compress_image(self, msg):
        img = self.process_image(msg, self.COMPRESS_FORMAT)
        w, h, d = img.shape
        x = img.reshape((w*h), d)
        k = 20
        colors = self.find_k_means(x, k, 20)
        idx = self.find_closest_centroids(x, colors)
        idx = np.array(idx, dtype=np.uint8)
        x_reconstructed = np.array(colors[idx, :] * 255, dtype=np.uint8).reshape((w, h, d))
        img_compressed = Image.fromarray(x_reconstructed)
        return img_compressed

    def init_K_centroids(self, x, k):
        m = len(x)
        return x[np.random.choice(m, k, replace=False), :]

    def find_closest_centroids(self, x, centroids):
        m = len(x)
        c = np.zeros(m)
        for i in range(m):
            dist = np.linalg.norm(x[i] - centroids, axis=1)
            c[i] = np.argmin(dist)
        return c

    def compute_means(self, x, idx, k):
        _, n = x.shape
        centroids = np.zeros((k, n))
        for i in range(k):
            ex = x[np.where(idx == i)]
            mean = [np.mean(column) for column in ex.T]
            centroids[i] = mean
        return centroids

    def find_k_means(self, x, k, max_iters):
        centroids = self.init_K_centroids(x, k)
        previous_centroids = centroids
        for itr in range(max_iters):
            idx = self.find_closest_centroids(x, centroids)
            centroids = self.compute_means(x, idx, k)
            if (centroids == previous_centroids).all():
                return centroids
            else:
                previous_centroids = centroids
        return centroids