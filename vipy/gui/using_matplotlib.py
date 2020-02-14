import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from vipy.util import islist, temppng


FIGHANDLE = {}
matplotlib.rcParams['toolbar'] = 'None'


# Optional latex strings in captions
try:
    from distutils.spawn import find_executable
    if not find_executable('latex'):
        raise
    matplotlib.rc('text', usetex=True)  # requires latex installed
except:
    pass  # ignored if latex is not installed


def flush():
    plt.pause(0.001)

    
def show(fignum):
    plt.ion()
    plt.draw()
    plt.show()


def noshow(fignum):
    closeall()
    plt.ioff()


def savefig(filename=None, fignum=None, pad_inches=0, dpi=None, bbox_inches='tight', format=None):
    if fignum is not None:
        plt.figure(fignum)
    if filename is None:
        filename = temppng()
    plt.savefig(filename, pad_inches=pad_inches, dpi=dpi, bbox_inches=bbox_inches, format=format)
    return filename


def figure(fignum=None):
    if fignum is not None:
        plt.figure(fignum)
    else:
        plt.figure()
    return plt


def close(fignum):
    global FIGHANDLE
    if fignum in FIGHANDLE:
        FIGHANDLE.pop(fignum, None)
        return plt.close(fignum)
    else:
        return None


def closeall():
    global FIGHANDLE
    FIGHANDLE = {}
    return plt.close('all')


def _imshow_tight(img, fignum=None):
    """Helper function to show an image in a figure window"""
    dpi = 100.0
    fig = plt.figure(fignum, dpi=dpi, figsize=(img.shape[1] / dpi, img.shape[0] / dpi))
    plt.clf()

    # Tight axes
    ax = plt.Axes(fig, [0., 0., 1.0, 1.0], frameon=False)
    fig.add_axes(ax)
    for a in plt.gcf().axes:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)
    imh = plt.imshow(img, animated=True, interpolation='nearest', aspect='equal')
    return (fig.number, imh)


def imshow(img, fignum=None):
    """Show an image in a figure window (optionally visible), reuse previous figure if it is the same shape"""
    global FIGHANDLE
    if fignum in plt.get_fignums() and fignum in FIGHANDLE and FIGHANDLE[fignum].get_size() == img.shape[0:2]:
        # Delete all polygon and text overlays from previous drawing
        FIGHANDLE[fignum].set_data(img)
        for c in plt.gca().get_children():
            if 'Text' in c.__repr__() or 'Polygon' in c.__repr__() or 'Circle' in c.__repr__() or 'Line' in c.__repr__() or 'Patch' in c.__repr__():
                try:
                    c.remove()
                except:
                    pass
    else:
        if fignum in plt.get_fignums() and fignum in FIGHANDLE:
            close(fignum)
        (fignum, imh) = _imshow_tight(img, fignum=fignum)
        FIGHANDLE[fignum] = imh
    return fignum


def boundingbox(img, xmin, ymin, xmax, ymax, bboxcaption=None, fignum=None, bboxcolor='green', facecolor='white', facealpha=0.5, textcolor='black', textfacecolor='white', textfacealpha=1.0, fontsize=10, captionoffset=(0,0)):
    """Draw a captioned bounding box on a previously shown image"""
    plt.figure(fignum)
    lw = 3  # pull in the boxes by linewidth so that they do not overhang the figure
    (H,W) = (img.shape[0], img.shape[1])
    plt.axvspan(max(xmin, lw/2), min(xmax, W-lw/2), ymin=1.0 - np.float32(float(min(ymax, H-lw/2)) / float(H)), ymax=1-np.float32(float(max(ymin, lw/2)) / float(H)), edgecolor=bboxcolor, facecolor=facecolor, linewidth=lw, fill=True, alpha=facealpha, label=None, capstyle='round', joinstyle='bevel', clip_on=True)

    # Text string
    if bboxcaption is not None:
        # clip_on clips anything outside the image
        plt.text(xmin + captionoffset[0], ymin + captionoffset[1], bboxcaption, color=textcolor, bbox=dict(facecolor=textfacecolor, edgecolor=textcolor, alpha=textfacealpha, boxstyle='round'), fontsize=fontsize, clip_on=True)

    return fignum


def imdetection(img, detlist, fignum=None, bboxcolor='green', do_caption=True, facecolor='white', facealpha=0.5, textcolor='green', textfacecolor='white', textfacealpha=1.0, fontsize=10, captionoffset=(0,0)):
    """Show bounding boxes from a list of vipy.object.Detections on the same image, plotted in list order with optional captions """

    # Create image
    fignum = imshow(img, fignum=fignum)

    # Valid detections
    for (k,det) in enumerate(detlist):
        if do_caption:
            bboxcaption = det.category()
        else:
            bboxcaption = None

        if islist(bboxcolor):
            bboxcolor_ = bboxcolor[k]
        else:
            bboxcolor_ = bboxcolor

        if islist(textcolor):
            textcolor_ = textcolor[k]
        else:
            textcolor_ = textcolor

        boundingbox(img, xmin=det.xmin(), ymin=det.ymin(), xmax=det.xmax(), ymax=det.ymax(), bboxcaption=bboxcaption,
                    fignum=fignum, bboxcolor=bboxcolor_, facecolor=facecolor, facealpha=facealpha, textcolor=textcolor_, textfacecolor=textfacecolor, fontsize=fontsize, captionoffset=captionoffset, textfacealpha=textfacealpha)

    return fignum


