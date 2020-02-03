import numpy as np
from vipy.geometry import BoundingBox

class Detection(BoundingBox):
    """Represent a single bounding box with a label and confidence for an object detection"""
    def __init__(self, label='object', xmin=None, ymin=None, width=None, height=None, xmax=None, ymax=None, confidence=None, xcentroid=None, ycentroid=None):
        super(Detection, self).__init__(xmin=xmin, ymin=ymin, width=width, height=height, xmax=xmax, ymax=ymax, xcentroid=xcentroid, ycentroid=ycentroid)
        self._label = str(label)
        self._confidence = float(confidence) if confidence is not None else confidence        
        
    def __repr__(self):
        strlist = []
        if self.category() is not None: 
            strlist.append('category="%s"' % self.category())
        if self.isvalid():
            strlist.append('bbox=(xmin=%1.1f,ymin=%1.1f,xmax=%1.1f,ymax=%1.1f)' %
                           (self.bbox.xmin(), self.bbox.ymin(),self.bbox.xmax(), self.bbox.ymax()))
        if self._confidence is not None:
            strlist.append('conf=%1.3f')
        return str('<vipy.object.detection: %s>' % (', '.join(strlist)))
            
    def __str__(self):
        return self.__repr__()

    def category(self):
        return self._label

    def label(self):
        return self._label


class Track(object):

    """Represent many bounding boxes of an instance through time"""
    def __init__(self, label, frames, boxes, confidence=None, attributes=None):
        self._label = label
        self._frames = frames
        self._boxes = boxes
        assert all([isinstance(bb, BoundingBox) for bb in boxes]), "Bounding boxes must be vipy.geometry.BoundingBox objects"
        assert all([bb.isvalid() for bb in boxes]), "Invalid bounding boxes"

    def __repr__(self):
        strlist = []
        if self.category() is not None: 
            strlist.append('category="%s"' % self.category())
        strlist.append('frame=[%d,%d]' % (self.startframe, self.endframe))
        strlist.append('obs=%d' % len(self._frames))
        return str('<vipy.object.track: %s>' % (', '.join(strlist)))
        
    def __getitem__(self, k):
        if k >= self.startframe() and k < self.endframe():
            return self._interpolate(k)
        else:
            raise ValueError('Invalid frame index %d ' % k)

    def __iter__(self):
        for k in range(self._startframe, self._endframe):
            yield (k,self._interpolate(k))
        
        
    def startframe(self):
        return np.min(self._frames)

    def endframe(self):
        return np.max(self._frames)

    def _interpolate(self, k):
        """Linear bounding box interpolation at frame=k given observed boxes (x,y,w,h) at observed frames"""
        (xmin, ymin, width, height) = zip(*[bb.to_xywh() for bb in self._boxes])
        return Detection(label=self._label,
                         xmin=np.interp(k, self._frames, xmin),
                         ymin=np.interp(k, self._frames, ymin),
                         width=np.interp(k, self._frames, width),
                         height=np.interp(k, self._frames, height))                                     

    def category(self, label=None):
        if label is not None:
            self._label = label
            return self
        else:
            return self._label

    def during(self, k):
        return k>=self.startframe() and k<self.endframe()

    
