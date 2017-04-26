#!/usr/bin/python
#
# Magnetic Resonance Image Simulation Calculator
# (Portuguese marisco is for "mussels" or "seafood" ;)
#
# calculates a synthetic MR image based on:
#   - previousely segmented WM/GM/CSF images
#   - literature values for tissue parameters T1/T2/PD, and
#   - user adjustable sequence parameters TE/TR
#
# just a little programming exercise, for educational purposes
#
# License GPLv3 (http://www.gnu.org/licenses)
# 

import os;
import sys;
from math import exp, log;
# Numpy
try: import numpy as np;
except: 
    print ("Error: NumPy library not found, see http://www.numpy.org");
    print ("       on linux simply try `yum install python-numpy`");           
    sys.exit(1);
# NiBabel
try: import nibabel as nib;
except: 
    print("Warning: NiBabel library not found, fallback to RGB.tif input (requires PIL)");
    print("         to install NiBabel see http://nipy.org/nibabel/installation.html");
    print("         on linux simply try `yum install python-nibabel`");  
# Python Imaging Library (PIL), alternative "pillow"
PIL_installed=True;
try: 
    from PIL import Image;
    if Image.VERSION == '1.1.6':
        print("Warning: old PIL library found, upgrade recomended");      
except: 
    print("Warning: PIL library not found, fallback to internal alternative");
    print("         to install PIL see http://www.pythonware.com/products/pil");
    print("         on linux simply try `yum install python-imaging-tk`");    
    print("         to install `pillow` (a dropin PIL fork) see http://python-pillow.org/");
    print("         and follow the release link to http://pypi.python.org/pypi/Pillow/");
    PIL_installed=False;
try: 
    from PIL import ImageTk; 
except: 
    print("Warning: additional PIL library `python-imaging-tk` not found ");
    print("         on linux simply try `yum install python-imaging-tk`");
    print("             or respectively `yum install python3-pil.imagetk`");      
    PIL_installed=False;    
# Tkinter    
try: import Tkinter as tk;   # Python2
except: 
  try: import tkinter as tk; # Python3
  except: 
    print (\
    "Error: Tkinter/imageTk library not found, see one of the following:\n"+\
    "       - Linux: http://tkinter.unpythonic.net/wiki/How_to_install_Tkinter\n"+\
    "                or simply try `yum install python-tk`\n"+\
    "       - MacOs: http://www.python.org/download/mac/tcltk\n"+\
    "       - Windows: already included with python, http://www.python.org\n"+\
    "                  otherwise: http://www.lfd.uci.edu/~gohlke/pythonlibs\n")
    sys.exit(1);           
try: from tkMessageBox import showerror;       # Python 2
except: pass
try: from tkinter.messagebox import showerror; # Python3
except: pass


# predefined Tissue Parameters, taken from:
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2822798/
T1_GM_def  = 1034;  T1_WM_def  = 660;   T1_CSF_def = 4000;
T2_GM_def  = 93;    T2_WM_def  = 73;    T2_CSF_def = 2470;
PD_GM_def  = 0.78;  PD_WM_def  = 0.65;  PD_CSF_def = 0.97;

# predefined initial parameters
TE_def = 10;
TR_def = 200;
TI_def = 0;
Slice_def = 67;
W_def = 1.0 # default window (for intercative W/L adjust)
L_def = 0.5 # default level  (for intercative W/L adjust)
zoom_target = 2.5 # image zoom factor

def ATT (T1, T2, PD, TE, TR, TI):
    # convert to flaot to avoid rounding errors
    T1=float(T1); T2=float(T2); PD=float(PD);
    TE=float(TE); TR=float(TR); TI=float(TI);   
    # just for safety (negative values should never actually occur)
    T1=abs(T1); T2=abs(T2); PD=abs(PD);
    TE=abs(TE); TR=abs(TR); TI=abs(TI);
    # avoid division by zero
    if T1 == 0: T1 = sys.float_info.min;
    if T2 == 0: T2 = sys.float_info.min;  
    # calculate and return value
    if TI==0: return PD * exp(-TE/T2) * (1-exp(-(TR-TE)/T1));
    else: return PD * exp(-TE/T2) * (1-2*exp(-TI/T1)+exp(-(TR-TE)/T1));

