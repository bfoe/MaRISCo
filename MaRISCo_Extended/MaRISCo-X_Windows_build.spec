# -*- mode: python -*-
a = Analysis(['MaRISCo-X.py'],
             excludes=[ 'win32pdh','win32pipe',
                        'multiprocessing', 'ctypes', 'socket', 'bz2',
                        'select', 'pydoc', 'pickle', '_hashlib', '_ssl',
                        'setuptools', 'pyexpat', 'unicodedata', '_bsddb',
                        'PIL._webp'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
             
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
a.binaries += [('RGBA.tif', 'RGBA.tif', 'DATA')]           
a.datas = [x for x in a.datas if not ('tk8.5\msgs' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tk8.5\images' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tk8.5\demos' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\opt0.4' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\http1.0' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\encoding' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('tcl8.5\msgs' in os.path.dirname(x[1]))]            
a.datas = [x for x in a.datas if not ('\\tzdata' in os.path.dirname(x[1]))]   
        
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MaRISCo-X.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False, icon='MaRISCo-X.ico')          

