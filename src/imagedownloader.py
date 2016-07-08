#!/usr/bin/env python3
import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk, GObject
import requests
from urllib.parse import unquote_plus
import re
import os
import glob
from os.path import basename
from progreso import Progreso
from doitinbackground import DoitInBackground


GObject.threads_init()

NUM_THREADS = 10


EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg']

MAXDOWNLOADS = 5


def download_file(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def name_file(imgUrl):
    fileName = unquote_plus(unquote_plus(unquote_plus(basename(imgUrl))))
    if os.path.exists(fileName):
        base, ext = os.path.splitext(fileName)
        nfiles = len(glob.glob(base+'*'+ext))
        fileName = base+'_'+str(nfiles)+ext
    return fileName


def get_image_urls(mainurl):
    if not mainurl.lower().startswith('http://') and not\
            mainurl.lower().startswith('https://'):
        mainurl = 'http://%s' % mainurl
    print('Downloading from %s...' % mainurl)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS \
X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 \
Safari/537.36'
        }
    response = requests.get(url=mainurl, headers=headers)
    if response.status_code == 200:
        urlContent = response.content.decode()
        imgUrls = re.findall(
            '<img .*?src=[\',"](.*?)[\',"]',
            urlContent,
            re.IGNORECASE)
        imgUrls2 = re.findall(
            '<a .*?href=[\',"](.*?)[\',"]',
            urlContent,
            re.IGNORECASE)
        for imgUrl in imgUrls2:
            if imgUrl not in imgUrls:
                ext = os.path.splitext(imgUrl)[1]
                if ext.lower() in EXTENSIONS:
                    imgUrls.append(imgUrl)
        return imgUrls
    else:
        print('Error: ', response.status_code)
    return []


class SL(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(
            self,
            'Image Downloader',
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(400, 100)
        self.set_title('Image Downloader')
        self.connect('destroy', self.close_application)
        #
        vbox0 = Gtk.VBox(spacing=10)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        #
        table1 = Gtk.Table(2, 2, False)
        vbox0.add(table1)
        #
        label11 = Gtk.Label('Url:')
        label11.set_alignment(0, 0.5)
        table1.attach(label11, 0, 1, 0, 1)
        #
        self.entry11 = Gtk.Entry()
        table1.attach(self.entry11, 1, 2, 0, 1)
        #
        self.button = Gtk.Button('Select folder')
        self.button.connect('clicked', self.on_button_clicked)
        table1.attach(self.button, 0, 2, 1, 2)
        #
        self.show_all()

    def close_application(self, widget, event, data=None):
        exit(0)

    def on_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            "Select folder",
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
             Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        filter = Gtk.FileFilter()
        filter.set_name("Folder")
        filter.add_pattern("*")  # whats the pattern for a folder
        dialog.add_filter(filter)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            dialog.hide()
            self.button.set_label(dialog.get_filename())
        dialog.destroy()


def main():
    sl = SL()
    if sl.run() == Gtk.ResponseType.ACCEPT:
        sl.hide()
        if sl.button.get_label() != 'Select folder':
            folder = sl.button.get_label()
            url = sl.entry11.get_text()
            if len(url) > 0:
                urls = get_image_urls(url)
                total = len(urls)
                if total > 0:
                    p = Progreso('Prueba', None, len(urls))
                    dib = DoitInBackground(urls, folder)
                    dib.connect('started_one', p.set_start_one)
                    dib.connect('finished_one', p.increase)
                    dib.connect('finished', p.close)
                    dib.connect('stopit', p.close)
                    dib.start()
                    p.run()


if __name__ == '__main__':
    main()