def Update (slice,te, tr, ti):
    global NoiseData
    # calculate attenuation factors
    GM_att  = ATT (T1_GM_def, T2_GM_def, PD_GM_def, te, tr, ti);    
    WM_att  = ATT (T1_WM_def, T2_WM_def, PD_WM_def, te, tr, ti);    
    CSF_att = ATT (T1_CSF_def, T2_CSF_def, PD_CSF_def, te, tr, ti);
    # calculate current slice  
    data =  GM_data[:,:,slice-1]*GM_att; 
    data += WM_data[:,:,slice-1]*WM_att;
    data += CSF_data[:,:,slice-1]*CSF_att;
    if RecalcNoise:
        # add some noise
        max_ = np.amax(np.absolute(data)) + 0.1; # 0.1 is the amount of minimum hardware noise
        NoiseData = np.random.normal(loc=0., scale=0.01*max_, size=data.shape).astype(np.float32);
        NoiseData += np.random.normal(loc=0., scale=0.01, size=data.shape)*data.astype(np.float32);
    data += NoiseData;
    # Magnitude versus Real part Images (deal with negative values)   
    if ReImg_tkVar.get()==0: data = np.absolute(data) # Magnitude Image
    else: min_=np.amin(data); data -= min_; # Re Image: shift to positive
    # normalization    
    max_=np.amax(data);
    if max_>0: data /= max_;
    # W/L
    # default values are W=1.0; L=0.5
    data = (data-L)/W+0.5 # now we have values <0 and >1
    mask0 = data>0.0; data *= mask0; # solved <0
    mask1 = data<=1.0;
    mask1a = data>1.0
    data = data*mask1 + mask1a.astype(int);
    # scaling (max 256 !)
    data *= 220.;
    # display image
    if PIL_installed:
        if Image.VERSION != '1.1.6': # if not bad version go
            imageA = Image.fromarray(data.swapaxes(0, 1)) ;
            imageA = imageA.resize ([zoom_X,zoom_Y], resample=Image.BICUBIC);
            imageTk=ImageTk.PhotoImage(imageA);
        else: imageTk=tk.PhotoImage(data=make_img(NN_zoom(data,zoom_X,zoom_Y))); # PIL fallback
    else: imageTk=tk.PhotoImage(data=make_img(NN_zoom(data,zoom_X,zoom_Y))); # PIL fallback
    IMG_tkLabel.configure(image=imageTk); # image redisplaying
    IMG_tkLabel.image = imageTk;          # keep a reference!
    #print("Slice=%d  -  TE=%d - TR=%d - TI=%d" % (slice, te, tr, ti); # debug
    #if tr<ti+te: print("TR<TI+TE -  Ouch !!!" # debug
        
def validateTE (TE):
    global RecalcNoise;
    TE = int(TE);               # convert to int
    TR = int(TR_tkVar.get());   # get TR
    TI = int(TI_tkVar.get());   # get TI
    SL = int(SL_tkVar.get());   # get Slice
    if TE<1 :                   # uggly fix to avoid TE<1 (in analogy to TR)
        TE=1;                   # uggly fix to avoid TE<1 (in analogy to TR)
        TE_tkVar.set(TE);       # uggly fix to avoid TE<1 (in analogy to TR)
    if TR<TE*2+8:               # TR<TE is wrong py MR pysics
        TR=TE*2+8;              # correct local TR
        TR_tkVar.set(TR);       # correct TR in GUI
    if TR<TI+TE and TI>0:       # TR<TI+TE is wrong py MR pysics
        TR=TI+TE;               # correct local TR
        TR_tkVar.set(TR);       # correct TR in GUI
    RecalcNoise=True;
    Update(SL,TE, TR, TI);      # update
    TE_tkScale.focus();

def validateTR (TR):
    global RecalcNoise;
    TR = int(TR);               # convert to int
    TE = int(TE_tkVar.get());   # get TE
    TI = int(TI_tkVar.get());   # get TI
    SL = int(SL_tkVar.get());   # get Slice
    if TR<10:                   # uggly fix to avoid TR<10 (black/noisy image)
       TR=10;                   # uggly fix to avoid TR<10 (black/noisy image)
       TR_tkVar.set(TR)         # uggly fix to avoid TR<10 (black/noisy image)
    if TR<TE*2+8:               # TR<TE is wrong py MR pysics
        TE=(TR-8)/2;            # correct local TE
        TE_tkVar.set(TE);       # correct TE in GUI
    if TR<TI+TE and TI>0:       # TR<TI+TE is wrong py MR pysics
        TI=TR-TE;               # correct local TI
        TI_tkVar.set(TI);       # correct TI in GUI
    Update(SL,TE, TR, TI);      # update
    RecalcNoise=True;
    TR_tkScale.focus();
    
