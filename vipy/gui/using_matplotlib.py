import matplotlib
import sys

# if sys.platform == 'linux' or sys.platform == 'linux2':
#     try:
#         plt.switch_backend('tkagg')  # linux display
#     except:
#         matplotlib.use('Agg')
#         pass  # linux headless

from matplotlib import pyplot as plt
import numpy as np
from vipy.util import islist, temppng
import os
import sys


FIGHANDLE = {}
matplotlib.rcParams['toolbar'] = 'None'
plt.ion()
plt.show()

# Optional latex strings in captions
try:
    from distutils.spawn import find_executable
    if not find_executable('latex'):
        raise
    matplotlib.rc('text', usetex=True)  # requires latex installed
except:
    pass  # ignored if latex is not installed



def savefig(filename=None, handle=None, pad_inches=0, dpi=None, bbox_inches='tight', format=None):
    if handle is not None:
        plt.figure(handle)
    if filename is None:
        filename = temppng()
    plt.savefig(filename, pad_inches=pad_inches, dpi=dpi, bbox_inches=bbox_inches, format=format)
    return filename

def figure(fignum=None):
    if handle is not None:
        plt.figure(fignum)
    else:
        plt.figure()
    return plt

def close(fignum):
    global FIGHANDLE;
    if fignum in FIGHANDLE:
        FIGHANDLE.pop(fignum, None);
        return plt.close(fignum)
    else:
        return None

def closeall():
    global FIGHANDLE;  FIGHANDLE = {};
    return plt.close('all')

def _imshow_tight(img, figure=None, do_updateplot=True):
    """Helper function to show an image in a figure window"""
    dpi = 100.0
    fig = plt.figure(figure, dpi=dpi, figsize=(img.shape[1]/dpi, img.shape[0]/dpi))
    plt.clf()

    # Tight axes
    ax = plt.Axes(fig, [0., 0., 1.0, 1.0], frameon=False)
    fig.add_axes(ax)
    for a in plt.gcf().axes:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)    
    imh = plt.imshow(img, animated=True, interpolation='nearest', aspect='equal')    
    return imh


def imshow(img, figure=None, do_updateplot=True):
    """Show an image in a figure window, reuse previous figure if it is still visible and is the same shape"""
    global FIGHANDLE
    if figure in plt.get_fignums() and figure in FIGHANDLE and FIGHANDLE[figure].get_size() == img.shape[0:2]:
        # Delete all polygon and text overlays from previous drawing        
        FIGHANDLE[figure].set_data(img)
        for c in plt.gca().get_children():
            if 'Text' in c.__repr__() or 'Polygon' in c.__repr__() or 'Circle' in c.__repr__() or 'Line' in c.__repr__() or  'Patch' in c.__repr__():
                try:
                    c.remove()
                except:
                    pass
        if do_updateplot:
            plt.draw()
            plt.show()
    else:
        FIGHANDLE[figure] = _imshow_tight(img, do_updateplot=do_updateplot, figure=figure)
    plt.pause(0.00001)  # flush
    return figure


def imbbox(img, xmin, ymin, xmax, ymax, bboxcaption=None, figure=None, bboxcolor='green', facecolor='white', facealpha=0.5, textcolor='black', textfacecolor='white', do_updateplot=True, do_imshow=True, fontsize=10, captionoffset=(0,0)):
    """Draw bounding box on an image"""

    # Optionally update the underlying image to quickly add more polygons
    if do_imshow == True:
        imshow(img, figure=figure, do_updateplot=False)

    # (x,y) bounding box is right and down, swap to right and up for plot
    # clip_on clips anything outside the image
    plt.axvspan(xmin, xmax, ymin=1.0-np.float32(float(ymax)/float(img.shape[0])), ymax=1-np.float32(float(ymin)/float(img.shape[0])), edgecolor=bboxcolor, facecolor=facecolor, linewidth=3, fill=True, alpha=facealpha, label=None, capstyle='round', joinstyle='bevel', clip_on=True)

    # Text string
    if bboxcaption is not None:
        # clip_on clips anything outside the image
        plt.text(xmin+captionoffset[0], ymin+captionoffset[1], bboxcaption, color=textcolor, bbox=dict(facecolor=textfacecolor, edgecolor=textcolor, alpha=1, boxstyle='round'), fontsize=fontsize, clip_on=True)

    # Update plot only for final bbox if displaying a lot
    if do_updateplot == True:
        #plt.pause(0.00001)
        try:
            plt.gcf().canvas.flush_events()
        except:
            pass

        #plt.draw()
        #plt.show()

    plt.pause(0.00001)
    return plt.gcf().number

