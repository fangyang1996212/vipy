import os
import numpy as np
from vipy.image import ImageDetection, Image, ImageCategory, Scene
from vipy.object import Detection
from vipy.util import tempjpg, tempdir

def run():
    
    # Common Parameters
    jpegurl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Bubo_virginianus_06.jpg/1920px-Bubo_virginianus_06.jpg'
    gifurl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Rotating_earth_%28large%29.gif/200px-Rotating_earth_%28large%29.gif'
    pngurl = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/560px-PNG_transparency_demonstration_1.png'
    
    # Empty constructor should not raise exception
    im = Image()
    print('Empty Constructor: PASSED')

    # Non-existant filename should not raise exception during constructor (only during load)
    im = Image(filename='myfile')
    print('Filename Constructor: PASSED')

    # Malformed URL should raise exception
    try:
        im = Image(url='myurl')
        raise
    except:
        print('Malformed URL constructor: PASSED')

    # Valid URL should not raise exception (even if it is not an image extension)
    im = Image(url='http://visym.com')
    print('Image URL constructor: PASSED')

    # Valid URL and filename to save it
    im = Image(url='http://visym.com/myfile.jpg', filename='/my/file/path')
    print('URL and filename constructor: PASSED')
    
    # URL object
    im = Image(url=jpegurl)
    print('  Image __desc__: %s' % im)
    print('  Image length: %d' %  len(im))
    im.download()
    print('  Image __desc__: %s' % im)
    im.load()
    print('  Image __desc__: %s' % im)
    print('URL download: PASSED')

    # Valid URL but without an image extension 
    im = Image(url='http://bit.ly/great_horned_owl')
    print('  Image __desc__: %s' % im)
    im.load()
    print('  Image __desc__: %s' % im)
    print('URL download (without image extension): PASSED')
    
    # Invalid URL with ignore and verbose
    im = Image(url='https://a_bad_url.jpg')
    print('  Image __desc__: %s' % im)
    im.load(ignoreErrors=True, verbose=True)
    print('  Image __desc__: %s' % im)
    print('Invalid URL download: PASSED')

    # URL with filename 
    im = Image(url=jpegurl, filename='/tmp/myfile.jpg')
    print('  Image __desc__: %s' % im)
    print('  Image length: %d' %  len(im))
    im.download()
    print('  Image __desc__: %s' % im)
    im.load()
    print('  Image __desc__: %s' % im)
    print('URL with filename download: PASSED')

    # URL with filename in cache
    os.environ['VIPY_CACHE'] = tempdir()
    im = Image(url=jpegurl)
    print('  Image __desc__: %s' % im)
    im.load()
    print('  Image __desc__: %s' % im)
    assert os.environ['VIPY_CACHE'] in im.filename()
    print('URL with cache download: PASSED')
               
    # Filename object
    im = ImageDetection(filename='jebyrne.jpg', xmin=100, ymin=100, width=700, height=1000, category='face')
    print('Image __desc__: %s' % im)
    im.crop()
    print('Image __desc__: %s' % im)
    print('Filename: PASSED')

    # Clone
    im = Image(filename='jebyrne.jpg').load()
    imb = im
    im._array = im._array + 1  # modify array
    np.testing.assert_array_equal(imb.numpy(), im.numpy())  # share buffer
    imc = im.clone().flush().load()
    assert(np.any(im.numpy() != imc.numpy()))  # does not share buffer
    print('Image.clone: PASSED')    

    # Saveas
    im = Image(filename='jebyrne.jpg').load()
    f = tempjpg()    
    assert im.saveas(f) == f and os.path.exists(f)
    print('Image.saveas: PASSED')        

    # Stats
    im = Image(filename='jebyrne.jpg').load().stats()
    print('Image.stats: PASSED')        

    # Resize
    f = tempjpg()
    im = Image(filename='jebyrne.jpg').load().resize(16,16).saveas(f)
    assert Image(filename=f).shape() == (16,16,3)
    print('Image.resize: PASSED')        

    # Rescale
    f = tempjpg()
    im = Image(filename='jebyrne.jpg').load().resize(rows=8).saveas(f)
    assert Image(filename=f).height() == 8
    im = Image(filename='jebyrne.jpg').load().resize(cols=8).saveas(f)
    assert Image(filename=f).width() == 8
    im = Image(filename='jebyrne.jpg').load().maxdim(256).saveas(f)
    assert np.max(Image(filename=f).shape()) == 256
    print('Image.rescale: PASSED')        

    # GIF
    im = Image(url=gifurl)
    im.download(verbose=True)
    assert im.shape() == (200,200)
    print('GIF: PASSED')

    # Transparent PNG
    im = Image(url=pngurl)
    im.load(verbose=True)
    print('PNG: PASSED')

    # Image colorspace conversion
    im = Image(filename='jebyrne.jpg').resize(200,200)
    print(im.rgb())
    assert(im.shape() == (200,200,3))
    print(im.bgr())
    assert(im.shape() == (200,200,3))    
    print(im.rgba())
    assert(im.shape() == (200,200,4))        
    print(im.hsv())
    assert(im.shape() == (200,200,3))            
    print(im.bgra())
    assert(im.shape() == (200,200,4))                
    print(im.gray())
    assert(im.shape() == (200,200))                    
    print(im.float())
    assert(im.shape() == (200,200))                    
    print('Image conversion: PASSED')

    # Image colormaps
    im = ImageDetection(filename='jebyrne.jpg', xmin=100, ymin=100, width=200, height=200, category='face').crop()
    im.rgb().jet().bone().hot().rainbow()
    print('Image colormaps: PASSED')

    # Image detections
    im = ImageDetection(filename='jebyrne.jpg', xmin=100, ymin=100, width=200, height=200, category='face').crop()
    assert(im.shape() == (200,200,3))
    assert(im.bbox.width() == im.width() and im.bbox.height() == im.height() and im.bbox.xmin()==0 and im.bbox.ymin()==0)
    im = ImageDetection(filename='jebyrne.jpg', xmin=100, ymin=100, width=200, height=200, category='face')
    im = im.rescale(0.5)
    assert(im.bbox.width() == 100 and im.bbox.height() == 100)
    
    # Scene
    im = Scene()
    print('Empty Scene Constructor: PASSED')

    im = Scene(url='https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Bubo_virginianus_06.jpg/1920px-Bubo_virginianus_06.jpg').load()
    print('URL: PASSED')

    outfile = tempjpg()
    im = im.objects([Detection('obj1',50,100,300,300), Detection('obj2',600,600,400,400)])
    im.show(outfile=outfile)
    print('Show outfile ("%s"): PASSED' % outfile)


    
    

    
    
if __name__ == "__main__":
    run()