def validateTI (TI):
    global RecalcNoise;
    TI = int(TI);               # convert to int
    TE = int(TE_tkVar.get());   # get TE
    TR = int(TR_tkVar.get());   # get TR
    SL = int(SL_tkVar.get());   # get Slice
    if TI==0: # for TI=0 gray out GUI info
        if TR>4000: TR=4000; TR_tkVar.set(TR);
        TR_tkScale.configure(from_=0, to=4000, tickinterval=500, 
            resolution=1);
        TI_tkScale.configure(fg=sysbg, troughcolor=sysbg); 
        TI_tkLabel.configure(text='');
        ReImg_tkVar.set(0);
        ReImg_tkBox.configure(fg=sysbg, selectcolor=sysbg, state='disabled');
    else: # for TI>0 show GUI info
        TR_tkScale.configure(from_=0, to=16000, tickinterval=2000, 
            resolution=10);
        TI_tkScale.configure(fg='black', troughcolor=ltgray);
        TI_tkLabel.configure(text='TI ');
        ReImg_tkBox.configure(fg='black', selectcolor=ltgray, state='normal');
    if TR<TI+TE and TI>0:       # TR<TI+TE is wrong py MR pysics
        TR=TI+TE;               # correct local TR
        TR_tkVar.set(TR);       # correct TI in GUI
    RecalcNoise=True;
    Update(SL,TE, TR, TI);      # update
    TI_tkScale.focus();    
  
def validateSL (SL):
    global RecalcNoise;
    SL = int(SL);               # convert to int
    TE = int(TE_tkVar.get());   # get TE
    TR = int(TR_tkVar.get());   # get TR
    TI = int(TI_tkVar.get());   # get TI
    RecalcNoise=True;
    Update(SL,TE, TR, TI);      # update
    SL_tkScale.focus();

def validateRE ():              # just a wrapper
    global RecalcNoise;
    TE = int(TE_tkVar.get());   # get TE
    TR = int(TR_tkVar.get());   # get TR
    TI = int(TI_tkVar.get());   # get TI
    SL = int(SL_tkVar.get());   # get SL
    RecalcNoise=False;
    Update(SL,TE, TR, TI);      # update

def mouse_left_click(event): # to reset W/L 
    global W, L;             # to pass values after reset to "def Update" 
    W = W_def; L=L_def;      # reset to defaults
    validateRE ();
    
def mouse_right_click(event): # get initial position
    global x_click, y_click;  # to pass values after initial click to "def mouse_right_move"
    x_click = event.widget.winfo_pointerx()
    y_click = event.widget.winfo_pointery()
    
def mouse_right_move(event): # read motion relative to initial position
    global W, L;             # to pass values after adjust to "def Update" 
    global x_click, y_click;
    step_x=0.002; step_y=0.001;
    x_move = float(event.widget.winfo_pointerx()-x_click)*step_x;
    y_move = float(event.widget.winfo_pointery()-y_click)*step_y;
    x_click = event.widget.winfo_pointerx()
    y_click = event.widget.winfo_pointery()
    W -= x_move;
    L -= y_move;
    if W<=0: W=1e-10; # This really is required to avoid division by zero
    # ----------------------------------------------------
    # below are the conditions for strict W/L handling
    # however aperently these are not commonly implemented
    # therefor disabled, until further considerations
    # ----------------------------------------------------
    # advanced boundary conditions
    #if L+0.5*W>1.: L=1.-0.5*W          # either this
    #if L-0.5*W<0.: L=0.5*W             # and that
    #if L+0.5*W>1.: W=(1.-L)/0.5       # or this
    #if L-0.5*W<0.: W=L/0.5            # and that
    # simple boundary conditions
    #if L>1: L=1.
    #if L<step_y: L=step_y
    #if W>1: W=1.
    #if W<step_x: W=step_x
    validateRE ();

def make_img (data):
    # converts a 2D numpy float array into an image for tk.PhotoImage
    # tk.PhotoImage is the plain vanilla tkinter implementation
    # PIL.ImageTk.PhotoImage is what we are actually using
    # leave the code as fallback , in case PIL does not work 
    x=data.shape[0]
    y=data.shape[1]
    min_=np.amin(data); data -= min_ # shift to min = 0
    max_=np.amax(data);
    if max_>0: data /= max_; # normalize to 1
    data *= 191 #191 is max for tk.PhotoImage, PIL can deal with 254 (255?)
    data_int = data.astype(np.int32).swapaxes(0, 1).flatten()
    data_str = "".join([chr(item) for item in data_int])
    header_str = "P5 "+str(x)+" "+str(y)+" 255 "
    return header_str+data_str

