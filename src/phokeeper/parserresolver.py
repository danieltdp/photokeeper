from filetypes import *
from abstractreader import *
from concretereaders import *

class ParserResolver:
    '''Classe responsavel por selecionar e instanciar o parser a ser utilizado
    para um determinado arquivo'''
    
    types = (JPEG,MP4,MOV)
    
    def __init__(self,filename=None):
        if filename:
            self.set_filename(filename)
        
    def set_filename(self,filename):
        '''Redefine o arquivo que esse ParserResolver esta analisando'''
        self.filename = filename
        self.extension = self._get_extension()
        self.filetype = self._get_filetype()
        # print '%s :: %s :: %s' % (self.filename, self.extension, self.filetype)

    
    def _get_filetype(self):
        '''Retorna a classe que controla informacoes relativas ao tratamento 
        do arquivo self.filename'''
        for t in ParserResolver.types:
            if self.extension in t.extensions:
                return t
        return None

    def _get_extension(self):
        '''Obtem a extensao do arquivo self.filename.'''
        parts = self.filename.split('.')
        return parts[-1].lower()

    def get_parser(self):
        '''Seleciona, instancia e retorna a classe que eh capaz de ler os 
        metadados do arquivo self.filename'''
        if self.filetype:
            parsers =  self.filetype.parsers
            prefered = self.filetype.prefered
            parser_class = parsers[prefered]
            return parser_class(self.filename)
        else:
            return None
