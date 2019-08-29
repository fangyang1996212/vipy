import os
from bobo.util import remkdir, dirlist, imlist, filebase, readcsv
from bobo.image import ImageDetection
import bobo.app
    
class WebFace(object):
    def __init__(self, datadir=None):
        self.datadir = bobo.app.datadir() if datadir is None else datadir
                
    def __repr__(self):
        return str('<viset.CASIA-WebFace: %s>' % self.datadir)

    def _parse(self):
        outlist = []
        id2name = {k:v for (k,v) in readcsv(os.path.join(self.datadir, 'names.txt'), separator=' ')}            
        for d in dirlist(self.datadir):
            outlist = outlist + [ImageDetection(filename=imfile, category=id2name[str(filebase(d))], xmin=13, ymin=13, xmax=250-13, ymax=250-13) for imfile in imlist(d)]
        return outlist

    def dataset(self):
        return self._parse()
    
    def subjects(self):
        (subjectid, subjectname) = zip(*readcsv(os.path.join(self.datadir, 'names.txt'), separator=' '))
        return subjectname

    def subjectid(self):
        return {k:v for (k,v) in readcsv(os.path.join(self.datadir, 'names.txt'), separator=' ')}
                        
