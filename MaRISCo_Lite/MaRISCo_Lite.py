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


# ========================== IMPORT EXTERNAL SUBROUTINES =====================

import os;
import sys;
import random
import time;
from math import exp;
from operator import add, mul, abs;
# Python Imaging Library (PIL), alternative "pillow"
try: 
    from PIL import Image;
    if Image.VERSION == '1.1.6':
        print("Warning: old PIL library found, upgrade recomended");   
except: 
    print("Error: PIL library not found, fallback to internal alternative");
    print("       to install PIL see http://www.pythonware.com/products/pil");
    print("       on linux simply try `yum install python-imaging-tk`");    
    print("       to install `pillow` (a dropin PIL fork) see http://python-pillow.org/");
    print("       and follow the release link to http://pypi.python.org/pypi/Pillow/");
    sys.exit(1);       
try: 
    from PIL import ImageTk; 
except: 
    print("Error: additional PIL library `python-imaging-tk` not found ");
    print("       on linux simply try `yum install python-imaging-tk`");
    print("           or respectively `yum install python3-pil.imagetk`");    
    sys.exit(1);   
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

# =============================== CONSTANTS ==================================

# predefined Tissue Parameters, taken from:
# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2822798/
T1_GM_def  = 1034;  T1_WM_def  = 660;   T1_CSF_def = 4000;
T2_GM_def  = 93;    T2_WM_def  = 73;    T2_CSF_def = 2470;
PD_GM_def  = 0.78;  PD_WM_def  = 0.65;  PD_CSF_def = 0.97;

# predefined initial parameters
TE_def = 10;    # default echo time
TR_def = 200;   # default repetition time
TI_def = 0;     # default inversion time
Slice_def = 67; # default slice location
W_def = 1.0     # default window (for intercative W/L adjust)
L_def = 0.5     # default level  (for intercative W/L adjust)
zoom_target=2.5 # image zoom factor (relative to 1mm resolution)

# ========================= SUBROUTINE DEFINITIONS ===========================

def calcATT (T1, T2, PD, TE, TR, TI):
    # convert to flaot to avoid rounding errors
    T1=float(T1); T2=float(T2); PD=float(PD);
    TE=float(TE); TR=float(TR); TI=float(TI);
    # calculate and return value
    if TI==0: return PD * exp(-TE/T2) * (1-exp(-(TR-TE)/T1));
    else: return PD * exp(-TE/T2) * (1-2*exp(-TI/T1)+exp(-(TR-TE)/T1));

def calcImg (slice,te, tr, ti):
    global NoiseData, last_slice, data, data_raw, data_CSF_raw, data_GM_raw, data_WM_raw
    # calculate attenuation factors (255. is the max intensity in the import image)
    GM_att  = calcATT (T1_GM_def, T2_GM_def, PD_GM_def, te, tr, ti)/255.;    
    WM_att  = calcATT (T1_WM_def, T2_WM_def, PD_WM_def, te, tr, ti)/255.;    
    CSF_att = calcATT (T1_CSF_def, T2_CSF_def, PD_CSF_def, te, tr, ti)/255.;
    if slice != last_slice:
        img.seek(total_slices-slice);               # slicenumber
        img_CSF, img_GM, img_WM = img.split()       # sepatate tissues
        img_CSF = img_CSF.convert(mode='F')         # convert CSF image to mode float
        img_GM = img_GM.convert(mode='F')           # convert GM  image to mode float
        img_WM = img_WM.convert(mode='F')           # convert WM  image to mode float
        data_CSF_raw = list(img_CSF.getdata());     # convert to list 
        data_GM_raw  = list(img_GM.getdata());      # convert to list 
        data_WM_raw  = list(img_WM.getdata());      # convert to list      
        last_slice = slice
    # calculate new image
    data_CSF = [f * CSF_att for f in data_CSF_raw]; # normalize to 1.0 and multiply with ATT
    data_GM  = [f * GM_att for f in data_GM_raw];   # normalize to 1.0 and multiply with ATT
    data_WM  = [f * WM_att for f in data_WM_raw];   # normalize to 1.0 and multiply with ATT
    data_raw = map(add, data_CSF, data_GM); data_raw = map(add, data_raw, data_WM) # add
    data = data_raw
    if RecalcNoise:
        # add some noise
        min_= min (data); max_= max (data)
        n_level1 = max ([abs(max_), abs(min_)])
        n_level1 += 0.1  # amount of minimum hardware noise
        n_level1 *= 0.01 # amount of noise that scales linear with normalization (attenuator)
        n_level2 = 0.01  # simple model for physiological noise
        random.shuffle(Noise_Ref); 
        # sumation of the levels referencing to a single noise source is not strictly correct
        # correct would be referencing separate noise sources each with its own level, then sum
        # this would sum the noise levels in an incorrent way
        # the way it stands below noise sources are addad coherently, results are sligtly larger
        # but this is WAY faster
        NoiseData = map(mul, [n_level1+n_level2*abs(f) for f in data], Noise_Ref); #fastest
    data = map(add, data, NoiseData) # add noise
    # Magnitude versus Real part Images (deal with negative values)   
    if ReImg_tkVar.get()==0: data = [abs(f) for f in data] # Magnitude Image
    else: min_= min (data); data = [f-min_ for f in data]; # Re Image: shift to positive
    # normalization, WL, scaling to 220 --> all in one for speed (initial values W=1.0; L=0.5)
    normalization=max(data);
    if normalization == 0: normalization=sys.float_info.min;
    data = [((f/normalization-L)/W+0.5)*220. for f in data];
    data = [0 if f<0 else f for f in data];
    data = [220. if f>220. else f for f in data];
    return data;
      
