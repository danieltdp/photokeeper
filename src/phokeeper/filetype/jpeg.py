from hachoirreader import *
from jpegreader import *

class JPEG:
    '''Classe que controla informacoes relativas ao tratamento de jpegs'''
    extensions = ('jpg','jpeg')
    parsers = (HachoirGenericReader, JpegReaderExifReader)
    prefered = 1