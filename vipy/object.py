import numpy as np
from vipy.geometry import BoundingBox
import uuid


class Detection(BoundingBox):
    """Represent a single bounding box with a label and confidence for an object detection"""

    def __init__(self, label=None, xmin=None, ymin=None, width=None, height=None, xmax=None, ymax=None, confidence=None, xcentroid=None, ycentroid=None, category=None, xywh=None, shortlabel=None):
        super(Detection, self).__init__(xmin=xmin, ymin=ymin, width=width, height=height, xmax=xmax, ymax=ymax, xcentroid=xcentroid, ycentroid=ycentroid, xywh=xywh)
        assert not (label is not None and category is not None), "Constructor requires either label or category kwargs, not both"
        self._id = uuid.uuid1().hex        
        self._label = category if category is not None else label
        self._shortlabel = self._label if shortlabel is None else shortlabel
        self._confidence = float(confidence) if confidence is not None else confidence

    def __repr__(self):
        strlist = []
        if self.category() is not None:
            strlist.append('category="%s"' % self.category())
        if self.isvalid():
            strlist.append('bbox=(xmin=%1.1f, ymin=%1.1f, width=%1.1f, height=%1.1f)' %
                           (self.xmin(), self.ymin(),self.width(), self.height()))
        if self._confidence is not None:
            strlist.append('conf=%1.3f')
        return str('<vipy.object.detection: %s>' % (', '.join(strlist)))

    def __eq__(self, other):
        return isinstance(other, Detection) and xywh() == other.xywh() and self.category() == other.category()

    def __str__(self):
        return self.__repr__()

    def dict(self):
        return {'id':self._id, 'category':self.category(), 'boundingbox':super(Detection, self).dict()}
    
    def category(self, category=None):
        if category is None:
            return self._label
        else:
            self._label = category
            self._shortlabel = self._label
            return self

    def shortlabel(self, label=None):
        """A optional shorter label string to show in the visualizations"""        
        if label is not None:
            self._shortlabel = label
            return self
        else:
            return self._shortlabel

    def label(self, label):
        """Alias for category"""
        return self.category(label)


class Track(object):
    """Represent many labeled bounding boxes of an instance through time, as observed at finite times, with interpolation between observations"""

    def __init__(self, frames, boxes, category=None, label=None, confidence=None, attributes=None, framerate=None, interpolation='linear', boundary='extend', shortlabel=None):
        assert not (label is not None and category is not None), "Constructor requires either label or category kwargs, not both"        
        self._id = uuid.uuid1().hex
        self._label = category if category is not None else label
        self._shortlabel = self._label if shortlabel is None else shortlabel
        self._keyframes = None
        self._keyboxes = None
        assert isinstance(frames, tuple) or isinstance(frames, list), "Frames must be tuple or list"
        assert isinstance(boxes, tuple) or isinstance(boxes, list), "Boxes must be tuple or list"        
        assert all([isinstance(bb, BoundingBox) for bb in boxes]), "Bounding boxes must be vipy.geometry.BoundingBox objects"
        assert all([bb.isvalid() for bb in boxes]), "Invalid bounding boxes"
        assert len(frames) == len(boxes), "Boxes and frames must be the same length, there must be one frame per box"
        self._framerate = framerate
        assert interpolation in set(['linear']), "Invalid interpolation - Must be ['linear']"
        self._interpolation = interpolation
        assert boundary in set(['extend', 'strict']), "Invalid interpolation boundary - Must be ['extend', 'strict']"
        self._boundary = boundary
        
        # Sorted increasing frame order
        (frames, boxes) = zip(*sorted([(f,bb) for (f,bb) in zip(frames, boxes)], key=lambda x: x[0]))
        self._keyframes = frames
        self._keyboxes = boxes
        
    def __repr__(self):
        strlist = []
        if self.category() is not None:
            strlist.append('category="%s"' % self.category())
        if self.endframe() - self.startframe() > 0:
            strlist.append('startframe=%d, endframe=%d' % (self.startframe(), self.endframe()))
        strlist.append('keyframes=%d' % len(self._keyframes))
        return str('<vipy.object.track: %s>' % (', '.join(strlist)))

    def __getitem__(self, k):
        return self._linear_interpolation(k)

    def __iter__(self):
        print('__iter__')
        for k in range(self.startframe(), self.endframe()):
            yield self._linear_interpolation(k)

    def __len__(self):
        return len(self._keyframes)

    def dict(self):
        return {'id':self._id, 'category':self.category(), 'keyframes':self._keyframes, 'framerate':self._framerate, 
                'boundingbox':[bb.dict() for bb in self._keyboxes]}

    def add(self, frame, box):
        """Add a new keyframe and associated box to track"""
        self._keyframes.append(frame)
        self._keyboxes.append(box)
        (self._keyframes, self._keyboxes) = zip(*sorted([(f,bb) for (f,bb) in zip(self._keyframes, self._keyboxes)], key=lambda x: x[0]))        
        return self
        
    def keyframes(self):
        """Return keyframe frame indexes where there are track observations"""
        return self._keyframes

    def framerate(self, fps):
        """Resample keyframes from known original framerate set by constructor to be new framerate fps"""
        assert self._framerate is not None, "Framerate conversion requires that the framerate is known for current keyframes.  This must be provided to the vipy.object.Track() constructor."
        self._keyframes = [int(np.round(f*(fps/float(self._framerate)))) for f in self._keyframes]
        self._framerate = fps
        return self
        
    def startframe(self):
        return np.min(self._keyframes)

    def endframe(self):
        return np.max(self._keyframes)

    def _linear_interpolation(self, k):
        """Linear bounding box interpolation at frame=k given observed boxes (x,y,w,h) at observed frames, with repeated endpoints"""
        (xmin, ymin, width, height) = zip(*[bb.to_xywh() for bb in self._keyboxes])
        d = Detection(category=self._label,
                      xmin=np.interp(k, self._keyframes, xmin),
                      ymin=np.interp(k, self._keyframes, ymin),
                      width=np.interp(k, self._keyframes, width),
                      height=np.interp(k, self._keyframes, height))
        d._id = self._id  # for track correpsondence 
        return d if self._boundary == 'extend' else (None if not self.during(k) else d)

    def category(self, label=None):
        if label is not None:
            self._label = label
            self._shortlabel = label
            return self
        else:
            return self._label

    def label(self, label):
        """Alias for category"""
        return self.category(label)
        
    def shortlabel(self, label=None):
        """A optional shorter label string to show in the visualizations"""                
        if label is not None:
            self._shortlabel = label
            return self
        else:
            return self._shortlabel

    def during(self, k):
        return k >= self.startframe() and k < self.endframe()

    def offset(self, dt=0, dx=0, dy=0):
        self._keyboxes = [bb.offset(dx, dy) for bb in self._keyboxes]
        self._keyframes = list(np.array(self._keyframes) + dt)
        return self

    def rescale(self, s):
        """Rescale track boxes by scale factor s"""
        self._keyboxes = [bb.rescale(s) for bb in self._keyboxes]
        return self

    def scale(self, s):
        """Alias for rescale"""
        return self.rescale(s)

    def scalex(self, sx):
        """Rescale track boxes by scale factor sx"""
        self._keyboxes = [bb.scalex(sx) for bb in self._keyboxes]
        return self

    def scaley(self, sy):
        """Rescale track boxes by scale factor sx"""
        self._keyboxes = [bb.scaley(sy) for bb in self._keyboxes]
        return self

    def dilate(self, s):
        """Dilate track boxes by scale factor s"""
        self._keyboxes = [bb.dilate(s) for bb in self._keyboxes]
        return self

    def rot90cw(self, H, W):
        """Rotate an image with (H,W)=shape 90 degrees clockwise and update all boxes to be consistent"""
        self._keyboxes = [bb.rot90cw(H, W) for bb in self._keyboxes]
        return self

    def rot90ccw(self, H, W):
        """Rotate an image with (H,W)=shape 90 degrees clockwise and update all boxes to be consistent"""
        self._keyboxes = [bb.rot90ccw(H, W) for bb in self._keyboxes]
        return self


