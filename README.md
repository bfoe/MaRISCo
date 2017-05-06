<h1>MaRISCo</h1><p>
&emsp; <b>Ma</b>gnetic <b>R</b>esonance <b>I</b>mage <b>S</b>imulation <b>C</b>alculat<b>o</b>r<br>
&emsp; &emsp;&emsp; ( portuguese "marisco" translates to "mussels" or "seafood" ;)<br>
<br></p>
<h2>Purpose:</h2><p>
&emsp; Interactively calculate a synthetic MR image based on:<br>
&emsp;&emsp; - previously segmented WM/GM/CSF images (included)<br>
&emsp;&emsp; - literature values for tissue parameters T1/T2/PD, and<br>
&emsp;&emsp; - user adjustable sequence parameters TE/TR/TI<br>
&emsp;&nbsp; Use for educational purposes to demonstrate how the choice of<br>
&emsp;&nbsp; acquisition parameters influence the image contrast and quality.<br>
<br></p>
<h2>Requirements:</h2><p>
&emsp; <a href="http://www.python.org">Python</a> which normally already includes <a href="http://wiki.python.org/moin/TkInter">TkInter</a><br>
&emsp; plus the additional Python modules 
<a href="http://www.numpy.org">Numpy</a><b>, </b>
<a href="http://nipy.org/nibabel">NiBabel</a> <br>
&emsp; and 
<a href="http://www.pythonware.com/products/pil">PIL</a> or it's fork 
<a href="http://python-pillow.org/">pillow</a><br>
<br></p>
<h2>License:</h2><p>
&emsp; <a href="http://www.gnu.org/licenses">GPLv3</a><br>
<br></p>
<h2>References:</h2><p>
&emsp; Tissue parameters:<br>
&emsp;&emsp;&emsp; <b>G</b>ray <b>M</b>atter &emsp;&emsp; <b>W</b>hite <b>M</b>atter &emsp;&emsp; <b>C</b>erebro<b>S</b>pinal <b>F</b>luid<br>
&emsp;&emsp;&emsp; T1 = 1034ms &nbsp;&emsp; T1 = 660ms &emsp;&emsp;&nbsp;&nbsp; T1 = 4000ms<br>
&emsp;&emsp;&emsp; T2 = 93ms &emsp;&emsp;&nbsp;&nbsp; T2 = 73ms  &emsp;&emsp;&emsp; T2 = 2470ms<br>
&emsp;&emsp;&emsp; PD = 0.78 &emsp;&emsp;&nbsp;&nbsp;&nbsp; PD = 0.65 &emsp;&emsp;&emsp;&nbsp; PD = 0.97<br>
&emsp;&nbsp; extracted from <a href="http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2822798/">Gasparovic <em>et al</em> J Neurotrauma (2009)</a><br>
<br>
&emsp; Signal equations:<br>
&emsp;&emsp;&emsp; SE &nbsp;= &nbsp;PD &nbsp; * &nbsp; e<sup> -TE/T<sub>2</sub></sup> &nbsp; * &nbsp; ( 1 - e<sup> -(TR-TE)/T<sub>1</sub></sup> )<br>
&emsp;&emsp;&emsp; IR &nbsp;&nbsp;= &nbsp; PD &nbsp; * &nbsp; e<sup> -TE/T<sub>2</sub></sup> &nbsp; * &nbsp; ( 1 - 2e<sup> -TI/T<sub>1</sub></sup> + e <sup> -(TR-TE)/T<sub>1</sub></sup> )<br>
&emsp;&nbsp; from Wikipedia: <a href="http://en.wikipedia.org/wiki/Synthetic_MRI">Synthetic MRI</a><br>
<br>
&emsp; Segmented Images:<br>
&emsp;&emsp; The image displayed was processed based on case #3 of the <a href="http://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/Data">FreeSurfer Tutorial Datasets</a>,<br> 
&emsp;&emsp; the complete set of files can be downloaded directly <a href="http://surfer.nmr.mgh.harvard.edu/pub/data/fsfast-tutorial.subjects.tar.gz">here</a> (caution 3.2GB).<br>
&emsp;&emsp; Segmentation was done with the <a href="http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FAST">FAST</a> tool from FSLv3
<br></p>
<h2>Usage:</h2><p>
&emsp; By changing the slider positions for TE (echo time) and TR (repetition time) you can<br>
&emsp; interactively explore the changes in the image contrast. <br>
&emsp; For example, starting from the initial T1 weighted image at TE/TR = 10/200ms simulate a<br> 
&emsp; T2 weighted image by simply adjusting the sliders to TE/TR = 120/3000ms.<br>
&emsp; Window and Level (W/L) of the image can be adjusted holding down right mouse button while<br>
&emsp; moving over the image, a left click resets to the default W/L value.<br>
<br>
&emsp;&emsp; <img src="Screenshots/T1.jpg" alt="T1 weighted Image" width="200" height="333">
&emsp;&emsp; <img src="Screenshots/T2.jpg" alt="T2 weighted Image" width="200" height="333"><br>
<br>
&emsp; If you click on the grayed out slider at the bottom you can switch from a Spin Echo Sequence<br>
&emsp; to Inversion Recovery and additionally adjust the Inversion time (TI).<br>
&emsp; You can find (several) conditions where the signal for the Cerebrospinal Fluid (CSF) is nulled,<br>
&emsp; for example, like in the images below.<br>
<br>
&emsp;&emsp; <img src="Screenshots/FLAIR.jpg" alt="T2 weighted FLAIR" width="200" height="333">
&emsp;&emsp; <img src="Screenshots/IR_T1.jpg" alt="T1 weighted FLAIR" width="200" height="333"><br>
<br>
&emsp; The setting TE/TR/TI = 150/1200/2500ms is a classical FLAIR condition, where FLAIR stands for<br>
&emsp; "<b>F</b>luid <b>A</b>ttenuated <b>I</b>nversion <b>R</b>ecovery", but you can also find CSF nulled images at around<br>
&emsp; TE/TR/TI = 20/2000/800ms that exhibit T1 contrast, therefore sometimes called T1-FLAIR.<br>
<br>
&emsp; Between these two extreme conditions are images that look somewhat weird, this is because normally<br>
&emsp; MR images are shown in magnitude mode that does not distinguish between positive and negative signals.<br>
&emsp; Though, for certain combinations of TI and TR there may be conditions where some signals have positive<br>
&emsp; signal while others are still negative.<br>
&emsp; In this case one might like to switch from magnitude images to a mode that permits to distinguish between<br>
&emsp; positive and negative signals, the resulting images are sometimes called "Real part Images" and that's what the<br>
&emsp; checkbox bottom-right with the little "R" is for, below two images with identical TE/TR/TI in both modes<br>
<br>
&emsp;&emsp; <img src="Screenshots/IR_Magnitude.jpg" alt="IR magnitude image" width="200" height="333">
&emsp;&emsp; <img src="Screenshots/IR_Real.jpg" alt="IR real part image" width="200" height="333"><br>
<br>
&emsp; The software adds some random noise to the images such that the simulation gives some impression<br> 
&emsp; how real images could look.<br>
&emsp; This is by no means (<b>usual disclaimers apply!</b>) a substitute for adjusting real acquisition parameters<br>
&emsp; on real scanner hardware. But it looks nice, so play around and <b>have fun ;)</b><br></p>
<br></p>
<h2>Advanced usage:</h2><p>
&emsp; You can use your own segmentation results as base for the image simulation:<br>
&emsp; simply substitute the files "CSF.nii.gz", "GM.nii.gz"and "WM.nii.gz".<br> 
<br>
&emsp; <b>ATTENTION:</b> For educational/investigational purposes only, not for clinical use!<br>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp; Simulation does not substitute acquisition of real images! <br></p>
<br>
<h2>Development status:</h2><p>
&emsp; The MaRISCo sources in the root folder are code locked.<br>
&emsp; No further improvements will be implemented, no standalone distributables are provided<br> 
&emsp; This version is to quickly visualize segmentation results from different origins (FSL/SPM etc.).<br>
&emsp; If your intention is purely educational go for one of the following:<br> 
<br>
&emsp; The MaRISCo_Lite version has a smaller footprint while maintaining the main functionality identical,<br>
&emsp; for details see the <a href="https://github.com/bfoe/MaRISCo/tree/master/MaRISCo_Lite">README</a>, 
there are standalone distributables for <a href="https://github.com/bfoe/MaRISCo/raw/master/MaRISCo.exe">Windows</a>
and <a href="https://github.com/bfoe/MaRISCo/raw/master/MaRISCo_MacOS.zip">MacOS</a><br>
&emsp; This version is basically code locked too.<br>
<br>
&emsp; The MaRISCo_Extended version aims to go beyond CSF/GM/WM segmentation,<br>
&emsp; for details see the <a href="https://github.com/bfoe/MaRISCo/tree/master/MaRISCo_Extended">README</a>, 
standalone distributables for <a href="https://github.com/bfoe/MaRISCo/raw/master/MaRISCo-X.exe">Windows</a>
and <a href="https://github.com/bfoe/MaRISCo/raw/master/MaRISCo-X_MacOS.zip">MacOS</a> coming up ...<br>
<br>