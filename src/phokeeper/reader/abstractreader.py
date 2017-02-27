
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