def imdetection(img, detlist, figure=None, bboxcolor='green', do_caption=True, facecolor='white', facealpha=0.5, textcolor='green', textfacecolor='white', captionlist=None, fontsize=10, captionoffset=(0,0)):
    """Show bounding boxes from a list of vipy.object.Detections on the same image, plotted in list order with optional captions """

    # Empty?
    if len(detlist) == 0:
        imshow(img, figure=figure, do_updateplot=True)
        return figure

    # Valid detections
    fig = figure
    for (k,det) in enumerate(detlist):
        do_imshow = True if k==0 else False  # first image only
        do_updateplot = True if k==(len(detlist)-1) else False  # last image only
        if do_caption and captionlist is not None:
            bboxcaption = str(captionlist[k])
        elif do_caption:
            bboxcaption = str(det.category())
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

        fig = imbbox(img=img, xmin=det.xmin(), ymin=det.ymin(), xmax=det.xmax(), ymax=det.ymax(), bboxcaption=bboxcaption, do_imshow=do_imshow, do_updateplot=do_updateplot, figure=fig, bboxcolor=bboxcolor_, facecolor=facecolor, facealpha=facealpha, textcolor=textcolor_, textfacecolor=textfacecolor, fontsize=fontsize, captionoffset=captionoffset)
    #plt.hold(False)
    plt.pause(0.00001)
    return fig


def imframe(img, fr, color='b', markersize=10, label=None, figure=None):
    """Show a scatterplot of fr=[[x1,y1],[x2,y2]...] 2D points overlayed on an image"""    
    if figure is not None:
        fig = plt.figure(figure)
        #plt.hold(True)
    else:
        fig = plt.figure()
        #plt.hold(True)

    figure = plt.gcf().number

    plt.pause(0.00001)
    #fig = plt.figure(np.floor(np.random.rand()*50))
    plt.clf()

    #height = float(im.shape[0])
    #width = float(im.shape[1])
    #fig = plt.gcf()
    #fig.set_size_inches(width/height, 1, forward=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.], frameon=False)
    #ax.set_axis_off()
    fig.add_axes(ax)


    if img is not None:
        b = ax.imshow(img, cmap=cm.gray)
    #plt.autoscale(tight=True)
    #plt.axis('image')
    #plt.axis('off')


    plt.axis('off')
    ax.set_axis_off()
    for a in plt.gcf().axes:
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)

    plt.autoscale(tight=True)
    #plt.hold(True)
    plt.plot(fr[:,0],fr[:,1],'%s.' % color, markersize=markersize, axes=ax)
    #plt.hold(False)
    #ax = plt.axes([0,0,1,1])
    #ax.axis('off')
    if label is not None:
        for ((x,y),lbl) in zip(fr, label):
            #plt.text(x, y, lbl, bbox=dict(facecolor='white', edgecolor='g',alpha=1))
            ax.text(x, y, lbl, color='white')

    #plt.draw()

    plt.pause(0.00001)
    return plt


def frame(fr, im=None, color='b.', markersize=10, figure=None, caption=None):
    """Show a scatterplot of fr=[[x1,y1],[x2,y2]...] 2D points"""
    if figure is not None:
        fig = plt.figure(figure)
        #plt.hold(True)
    else:
        fig = plt.figure()
        plt.clf()
        #plt.hold(True)

    ax = plt.axes([0,0,1,1])
    #b = plt.imshow(im, cmap=cm.gray)
    #plt.hold(True)
    plt.plot(fr[:,0],fr[:,1],color)
    #plt.hold(False)
    plt.axis('off');
    plt.draw()
    #return plt


def colorlist():
    """Return a list of named colors"""
    colorlist = [str(name) for (name, hex) in matplotlib.colors.cnames.items()]
    primarycolorlist = ['green','blue','red','cyan','orange', 'yellow','violet']
    return primarycolorlist + [c for c in colorlist if c not in primarycolorlist]