class Activity(object):
    def __init__(self, startframe, endframe, label=None, category=None, subject=None, objects=None, attributes=None, shortlabel=None):
        assert not (label is not None and category is not None), "Constructor requires either label or category kwargs, not both"        
        self._id = uuid.uuid1().hex
        self._startframe = startframe
        self._endframe = endframe
        self._label = category if category is not None else label        
        self._shortlabel = self._label if shortlabel is None else shortlabel
        self._subject = subject
        self._objects = objects
        if objects is not None:
            assert isinstance(objects, list) and all([isinstance(x, Track) for x in objects]), "Invalid object list - Must be a list [vipy.object.Track(), ...]"
        if subject is not None:
            assert isinstance(subject, Track), "Invalid subject - Must be a vipy.object.Track()"            
        self._attributes = attributes
        
    def __repr__(self):
        return str('<vipy.activity: category="%s", frames=(%d,%d), objects=%s>' % (self.category(), self.startframe(), self.endframe(), str(set([x.category() for x in self.objects()]))))

    def dict(self):
        return {'id':self._id, 'category':self.category(), 'startframe':self._startframe, 'endframe':self._endframe, 'attributes':self._attributes,
                'subject':self._subject.dict() if self._subject is not None else None,
                'objects':[obj.dict() for obj in self._objects] if self._objects is not None else None}
    
    def startframe(self):
        return self._startframe

    def endframe(self):
        return self._endframe

    def category(self, label=None):
        if label is not None:
            self._label = label
            self._shortlabel = label
            return self
        else:
            return self._label

    def label(self, label):
        """Alias for category"""
        return self.category(label)
        
    def shortlabel(self, label=None):
        """A optional shorter label string to show in the visualizations"""                
        if label is not None:
            self._shortlabel = label
            return self
        else:
            return self._shortlabel
        
    def objects(self, objects=None):
        if objects is not None:
            self._objects = objects
            return self
        else:
            return self._objects

    def subject(self, subject=None):
        if subject is not None:
            self._subject = subject
            return self
        else:
            return self._subject

    def hastrack(self, t):
        """Is the track part of the activity?"""
        assert isinstance(t, Track) or isinstance(t, Detection), "Invalid input - Must be a vipy.object.Track()"
        return (self._subject is not None and self._subject._id == t._id) or (self._objects is not None and any([obj._id == t._id for obj in self._objects]))
            
    def during(self, frame):
        return int(frame) >= self._startframe and int(frame) <= self._endframe

    def offset(self, dt):
        self._startframe = self._startframe - dt
        return self
    
