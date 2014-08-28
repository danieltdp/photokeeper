#!/bin/env python
import datetime
import sys
import os
import os.path
import string

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
    #TODO Implementar o leitor manual de MOVs
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
        
    def copy_files(self):
        for year in sorted(self.target_files.keys):
            yearpath = os.path.join(self.destination_dir,year)
            self._ensure_path_existante(yearpath)
            for month in sorted(self.target_files[year].keys()):
                monthpath = os.path.join(yearpath,month)
                self._ensure_path_existance(monthpath)
                for filename in sorted(self.target_files[year][month]):
                    destination_filename = self.ensure_name_corectness(monthpath,filename)
                    print filename, destination_filename
                            
    def _ensure_path_existance(self,path):
        '''Garante que um determinado diretorio existe e pode ser utilizado'''
        pass
    
    def _ensure_name_correctness(self,path,filename):
        '''This is a recursive function. Retorna o nome que o arquivo filename 
        deve usar para ser gravado com no diretorio path com a garantia de nao 
        sobrescrever outros arquivos que possam ja existir la'''
        #TODO testar, no caos de colisoes, se se trata do mesmo arquivo
        filename = os.path.basename(filename)
        result = os.path.join(path,filename)
        if os.path.exists(result):
            new_filename = self._build_alternative_name(filename)
            result = self._ensure_name_correctness(path,new_filename)
        return result    
                
    def _build_alternative_name(self,original_name):
        '''Apply a change rule to the original_name in order to avoid 
        collisions. It is not the duty of this funcion to test whether this
        makes a new collision'''
        # Separate name from extension
        if '.' not in original_name:
            extension = None
            name = original_name
        else:
            parts = string.rsplit(original_name,'.',1)
            name = parts[0]
            extension = parts[1]
        # Treat both cases: name without and with '_'. the later is more complex
        if '_' not in name:
            name = name + '_1'
        else:
            # This is the case of possible previous appendage, but it can be 
            # a false positive. We have to separte a file named myphoto_2.jpg 
            # from  myphoto_HDR.jpg. The first would be myphoto_3.jpg and the 
            # second, myphoto_HDR_1.jpg
            parts = string.rsplit(name,'_',1)
            possible_number = parts[1]
            the_rest = parts[0]
            try:
                number = int(possible_number)
                # It was actually a number and has to be incremented
                number = number + 1
                appendage = str(number)
                name = the_rest + '_' + appendage
            except ValueError:
                # Nope, not a number. Just a false positive
                name = name + '_1'
        if extension:
            return name + '.' + extension
        else:
            return name
        
k = Photokeeper('/home/ubuntu/data',None)
k.read_original_files()
k.print_orginal_files()
k.print_failed_files()
testtuples = (
    ('myfile.jpg','myfile_1.jpg'), 
    ('myfile_1.jpg', 'myfile_2.jpg'),
    ('myfile_15.jpg', 'myfile_16.jpg'),
    ('myfile_xpto.jpg', 'myfile_xpto_1.jpg'),
    ('myfile_xpto_4.jpg', 'myfile_xpto_5.jpg'),
    ('myfile_2_xpto.jpg', 'myfile_2_xpto_1.jpg'),
    ('myfile','myfile_1'), 
    ('myfile_1', 'myfile_2'),
    ('myfile_15', 'myfile_16'),
    ('myfile_xpto', 'myfile_xpto_1'),
    ('myfile_xpto_4', 'myfile_xpto_5'),
    ('myfile_2_xpto', 'myfile_2_xpto_1'))
for testtuple in testtuples:
    result = k._build_alternative_name(testtuple[0])
    if result != testtuple[1]:
        t = '[ERROR]'
    else:
        t = '[  OK ]'
    print '%s input: %s; expected: %s; output %s' % (t , testtuple[0], testtuple[1], result)
