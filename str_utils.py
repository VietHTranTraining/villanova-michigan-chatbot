import unicodedata

def uniToStr(uncd):
   return unicodedata.normalize('NFKD', uncd).encode('ascii','ignore')
