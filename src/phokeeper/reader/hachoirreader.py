from abstractreader import *

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
