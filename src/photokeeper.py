import datetime
import sys

# http://hachoir3.readthedocs.org/
import hachoir_parser
import hachoir_metadata
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename

# import exifread
# def get_exif_date(filename):
#     f = open(filename,'rb')
#     keys = exifread.process_file(f,details=False)
#     f.close()
#     exif_date = keys['EXIF DateTimeOriginal']
#     return exif_date.values
# def get_path(filename):
#     #exif_date = get_exif_date(filename)
#     #date_time = datetime.datetime.strptime(exif_date,'%Y:%m:%d %H:%M:%S')
#     date_time = get_exif_date(filename)
#     return '%d/%.2d'%(date_time.year, date_time.month)


def get_exif_date(filename):
    filename, realname = unicodeFilename(filename), filename
    parser = hachoir_parser.createParser(filename, realname)
    if not parser:
        print >>stderr, "Unable to parse file"
        exit(1)
    try:
        ## TODO Essa chamada da um warning quando nao ha gps data
        metadata = hachoir_metadata.extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
    if not metadata:
        print "Unable to extract metadata"
        exit(1)
    return metadata.get('creation_date')

def get_path(filename):
    date_time = get_exif_date(filename)
    return '%d/%.2d'%(date_time.year, date_time.month)

files = ('../../data/video.mp4','../../data/DSC_0003.JPG')
#filename = 'teste.jpg'
for filename in files:
    photo_path = get_path(filename)
    print '%s: %s'%(filename,photo_path)






# ----------------------
# testes
# -----------------------
# filename, realname = unicodeFilename(filename), filename
# parser = createParser(filename, realname)
# if not parser:
#     print >>stderr, "Unable to parse file"
#     exit(1)
# try:
#     ## TODO Essa chamada da um warning quando nao ha gps data
#     metadata = hachoir_metadata.extractMetadata(parser)
# except HachoirError, err:
#     print "Metadata extraction error: %s" % unicode(err)
#     metadata = None
# if not metadata:
#     print "Unable to extract metadata"
#     exit(1)
# for item in metadata:
#     sys.stdout.write('%s :: '%item.key)
#     for value in item.values:
#         sys.stdout.write('%s :: '%value.value)
#     sys.stdout.write('\n')
#metadata.get('creation_date')

#print dir(metadata)
#text = metadata.exportPlaintext()
#charset = getTerminalCharset()
#for line in text:
    #print makePrintable(line, charset)