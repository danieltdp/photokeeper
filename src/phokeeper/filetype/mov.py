from hachoirreader import *

class MOV:
    '''Classe que controla informacoes relativas ao tratamento de movs'''
    #TODO Implementar o leitor manual de MOVs
    extensions = ('mov',)
    parsers = (HachoirGenericReader,)
    prefered = 0