def UpdateImg (slice,te, tr, ti):
    data = calcImg(slice,te, tr, ti); # this does all the work
    if Start<=1:             # not yet started
        if Start==1: return; # inside start animation
        im = img.resize ([zoom_X,zoom_Y], resample=Image.BICUBIC);
        try: 
            imageTk=ImageTk.PhotoImage(im);
            IMG_tkLabel.configure(image=imageTk); # image redisplaying    
            IMG_tkLabel.image = imageTk;          # keep a reference!
        except: pass # may happen when missing python-imaging-tk
        return
    # display image
    im = Image.new('F', (IMAGEWIDTH, IMAGELENGTH))
    im.putdata(data)
    im = im.resize ([zoom_X,zoom_Y], resample=Image.BICUBIC);
    try:
        imageTk=ImageTk.PhotoImage(im);
        IMG_tkLabel.configure(image=imageTk); # image redisplaying
        IMG_tkLabel.image = imageTk;          # keep a reference!
    except: pass # may happen when missing python-imaging-tk

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
    UpdateImg(SL,TE, TR, TI);   # update image
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
    UpdateImg(SL,TE, TR, TI);   # update image
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
    UpdateImg(SL,TE, TR, TI);   # update image
    TI_tkScale.focus();    
  
def validateSL (SL):
    global RecalcNoise;
    SL = int(SL);               # convert to int
    TE = int(TE_tkVar.get());   # get TE
    TR = int(TR_tkVar.get());   # get TR
    TI = int(TI_tkVar.get());   # get TI
    RecalcNoise=True;
    UpdateImg(SL,TE, TR, TI);   # update image
    SL_tkScale.focus();

def validateRE ():              # just a wrapper
    global RecalcNoise;
    TE = int(TE_tkVar.get());   # get TE
    TR = int(TR_tkVar.get());   # get TR
    TI = int(TI_tkVar.get());   # get TI
    SL = int(SL_tkVar.get());   # get SL
    RecalcNoise=False;
    UpdateImg(SL,TE, TR, TI);   # update image

def mouse_left_click(event): # to reset W/L 
    global W, L;             # to pass values after reset to "def updateImg"
    if Start==0: return     # permit adjust only after start    
    W = W_def; L=L_def;      # reset to defaults
    validateRE ();
    
def mouse_right_click(event): # get initial position
    global x_click, y_click;  # to pass values after initial click to "def mouse_right_move"
    if Start==0: return     # permit adjust only after start    
    x_click = event.widget.winfo_pointerx()
    y_click = event.widget.winfo_pointery()
    
def mouse_right_move(event): # read motion relative to initial position
    global W, L;             # to pass values after adjust to "def updateImg" 
    global x_click, y_click;
    if Start==0: return     # permit adjust only after start    
    step_x=0.002; step_y=0.001;
    x_move = float(event.widget.winfo_pointerx()-x_click)*step_x;
    y_move = float(event.widget.winfo_pointery()-y_click)*step_y;
    x_click = event.widget.winfo_pointerx()
    y_click = event.widget.winfo_pointery()
    W -= x_move;
    L -= y_move;
    if W<=0: W=1e-10; # required to avoid division by zero
    validateRE ();

