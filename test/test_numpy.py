#!/usr/bin/env python
# coding: utf-8

from nose import main
from nose.tools import *
import unittest

import time
import numpy
import random
from msgpack import packb, unpackb

def decode_numpy( obj):
    if "__ion_array__" in obj:
        return numpy.array(obj['content'],dtype=numpy.dtype(obj['shape']['type']))

    elif '__complex__' in obj:
        return complex(obj['real'], obj['imag'])
        ## Always return object
    return obj

def encode_numpy( obj):
    if isinstance(obj, numpy.ndarray):
        return {"shape":{"type":str(obj.dtype),"nd":len(obj.shape),"lengths":obj.shape},"content":obj.tolist(),"__ion_array__":True}

    elif isinstance(obj, complex):
        return {'__complex__': True, 'real': obj.real, 'imag': obj.imag}

    else:
        # Must raise type error to avoid recursive failure
        raise TypeError('Unknown type in user specified encoder')
    return obj



class NumpyMsgPackTestCase(unittest.TestCase):

    _decoder = None
    _encoder = None

    types = {
        'int8':('int8',random.randint,(-(1 << 7), (1 << 7)-1)),
        'int16':('int16',random.randint,(-(1 << 15), (1 << 15)-1)),
        'int32':('int32',random.randint,(-(1 << 31), (1 << 31)-1)),
        'int64':('int64',random.randint,(-(1 << 63), (1 << 63)-1)),

        'uint8':('uint8',random.randint,(0, (1 << 8)-1)),
        'uint16':('uint16',random.randint,(0, (1 << 16)-1)),
        'uint32':('uint32',random.randint,(0, (1 << 32)-1)),
        'uint64':('uint64',random.randint,(0, (1 << 64)-1)),


        'float32_eps':('float32',lambda o: 1+o ,(numpy.finfo('float32').eps,)),
        'float32_epsneg':('float32',lambda o: 1-o ,(numpy.finfo('float32').epsneg,)),
        'float32':('float32',numpy.random.uniform,(numpy.finfo('float32').min, numpy.finfo('float32').max)),

        'float64_eps':('float64',lambda o: 1+o ,(numpy.finfo('float64').eps,)),
        'float64_epsneg':('float64',lambda o: 1-o ,(numpy.finfo('float64').epsneg,)),
        'float64':('float64',numpy.random.uniform,(numpy.finfo('float64').min, numpy.finfo('float64').max)),

        'complex64':('complex64',lambda a,b: numpy.complex(numpy.random.uniform(a,b), numpy.random.uniform(a,b)) ,(numpy.finfo('float64').min, numpy.finfo('float64').max)),

    }

    #shapes = ((3,4), (9,12,18), (10,10,10,10))
    shapes = ((100,100,10,10),)


    def __init__(self, *args, **kwargs):
        super(NumpyMsgPackTestCase, self).__init__(*args,**kwargs)

        self._decoder = decode_numpy
        self._encoder = encode_numpy

    def test_all(self):

        for type,(type, func, args) in self.types.iteritems():
            for shape in self.shapes:
                print "Running type: %s, shape: %s" % (type, str(shape))
                self.run_it(self._encoder, self._decoder, type, func, args, shape)


    def run_it(self, encoder, decoder, type, func, args, shape):

        array = numpy.zeros(shape, type)

        for x in numpy.nditer(array, op_flags=['readwrite']):
            x[...] = func(*args)

        tic = time.time()
        msg = packb(array, default=encoder)
        new_array = unpackb(msg,object_hook=decoder)
        toc = time.time() - tic


        print 'Binary Size: "%d", Time: %s' % (len(msg), toc)

        assert_true((array == new_array).all())



