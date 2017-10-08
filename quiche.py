import pickle
import hashlib
import zlib
import time
import functools


class Quiche(object):
    """
    A caching utility
    """

    def __init__(self, filename, lifetime=3600):
        """
        :param filename: Filename of the cache file (create the file if doesn't exist)
        :param lifetime: Lifetime in seconds of a cached element (default is 1 hours)
        """
        self.filename = filename
        self.lifetime = lifetime

        # Read the cache file or create one blank.
        try:
            self.cache = self._read_cache()
        except FileNotFoundError:
            self.cache = []
            self._write_cache(self.cache)

    def _write_cache(self, cache):
        """
        Write cache in the file.
        """
        with open(self.filename, 'wb') as cache_file:
            data = zlib.compress(pickle.dumps(cache))
            cache_file.write(data)

    def _read_cache(self):
        """
        Read the content of the cache file.
        """
        with open(self.filename, 'rb') as cache_file:
            data = cache_file.read()

        return pickle.loads(zlib.decompress(data))

    @staticmethod
    def _get_checksum(function, args):
        """
        Get the checksum of a function for a given arg.
        """
        id_key = str(function.__code__.co_code) + str(pickle.dumps(args))
        return hashlib.sha1(id_key.encode('utf-8')).digest()

    def save(self):
        """
        Save the cache and clean expired element.
        :return: the updated cache
        """

        # Clean expired element
        new_cache = []
        for element in self.cache:
            if element['expire_date'] > time.time():
                new_cache.append(element)

        # Update and save the new cache
        self.cache = new_cache
        self._write_cache(self.cache)

        return self.cache

    def cached(self, function):
        """
        Run the function on cache.
        """

        @functools.wraps(function)
        def wrapper(*args):
            # Get hashed function id and args.
            checksum = self._get_checksum(function, args)

            # Check if the result is cached.
            for element in self.cache:
                if element['checksum'] == checksum and element['expire_date'] > time.time():
                    self.save()
                    return element['result']

            # If not cached, run the function and save the result on the cache.
            result = function(*args)

            self.cache.append({
                'checksum': checksum,
                'result': result,
                'expire_date': time.time() + self.lifetime
            })

            self.save()
            return result

        return wrapper