def NN_zoom (inp,x,y): 
    # simple 2D implementation for Nearest Neighbour interpolation
    # drop-in replacement for PIL.Image.resize
    # fallback in case PIL fails to import (if PIL_installed = False)
    # PIL is faster, and has a bicubic interpolation
    scale_x = x/float(inp.shape[0]); scale_y = y/float(inp.shape[1]);
    tmp = np.zeros([x,inp.shape[1]], dtype=type(inp[0,0]));
    for i in range (0,x): tmp[i,:]=inp[int(i/scale_x),:];
    out = np.zeros([x,y], dtype=type(inp[0,0]));
    for j in range (0,y): out[:,j]=tmp[:,int(j/scale_y)];
    return out
    # tought the following would be faster
    # but its actually ~50% slower
    ##scale_x = x/float(inp.shape[0]); scale_y = y/float(inp.shape[1]);
    ##ix = np.zeros(x, dtype=int); iy = np.zeros(y, dtype=int);
    ##for i in range (0,x): ix[i]=int(i/scale_x);
    ##for j in range (0,y): iy[j]=int(j/scale_y);
    ##return inp[np.ix_(ix,iy)] # 
    
# ========================= MAIN PROGRAM STARTS HERE =========================

# initialize tk
root = tk.Tk(); 
Program_name = os.path.basename(sys.argv[0]);
root.resizable(width=False, height=False)
root.title(Program_name[:Program_name.find('.')]);
ltgray='#dbdbdb'; sysbg = root.cget('bg');

# path to image files:
if sys.platform=="win32": slash='\\'
else: slash='/'
try: resourcedir = sys._MEIPASS+slash # when on PyInstaller 
except: # in plain python this is where the script was run from
    resourcedir = os.path.abspath(os.path.dirname(sys.argv[0]))+slash; 

try: # try reading input file from NIFTI's
    # extract infos from GM
    GM_image = nib.load(resourcedir+'GM.nii.gz');
    data_pixdim = GM_image.get_header().get_zooms()
    GM_data = GM_image.get_data();
    data_dim = GM_data.shape
    total_slices = data_dim[2];
    zoom_X=int(data_dim[0]*data_pixdim[0]*zoom_target); # enlarge x 2.5 (used in Update)
    zoom_Y=int(data_dim[1]*data_pixdim[1]*zoom_target); # enlarge x 2.5 (used in Update) 
    # read WM, CSF   
    WM_data = nib.load(resourcedir+'WM.nii.gz').get_data();
    CSF_data = nib.load(resourcedir+'CSF.nii.gz').get_data();
    # reformat data
    GM_data  = GM_data [:,::-1,::-1]; # flip AP and reverse slice order
    WM_data  = WM_data [:,::-1,::-1]; # flip AP and reverse slice order
    CSF_data = CSF_data [:,::-1,::-1];# flip AP and reverse slice order
except:
    try: # try reading input file from RGB tif
        # extract infos  
        img = Image.open(resourcedir+'RGB.tif');
        try:
            IMAGEWIDTH   = img.tag.tags[256][0];
            IMAGELENGTH  = img.tag.tags[257][0];
        except:
            IMAGEWIDTH, IMAGELENGTH = img.size
        try:
            x_resolution = img.tag.tags[282];  # in DPI
            y_resolution = img.tag.tags[283];  # in DPI
            pixdim_x = float(x_resolution[0][1])/float(x_resolution[0][0]);
            pixdim_y = float(y_resolution[0][1])/float(y_resolution[0][0]);
        except: 
            pixdim_x, pixdim_y = img.info['resolution']
            pixdim_x = 1/pixdim_x
            pixdim_y = 1/pixdim_y
        # read data
        all_data = np.array(img)[..., np.newaxis];
        error=False; i=0;
        while not error:
          try:
            i += 1;
            img.seek(i);
            all_data = np.append(all_data, np.atleast_3d(np.array(img)[..., np.newaxis]), axis=3);
          except:
            error=True;
        GM_data  = all_data.astype(np.float32)[:,:,1,:]/255.;
        WM_data  = all_data.astype(np.float32)[:,:,2,:]/255.;
        CSF_data = all_data.astype(np.float32)[:,:,0,:]/255.;
        # reformat data
        GM_data = np.swapaxes(GM_data, 0, 1);   # swap RL-AP
        WM_data = np.swapaxes(WM_data, 0, 1);   # swap RL-AP
        CSF_data = np.swapaxes(CSF_data, 0, 1); # swap RL-AP        
        GM_data  = GM_data [:,:,::-1];          # reverse slice order
        WM_data  = WM_data [:,:,::-1];          # reverse slice order
        CSF_data = CSF_data [:,:,::-1];         # reverse slice order
        # calculate parameters from extracted infos 
        total_slices = all_data.shape[3];
        zoom_X=int(CSF_data.shape[0]*pixdim_x*zoom_target); # enlarge x 2.5 (used in Update)
        zoom_Y=int(CSF_data.shape[1]*pixdim_y*zoom_target); # enlarge y 2.5 (used in Update)
    except: 
        root.withdraw(); 
        showerror(Program_name,' Error loading Image file(s)         ');
        sys.exit(1); 
        # you may also come here if the TIF file is OK, but PIL is not installed to read it


