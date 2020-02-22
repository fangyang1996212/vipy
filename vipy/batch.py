import os
import sys
import atexit
from vipy.util import try_import, islist, tolist
from itertools import repeat
try_import('dask', 'dask distributed torch')
from dask.distributed import Client
from dask.distributed import as_completed, wait
try_import('torch', 'torch');  import torch
import numpy as np


class Batch(object):
    """vipy.batch.Batch class

    This class provides a representation of a set of vipy objects.  All of the object types must be the same.  If so, then an operation on the batch is performed on each of the elements in the batch in parallel.

    Examples:

    >>> b = vipy.batch.Batch([Image(filename='img_%06d.png' % k) for k in range(0,100)])
    >>> b.bgr()  # convert all elements in batch to BGR
    >>> b.torch()  # load all elements in batch and convert to torch tensor
    >>> b.map(lambda im: im.bgr())  # equivalent
    >>> b.map(lambda im: np.sum(im.array())) 
    >>> b.map(lambda im, f: im.saveas(f), args=['out%d.jpg' % k for k in range(0,100)])
    
    >>> v = vipy.video.RandomSceneActivity()
    >>> b = vipy.batch.Batch(v, n_processes=16)
    >>> b.map(lambda v,k: v[k], args=[(k,) for k in range(0, len(v))])  # paralle interpolation

    >>> d = vipy.dataset.kinetics.Kinetics700('/path/to/kinetics').download().trainset()
    >>> b = vipy.batch.Batch(d, n_processes=32)
    >>> b.map(lambda v: v.download().save())  # will download and clip dataset in parallel

    """    
             
    def __init__(self, objlist, n_processes=4, dashboard=False):
        """Create a batch of homogeneous vipy.image objects from an iterable that can be operated on with a single parallel function call
        """

        objlist = tolist(objlist)
        self._batchtype = type(objlist[0])        
        assert all([isinstance(im, self._batchtype) for im in objlist]), "Invalid input - Must be homogeneous list of the same type"                
        self._objlist = objlist        
        self._client = Client(name='vipy', scheduler_port=0, dashboard_address=None if not dashboard else ':0', processes=True, threads_per_worker=1, n_workers=n_processes, env={'VIPY_BACKEND':'Agg'})
        self._n_processes = n_processes
        atexit.register(self.shutdown)        
        
    def __len__(self):
        return len(self._objlist)

    def __del__(self):
        self.shutdown()
        
    def __repr__(self):
        return str('<vipy.batch: type=%s, len=%d, procs=%d>' % (str(self._batchtype), len(self), self._n_processes))

    def batch(self, resultlist=None):
        if resultlist is not None:            
            assert islist(resultlist), "Invalid input"
            #completedlist = [f.result() for f in as_completed(resultlist)]
            wait(resultlist)
            completedlist = [f.result() for f in resultlist]
            if isinstance(completedlist[0], self._batchtype):
                self._objlist = completedlist
                return self
            else:
                return completedlist
        else:
            return self._objlist
        
    def __iter__(self):
        for im in self._objlist:
            yield im
            
    def __getattr__(self, attr):
        """Call the same method on all Image objects"""
        return lambda *args, **kw: self.batch(self.__dict__['_client'].map(lambda im: getattr(im, attr)(*args, **kw), self._objlist))
        
    def map(self, f_lambda, args=None):
        """Run the lambda function on each of the elements of the batch. 
        
        If args is provided, then this is a unique argument for the lambda function for each of the elements in the batch
        
        >>> iml = [vipy.image.RandomScene(512,512) for k in range(0,1000)]   
        >>> imb = vipy.image.Batch(iml, n_processes=4) 
        >>> imb.map(lambda im,f: im.saveas(f), args=[('/tmp/out%d.jpg'%k,) for k in range(0,1000)])  
        >>> imb.map(lambda im: im.rgb())  # this is equivalent to imb.rgb()

        """
        c = self.__dict__['_client']        
        if args is not None:
            if len(self._objlist) > 1:
                assert islist(args) and len(list(args)) == len(self._objlist), "args must be a list of arguments of length %d, one for each element in batch" % len(self._objlist)
                return self.batch([c.submit(f_lambda, im, *a) for (im, a) in zip(self._objlist, args)])                
            else:
                assert islist(args), "args must be a list"
                obj = c.scatter(self._objlist[0], broadcast=True)
                return self.batch([self.__dict__['_client'].submit(f_lambda, obj, *a) for a in args])
        else:
            return self.batch(self.__dict__['_client'].map(f_lambda, self._objlist))

    def filter(self, f_lambda):
        """Run the lambda function on each of the elements of the batch and filter based on the provided lambda  
        """
        c = self.__dict__['_client']        
        is_filtered = self.batch(self.__dict__['_client'].map(f_lambda, self._objlist))
        self._objlist = [obj for (f, obj) in zip(is_filtered, self._objlist) if f is True]
        return self
        
    def torch(self):
        """Convert the batch of N HxWxC images to a NxCxHxW torch tensor"""
        return torch.cat(self.map(lambda im: im.torch()))

    def numpy(self):
        """Convert the batch of N HxWxC images to a NxCxHxW torch tensor"""
        return np.stack(self.map(lambda im: im.numpy()))
    
    def shutdown(self):
        self._client.shutdown()        
    
