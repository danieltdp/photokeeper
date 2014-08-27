#!/bin/env python
import datetime
import sys
import os
import os.path


class MetadataReader:
    '''Classe abstrata para leitura dos metadados ano e mes de arquivos de midia
    o contrato que ela define sao dois atributos (self.year e self.month), que
    sao preenchidos apos a chamda da funcao self.parse()
    A classe tambem contem a implementacao adequada para obter o caminho onde
    a midia sera armazenada a partir dessas informacoes (ano e mes)'''
    def __init__(self, filename):
        self.filename = filename
        self.month = 'noyear'
        self.year = 'nomonth'
        
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
        key = 'EXIF DateTimeOriginal'
        if key in keys:
            exif_date = keys[key]
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

#files = ('../../data/DSC_0003.JPG',)
#files = sys.argv[1:]
files = ('../../data/video.mp4','../../data/DSC_0003.JPG')


class Photokeeper:
    def __init__(self,original_dir,destination_dir):
        self.original_dir = original_dir
        self.destination_dir = destination_dir
        self.target_files = dict()
        self.failed_files = list()
        self.parser_resolver = ParserResolver()
        
    def read_original_files(self):
        os.path.walk(self.original_dir,Photokeeper._read_one_original_dir, self)
        
    def _read_one_original_dir(self,dirname,filenames):
        for filename in filenames:
            full_filename = os.path.join(dirname,filename)
            self.parser_resolver.set_filename(full_filename)
            parser = self.parser_resolver.get_parser()
            if parser:
                parser.parse()
                year = parser.year
                month = parser.month
                if year not in self.target_files.keys():
                    self.target_files[year] = dict()
                if month not in self.target_files[year].keys():
                    self.target_files[year][month] = list()
                self.target_files[year][month].append(full_filename)
            else:
                self.failed_files.append(full_filename)
                
    def print_orginal_files(self):
        for year in sorted(self.target_files.keys()):
            print '# YEAR %s' % year
            for month in sorted(self.target_files[year].keys()):
                print '## MONTH %s' % month
                for f in sorted(self.target_files[year][month]):
                    print ' - %s' % f
                    
    def print_failed_files(self):
        for f in self.failed_files:
            print ' - %s' % f
                    
                    
k = Photokeeper('/home/ubuntu/data',None)
k.read_original_files()
k.print_orginal_files()
k.print_failed_files()
