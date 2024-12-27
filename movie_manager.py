import os
import re
import ffmpeg

def extract_year(movie_string):
    # Regular expression to match the year, handling both formats
    match = re.search(r'\((\D*(\d{4}))\)', movie_string)
    if match:
        return match.group(2)
    return None

class Movie:
    length_of_parameters = 3

    def __init__(self, name, resolution, file_size, external_subtitles=False):
        if name.__contains__('['):
            self.name = name.split('[')[0].strip()
        else:
            self.name = name
        self.resolution = resolution
        self.file_size = file_size
        self.external_subtitles = external_subtitles

    def __str__(self):
        return f"{self.name} {self.resolution} {self.file_size} ({self.external_subtitles})"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        if isinstance(other, Movie):
            return self.name == other.name and self.resolution == other.resolution and self.external_subtitles == other.external_subtitles and self.file_size == other.file_size
        return False
    
    def list(self):
        return [self.name, self.resolution, self.size, "x" if self.external_subtitles else ""]
    
    def get_name(self):
        return self.name.split("(")[0].strip()
    
    def get_year(self):
        print(extract_year(self.name))
        return int(extract_year(self.name))
        
    def get_resolution(self):
        return self.resolution
    
    def get_file_size(self):
        return self.file_size

video_extensions = (".mp4", ".mkv", "webm", ".ts", ".ogg")
subtitle_extensions = (".en", ".default", ".fr", ".de", ".german", ".srt")

class MovieManager:
    def __init__(self, directories=[]):
        self.movie_directories = directories
        self.movie_list = []
        self.subtitle_list = []

    def get_movie_list(self):
        return self.movie_list
    
    def get_video_data(self, file_path):
        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        size_bytes = os.path.getsize(file_path)
        size_gb = size_bytes / (1024 ** 3)  # Convert size to gigabytes
        return video_stream['width'], video_stream['height'], size_gb
    
    @staticmethod
    def remove_extensions(word, extensions):
        for item in extensions:
            word = word.replace(item, "")
        return word

    def process_files(self):
        for directory in self.movie_directories:
            for root, dirs, files in os.walk(directory):
                if 'extras' in dirs:
                    dirs.remove('extras')  # Skip directories named 'extras'
                for file in files:
                    if file.endswith(video_extensions):
                        width, height, size_gb = self.get_video_data(os.path.join(root, file))
                        file = self.remove_extensions(file, video_extensions)
                        resolution = width, height
                        self.movie_list.append(Movie(file, resolution, size_gb))
                    elif file.endswith(".srt"):
                        file = self.remove_extensions(file, subtitle_extensions)
                        self.subtitle_list.append(file)

        for subtitle in self.subtitle_list:
            for movie in self.movie_list:
                if subtitle in movie.name:
                    movie.external_subtitles = True