def image_motion(event): # to reset W/L
    x=int(event.x); y=int(event.y); 
    x_str = str(x); blanks = ' '*max(4-len(x_str),1); x_str += blanks;
    y_str = str(y); blanks = ' '*max(4-len(y_str),1); y_str += blanks;
    x_raw=int(x/pixdim_x/zoom_target);
    y_raw=int(y/pixdim_y/zoom_target);
    s=data_raw[x_raw+y_raw*IMAGEWIDTH];
    wm=data_WM_raw[x_raw+y_raw*IMAGEWIDTH]/255.*100; wm_str = ("%4.1f" %wm);
    if wm_str=="100.0": wm_str=" 100";
    gm=data_GM_raw[x_raw+y_raw*IMAGEWIDTH]/255.*100; gm_str = ("%4.1f" %gm);
    if gm_str=="100.0": gm_str=" 100";
    csf=data_CSF_raw[x_raw+y_raw*IMAGEWIDTH]/255.*100; csf_str = ("%4.1f" %csf);
    if csf_str=="100.0": csf_str=" 100";  
    text = " X=%sY=%s WM/GM/CSF =%s/%s/%s%%" % (x_str, y_str, wm_str, gm_str, csf_str)
    if Start>0: # doesn't make sense to display signal before
        text += "   Signal=%.2f" % (s)
    INF_tkVar.set(text);
    
def image_leave(event): # to reset W/L   
    INF_tkVar.set('');  
       
def START(event):
    global RecalcNoise, Start;
    Start=1;
    START_tkText.grid_forget();
    root.update(); # update GUI
    # get startup RGB image
    steps=20;
    for i in range (0, steps):     
        # calc grayscale image for blending
        im2 = Image.new('F', (IMAGEWIDTH, IMAGELENGTH));
        data = calcImg(SL_tkVar.get(),TE_tkVar.get(), TR_tkVar.get(), TI_tkVar.get());
        im2.putdata(data);
        im2 = im2.resize ([zoom_X,zoom_Y], resample=Image.BICUBIC);
        im2 = im2.convert(mode='RGB');
        RecalcNoise = False;
        # get RGB image for blending
        im1 = img.resize ([zoom_X,zoom_Y], resample=Image.BICUBIC);        
        # animation
        try: root.winfo_exists()
        except: sys.exit(1); # somebody killed the app ;)
        imageTk=ImageTk.PhotoImage(Image.blend(im1,im2,(i+1)/float(steps)));
        IMG_tkLabel.configure(image=imageTk); # image redisplaying
        IMG_tkLabel.update_idletasks();       # update GUI
        IMG_tkLabel.image = imageTk;          # keep a reference!
        root.update(); #root.update_idletasks();        
        time.sleep(0.005);   
    Start=2;   
    UpdateImg(SL_tkVar.get(),TE_tkVar.get(), TR_tkVar.get(), TI_tkVar.get()); # update image

# ========================= MAIN PROGRAM STARTS HERE =========================

# initialize tk
Start = 0
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
    
# read input file
try: 
    # extract infos  
    img = Image.open(resourcedir+'RGB.tif');
    img.load() # required to be able to split R/G/B=CSF/GM/WM
    try: # prefer to read directly the TIF tags
        IMAGEWIDTH   = img.tag.tags[256][0];
        IMAGELENGTH  = img.tag.tags[257][0];
    except: # if not present (depends on PIL/pillow implementation)
        IMAGEWIDTH, IMAGELENGTH = img.size
    try: # prefer to read directly the TIF tags
        x_resolution = img.tag.tags[282];  # in DPI
        y_resolution = img.tag.tags[283];  # in DPI
        pixdim_x = float(x_resolution[0][1])/float(x_resolution[0][0]);
        pixdim_y = float(y_resolution[0][1])/float(y_resolution[0][0]);
    except: # if not present (depends on PIL/pillow implementation)
        pixdim_x, pixdim_y = img.info['resolution']
        pixdim_x = 1/pixdim_x
        pixdim_y = 1/pixdim_y
    # calculate parameters from extracted infos 
    total_slices = 0
    while True:
        try: img.seek(total_slices); total_slices += 1
        except EOFError: break; 
    zoom_X=int(IMAGEWIDTH*pixdim_x*zoom_target); # enlarge x 2.5 (used in updateImg)
    zoom_Y=int(IMAGELENGTH*pixdim_y*zoom_target); # enlarge y 2.5 (used in updateImg)
except: 
    root.withdraw(); 
    showerror(Program_name,' Error loading Image file(s)         ');
    sys.exit(1); 
    # you may also come here if the TIF file is OK, but PIL is not installed to read it


