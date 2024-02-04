import sys
from urllib.parse import urlparse
import os
import queue
import threading
from io import BytesIO
from ds_store import DSStore
import requests
import argparse


class Scanner(object):
    def __init__(self, start_url):
        self.queue = queue.Queue()
        self.queue.put(start_url)
        self.processed_url = set()
        self.lock = threading.Lock()
        self.working_thread = 0
        self.dest_dir = os.path.abspath('.')

    def is_valid_name(self, entry_name):
        if entry_name.find('..') >= 0 or \
                entry_name.startswith('/') or \
                entry_name.startswith('\\') or \
                not os.path.abspath(entry_name).startswith(self.dest_dir):
            try:
                print('[ERROR] Invalid entry name: %s' % entry_name)
            except Exception as e:
                pass
            return False
        return True

    def process(self):
        while True:
            try:
                url = self.queue.get(timeout=2.0)
                self.lock.acquire()
                self.working_thread += 1
                self.lock.release()
            except Exception as e:
                if self.working_thread == 0:
                    break
                else:
                    continue
            try:
                if url in self.processed_url:
                    continue
                else:
                    self.processed_url.add(url)
                base_url = url.rstrip('.DS_Store')
                if not url.lower().startswith('http'):
                    url = 'http://%s' % url
                schema, netloc, path, _, _, _ = urlparse(url, 'http')
                try:
                    response = requests.get(url, allow_redirects=False)
                except Exception as e:
                    self.lock.acquire()
                    print('[ERROR] %s' % str(e))
                    self.lock.release()
                    continue

                if response.status_code == 200:
                    folder_name = netloc.replace(':', '_') + '/'.join(path.split('/')[:-1])
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    with open(netloc.replace(':', '_') + path, 'wb') as outFile:
                        self.lock.acquire()
                        print('[%s] %s' % (response.status_code, url))
                        self.lock.release()
                        outFile.write(response.content)
                    if url.endswith('.DS_Store'):
                        ds_store_file = BytesIO()
                        ds_store_file.write(response.content)
                        d = DSStore.open(ds_store_file)

                        dirs_files = set()
                        for x in d._traverse(None):
                            if self.is_valid_name(x.filename):
                                dirs_files.add(x.filename)
                        for name in dirs_files:
                            if name != '.':
                                self.queue.put(base_url + name)
                                if len(name) <= 4 or name[-4] != '.':
                                    self.queue.put(base_url + name + '/.DS_Store')
                        d.close()
            except Exception as e:
                self.lock.acquire()
                print('[ERROR] %s' % str(e))
                self.lock.release()
            finally:
                self.working_thread -= 1

    def scan(self):
        all_threads = []
        for i in range(10):
            t = threading.Thread(target=self.process)
            all_threads.append(t)
            t.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', help='Example: --domain https://www.example_site.com/.DS_Store')
    parser.add_argument('--list', help='Example: --list list_to_check.txt')
    args = parser.parse_args()
    single_domain = args.domain
    list_domains = args.list

    if single_domain:
        s = Scanner(f'https://{single_domain}/.DS_Store')
        s.scan()

    elif list_domains:
        with open(list_domains, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
        for url in urls:
            s = Scanner(f'https://{url}/.DS_Store')
            s.scan()
    else:
        print('.DS_Store Recursive File Downloader by zw1tt3r1on')
        print('')
        print('Usage: python ds_store_rfd.py --domain https://www.example_site.com/')
        print('Usage: python ds_store_rfd.py --list list_to_check.txt')
        sys.exit(0)