# variable Definition & Initialize
W = W_def; L=L_def; # defaults for intercative W/L adjust
SL_tkVar = tk.IntVar(); SL_tkVar.set(Slice_def);
TE_tkVar = tk.IntVar(); TE_tkVar.set(TE_def);
TR_tkVar = tk.IntVar(); TR_tkVar.set(TR_def);
TI_tkVar = tk.IntVar(); TI_tkVar.set(TI_def);
ReImg_tkVar = tk.IntVar(); ReImg_tkVar.set(0);
RecalcNoise = True # RecalcNoiseulated image, if not only W/L update
NoiseData   = 0    # initial definiton of global variable
# Image placeholder
IMG_tkLabel=tk.Label(text='init');
# tk.Scale slider for TE 
TE_tkScale = tk.Scale(root, command=validateTE, variable=TE_tkVar, 
    from_=0, to=250, tickinterval=25, resolution=1, 
    fg='black', troughcolor=ltgray, highlightcolor=sysbg, font=('Helvetica', 8), 
    length=zoom_X, showvalue='yes', orient='horizontal');
TE_tkLabel = tk.Label(root, text='TE ');
# tk.Scale slider for TR
TR_tkScale = tk.Scale(root, command=validateTR, variable=TR_tkVar, 
    from_=0, to=4000, tickinterval=500, resolution=1, 
    fg='black', troughcolor=ltgray, highlightcolor=sysbg, font=('Helvetica', 8), 
    length=zoom_X, showvalue='yes', orient='horizontal');
TR_tkLabel = tk.Label(root, text='TR ');
# tk.Scale slider for TI
TI_tkScale = tk.Scale(root, command=validateTI, variable=TI_tkVar, 
    from_=0, to=3000, tickinterval=500, resolution=1, 
    fg='black', troughcolor=ltgray, highlightcolor=sysbg, font=('Helvetica', 8), 
    length=zoom_X-40, showvalue='yes', orient='horizontal');
TI_tkLabel = tk.Label(root, text='TI ');
ReImg_tkBox = tk.Checkbutton(root, command=validateRE, variable=ReImg_tkVar,
    text = 'R', onvalue=1, offvalue=0);
# tk.Scale slider for Slice 
SL_tkScale = tk.Scale(root, command=validateSL, variable=SL_tkVar, 
    from_=1, to=total_slices, resolution=1, 
    fg='black', troughcolor=ltgray, highlightcolor=sysbg,
    length=zoom_Y-16, showvalue='no', orient='vertical');
SL_tkLabel  = tk.Label(root, font=('Helvetica', 8), textvariable=SL_tkVar);
# Layout
# ---------------------------------------
# | Slice number |   Image   |    <     |
# | Slice slider |     ^     |    <     |
# |     TE label | TE slider |    <     |
# |     TR label | TR slider |    <     |
# |     TT label | TI slider | ReImggBox |
# ---------------------------------------
SL_tkLabel.grid (row=0, column=0);             # Slice number 
SL_tkScale.grid (row=1, column=0, sticky="W"); # Slice slider
IMG_tkLabel.grid(row=0, column=1, columnspan=2, rowspan=2);  # Image
TE_tkLabel.grid (row=2, column=0, sticky="W"); # TE label
TE_tkScale.grid (row=2, column=1, columnspan=2, sticky="E"); # TE slider
TR_tkLabel.grid (row=3, column=0, sticky="W"); # TR label
TR_tkScale.grid (row=3, column=1, columnspan=2, sticky="E"); # TR slider
TI_tkLabel.grid (row=4, column=0, sticky="W"); # TI label
TI_tkScale.grid (row=4, column=1, sticky="W"); # TI slider
ReImg_tkBox.grid(row=4, column=2, sticky="W"); # Realpart Image checkBox
# this could be used for window/leveling (not actually implemented)
IMG_tkLabel.bind("<Button-1>",  mouse_left_click)
IMG_tkLabel.bind("<Button-3>",  mouse_right_click)
IMG_tkLabel.bind("<B3-Motion>", mouse_right_move)
# update and go ...
Update(int(SL_tkVar.get()), int(TE_tkVar.get()), int(TR_tkVar.get()), int(TI_tkVar.get()));

root.mainloop()
