#!/bin/env python
import datetime
import sys
import os


class MetadataReader:
    '''Classe abstrata para leitura dos metadados ano e mes de arquivos de midia
    o contrato que ela define sao dois atributos (self.year e self.month), que
    sao preenchidos apos a chamda da funcao self.parse()
    A classe tambem contem a implementacao adequada para obter o caminho onde
    a midia sera armazenada a partir dessas informacoes (ano e mes)'''
    def __init__(self, filename):
        self.filename = filename
        self.month = None
        self.year = None
        
    def get_path(self):
        '''Retorna o caminho a ser usado no armazenamento da midia (ano/mes)'''
        return '%d/%.2d'%(self.year, self.month)
        
    def parse(self):
        '''Metodo a ser implementado pelos leitores concretos. Ele deve definir
        os atributos self.year e self.month'''
        pass


import exifread

class JpegReaderExifReader(MetadataReader):
    '''Leitor que utiliza o pacote exifread para ler jpegs'''
    
    def __init__(self, filename):
        MetadataReader.__init__(self,filename)
        
    def parse(self):
        f = open(self.filename,'rb')
        keys = exifread.process_file(f,details=False)
        f.close()
        exif_date = keys['EXIF DateTimeOriginal']
        date_string = exif_date.values
        date_time = datetime.datetime.strptime(date_string,'%Y:%m:%d %H:%M:%S') 
        self.year = date_time.year
        self.month = date_time.month


# http://hachoir3.readthedocs.org/
import hachoir_parser
import hachoir_metadata
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
    
class HachoirGenericReader(MetadataReader):
    '''Leitor que utiliza o pacote hachoir para ler qualquer midia. Voa nas
    fotos jpeg no motox e eh relativamente lento. Porem le qualquer formato'''

    def __init__(self, filename):
        MetadataReader.__init__(self,filename)
    
    def parse(self):
        filename, realname = unicodeFilename(self.filename), self.filename
        parser = hachoir_parser.createParser(filename, realname)
        if not parser:
            sys.stderr.write("Unable to parse file %s/n"%self.filename)
            return
        try:
            ## TODO Essa chamada da um warning quando nao ha gps data
            metadata = hachoir_metadata.extractMetadata(parser)
        except HachoirError, err:
            print "Metadata extraction error: %s" % unicode(err)
            metadata = None
        if not metadata:
            print "Unable to extract metadata"
            exit(1)
        date_time = metadata.get('creation_date')
        self.year = date_time.year
        self.month = date_time.month


class JPEG:
    '''Classe que controla informacoes relativas ao tratamento de jpegs'''
    extensions = ('jpg','jpeg')
    parsers = (HachoirGenericReader, JpegReaderExifReader)
    prefered = 1
    
class MOV:
    '''Classe que controla informacoes relativas ao tratamento de movs'''
    extensions = ('mov',)
    parsers = (HachoirGenericReader,)
    prefered = 0
    
    
class MP4:
    '''Classe que controla informacoes relativas ao tratamento de mp4s'''
    extensions = ('mp4','mpeg4')
    parsers = (HachoirGenericReader,)
    prefered = 0

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

# files = ('../../data/DSC_0003.JPG',)
files = sys.argv[1:]
#files = ('../../data/video.mp4','../../data/DSC_0003.JPG')
pr = ParserResolver()
for file in files:
    pr.set_filename(file)
    p = pr.get_parser()
    if p:
        p.parse()
        print os.path.basename(p.filename), p.get_path()
    else:
        print 'Falhou para %s'%file

