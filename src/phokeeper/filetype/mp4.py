from hachoirreader import *

class MP4:
    '''Classe que controla informacoes relativas ao tratamento de mp4s'''
    extensions = ('mp4','mpeg4')
    parsers = (HachoirGenericReader,)
    prefered = 0