def imframe(img, fr, color='b', markersize=10, label=None, figure=None):
    """Show a scatterplot of fr=[[x1,y1],[x2,y2]...] 2D points overlayed on an image"""
    if figure is not None:
        fig = plt.figure(figure)
    else:
        fig = plt.figure()

    figure = plt.gcf().number

    plt.clf()

    ax = plt.Axes(fig, [0., 0., 1., 1.], frameon=False)
    fig.add_axes(ax)

    plt.axis('off')
    ax.set_axis_off()
    for a in plt.gcf().axes:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)

    plt.autoscale(tight=True)
    plt.plot(fr[:,0],fr[:,1],'%s.' % color, markersize=markersize, axes=ax)

    if label is not None:
        for ((x,y),lbl) in zip(fr, label):
            ax.text(x, y, lbl, color='white')

    return plt


def frame(fr, im=None, color='b.', markersize=10, figure=None, caption=None):
    """Show a scatterplot of fr=[[x1,y1],[x2,y2]...] 2D points"""
    if figure is not None:
        plt.figure(figure)
    else:
        plt.figure()
        plt.clf()

    plt.axes([0,0,1,1])
    plt.plot(fr[:,0],fr[:,1],color)
    plt.axis('off')
    plt.draw()


def colorlist():
    """Return a list of named colors that are higher contrast with a white background"""
    colorlist = [str(name) for (name, hex) in matplotlib.colors.cnames.items()]
    primarycolorlist = ['green','blue','red','cyan','orange', 'yellow','violet']
    tableaucolors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    colors = primarycolorlist + tableaucolors + [c for c in colorlist if c not in set(primarycolorlist).union(tableaucolors)]
    colors = [x for x in colors if x not in
              set(['whitesmoke', 'gainsboro', 'w', 'floralwhite', 'lightgoldenrodyellow', 'ghostwhite', 'white', 'mistyrose',
                   'seashell', 'ivory', 'honeydew', 'azure', 'lavenderblush', 'beige', 'mintcream', 'lightcyan',
                   'snow', 'gainsboro', 'linen', 'antiquewhite', 'papayawhip', 'oldlace', 'cornsilk', 'palegoldenrod',
                   'lightyellow', 'aliceblue', 'yellow', 'sandybrown', 'orange'])]  # https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    colors = [x for x in colors if 'light' not in x]
    return colors


def edit():
    import matplotlib.pyplot as plt 
    from matplotlib.widgets import Slider, Button, RadioButtons   
    button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
    ax2 = plt.axes([0.1, 0.325, 0.5, 0.05])

    ax2 = plt.axes([0, 0, 0.5, 0.05])
    ax2.patch.set_alpha(0.5) 
    Slider(ax2, 'Reset2', facecolor='red', alpha=0.5, valmin=0, valmax=10)
    ax2.patch.alpha = 0.5 

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class Annotate(object):
    def __init__(self):
        self.ax = plt.gca()
        self.rect = Rectangle((0,0), 1, 1)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.ax.add_patch(self.rect)
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        print ('press')
        self.x0 = event.xdata
        self.y0 = event.ydata

    def on_release(self, event):
        print ('release')
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        self.ax.figure.canvas.draw()


class DraggableRectangle(object):
    def __init__(self, rect):
        self.rect = rect
        self.press = None

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return

        contains, attrd = self.rect.contains(event)
        if not contains: return
        print('event contains', self.rect.xy)
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None: return
        if event.inaxes != self.rect.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        #print('x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f' %
        #      (x0, xpress, event.xdata, dx, x0+dx))
        self.rect.set_x(x0+dx)
        self.rect.set_y(y0+dy)

        self.rect.figure.canvas.draw()


    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.rect.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)

        
    #a = Annotate()
    #plt.show()    

    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    #rects = ax.bar(range(10), 20*np.random.rand(10))
    #drs = []
    #for rect in rects:
    #    dr = DraggableRectangle(rect)
    #    dr.connect()
    #    drs.append(dr)
    #
    #plt.show()


class DraggableRectangleFast(object):
    lock = None  # only one can be animated at a time
    def __init__(self, rect):
        self.rect = rect
        self.press = None
        self.background = None

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return
        if DraggableRectangle.lock is not None: return
        contains, attrd = self.rect.contains(event)
        if not contains: return
        print('event contains', self.rect.xy)
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata
        DraggableRectangle.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.rect)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if DraggableRectangle.lock is not self:
            return
        if event.inaxes != self.rect.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.rect.set_x(x0+dx)
        self.rect.set_y(y0+dy)

        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.rect)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        'on release we reset the press data'
        if DraggableRectangle.lock is not self:
            return

        self.press = None
        DraggableRectangle.lock = None

        # turn off the rect animation property and reset the background
        self.rect.set_animated(False)
        self.background = None

        # redraw the full figure
        self.rect.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)    