# variable Definition & Initialize
W = W_def; L=L_def; # defaults for intercative W/L adjust
last_slice = -1;
SL_tkVar = tk.IntVar(); SL_tkVar.set(Slice_def);
TE_tkVar = tk.IntVar(); TE_tkVar.set(TE_def);
TR_tkVar = tk.IntVar(); TR_tkVar.set(TR_def);
TI_tkVar = tk.IntVar(); TI_tkVar.set(TI_def);
ReImg_tkVar = tk.IntVar(); ReImg_tkVar.set(0);
RecalcNoise = True # RecalcNoiseulated image, if not only W/L update
# pregenerated list of random numbers
# normal distribution, floats between 0.0 and 1.0
Noise_Ref = [random.gauss(0, 1) for f in range (0,IMAGEWIDTH*IMAGELENGTH)];
NoiseData = [0 for f in range (0,IMAGEWIDTH*IMAGELENGTH)];
# Image placeholder
IMG_tkLabel=tk.Label(text='Image initialisation failed\n\ninstall PIL\n&\npython-imaging-tk', bd=0, cursor='crosshair');
# Image info text
INF_tkVar = tk.StringVar(); INF_tkVar.set('');
INF_tkLabel=tk.Label(textvariable=INF_tkVar, bd=0, font=('Courier', 8), width=0);
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
    length=zoom_Y-24, showvalue='no', orient='vertical');
SL_tkLabel  = tk.Label(root, font=('Helvetica', 8), textvariable=SL_tkVar);
# Layout
# ---------------------------------------
# | Slice number |   Image   |    <     |
# | Slice slider |     ^     |    <     |
# |              | ImageInfo |    <     |
# |     TE label | TE slider |    <     |
# |     TR label | TR slider |    <     |
# |     TT label | TI slider | ReImgBox |
# ---------------------------------------
SL_tkLabel.grid (row=0, column=0);             # Slice number 
SL_tkScale.grid (row=1, column=0, sticky="NW"); # Slice slider
IMG_tkLabel.grid(row=0, rowspan=2, column=1, columnspan=2);  # Image
INF_tkLabel.grid(row=2, column=1, columnspan=2, sticky="W");  # Image Info text
TE_tkLabel.grid (row=3, column=0, sticky="W"); # TE label
TE_tkScale.grid (row=3, column=1, columnspan=2, sticky="E"); # TE slider
TR_tkLabel.grid (row=4, column=0, sticky="W"); # TR label
TR_tkScale.grid (row=4, column=1, columnspan=2, sticky="E"); # TR slider
TI_tkLabel.grid (row=5, column=0, sticky="W"); # TI label
TI_tkScale.grid (row=5, column=1, sticky="W"); # TI slider
ReImg_tkBox.grid(row=5, column=2, sticky="W"); # Realpart Image checkBox
# START Text (used as a Button with variable text styles) covers the above while active
START_tkText  = tk.Text(root, bg=sysbg, height=0, width=0, relief=tk.RAISED, cursor='arrow');
START_tkText.tag_configure('norm', font=('Helvetica', 12), justify='center');
START_tkText.tag_configure('bold', font=('Helvetica', 12, 'bold'), justify='center');
START_tkText.tag_configure('big',  font=('Helvetica', 26), justify='center');
START_tkText.insert(tk.END, '\n   ', 'norm');
START_tkText.insert(tk.END, 'Ma', 'bold'); START_tkText.insert(tk.END, 'gnetic ', 'norm');
START_tkText.insert(tk.END, 'R', 'bold'); START_tkText.insert(tk.END, 'esonance ', 'norm');
START_tkText.insert(tk.END, 'I', 'bold'); START_tkText.insert(tk.END, 'mage ', 'norm');
START_tkText.insert(tk.END, 'S', 'bold'); START_tkText.insert(tk.END, 'imulation ', 'norm');
START_tkText.insert(tk.END, 'C', 'bold'); START_tkText.insert(tk.END, 'alculat', 'norm');
START_tkText.insert(tk.END, 'o', 'bold'); START_tkText.insert(tk.END, 'r', 'norm');
START_tkText.insert(tk.END, '\n\n\n', 'norm');
START_tkText.insert(tk.END, 'Start', 'big');
START_tkText.configure(state="disabled")
START_tkText.grid (row=3,  rowspan=3, column=0, columnspan=3, sticky="nsew");
START_tkText.bind("<Button-1>",  START)
# this is for window/leveling
IMG_tkLabel.bind("<Button-1>",  mouse_left_click)
IMG_tkLabel.bind("<Button-3>",  mouse_right_click)
IMG_tkLabel.bind("<B3-Motion>", mouse_right_move)
# this is for image info display
IMG_tkLabel.bind("<Motion>",  image_motion)
IMG_tkLabel.bind("<Leave>",  image_leave)
# update and go ...
UpdateImg(int(SL_tkVar.get()), int(TE_tkVar.get()), int(TR_tkVar.get()), int(TI_tkVar.get()));

root.mainloop()
