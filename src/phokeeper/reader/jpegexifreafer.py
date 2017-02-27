from abstractreader import *

import datetime

import exifread

class JpegReaderExifReader(MetadataReader):
    '''Leitor que utiliza o pacote exifread para ler jpegs'''
    
    def __init__(self, filename):
        MetadataReader.__init__(self,filename)
        
    def parse(self):
        f = open(self.filename,'rb')
        keys = exifread.process_file(f,details=False)
        f.close()
        key = 'EXIF DateTimeOriginal'
        if key in keys:
            exif_date = keys[key]
            date_string = exif_date.values
            date_time = datetime.datetime.strptime(date_string,'%Y:%m:%d %H:%M:%S') 
            self.year = date_time.year
            self.month = date_time.month