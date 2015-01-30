"""
 ccdproc

 This is a generic CCD image processing program.

 INPUTS:
  input       The input list of images.
  optional keyword arguments:
  =xTalk
  =linCorr    Apply linearity correction
  =fixPix
  =zero
  =flat
  =illum      Apply
  =bootstrap  Apply bootstrap correction.
  =bpm        Apply bad pixel mask using
  optional boolean keyword arugments:
  /trim
  /overscan
  /clobber
  /silent     Don't print anything to the screen.

 OUTPUTS:
  =error      Error if one occured.


 By D.Nidever  Jan 2014,  based in part on IRAF's ccdproc program
"""
#KENZA - Q: what is editgain?
#KENZA - Q: is gainCorr a dead variable?
#KENZA - Q: is verbose a dead variable?

import os.path

def ccdproc(input, xTalk='', linCorr='', fixPix='', zero='', flat='', \
                illum='', bootstrap='', bpm='', trim=False, overscan=False, \
                clobber=False, silent=False):


#====================
# CHECK THE INPUTS
#====================
# Load the input files
    loadinput(input, files, count=nFiles)
#KENZA - Check loadinput later
    files.strip()
    if nFiles==0:
        error = 'No files to process'
        if not silent: print error
        return error

    # No processing steps requested
    if not trim and not overscan and len(xTalk)==0 \ 
#not kwargs['fixPix'] and 
#linCorr=linCorr,fixPix=fixPix,bootstrap=bootstrap,bpm=bpm,
            and len(zero)==0 and len(flat)==0 and len(illum)==0:
#KENZA - Q: 'and and'?
#KENZA - Q: why check if 'fixPix' is set as a keyword? isn't it a value???
#KENZA - Q: should we check linCorr, bootstrap, bpm value too?
        error = 'NO PROCESSING STEPS'
        if not silent: print error
        return error


# Get file information
#   this also works if there is no input or the file doesn't exist
xTalk_info = ccdproc_fileinfo(xTalk)
linCorr_info = ccdproc_fileinfo(linCorr)
fixPix_info = ccdproc_fileinfo(fixPix)
zero_info = ccdproc_fileinfo(zero)
flat_info = ccdproc_fileinfo(flat)
illum_info = ccdproc_fileinfo(illum)
bootstrap_info = ccdproc_fileinfo(bootstrap)
bpm_info = ccdproc_fileinfo(bpm)

# Check that files exist if input
if len(xTalk)>0 and os.path.isfile(xTalk_info):
    error = 'XTALK file '+xTalk_info.file+' NOT FOUND'
if len(linCorr)>0 and os.path.isfile(linCorr_info):
    error = 'LINCORR file '+linCorr_info.file+' NOT FOUND'
if len(fixPix)>0 and os.path.isfile(fixPix_info):
    error = 'FIXPIX file '+fixPix_info.file+' NOT FOUND'
if len(zero)>0 and os.path.isfile(zero_info):
    error = 'ZERO file '+zero_info.file+' NOT FOUND'
if len(flat)>0 and os.path.isfile(flat_info):
    error = 'FLAT file '+flat_info.file+' NOT FOUND'
if len(illum)>0 and os.path.isfile(illum_info):
    error = 'ILLUM file '+illum_info.file+' NOT FOUND'
if len(bootstrap)>0 and os.path.isfile(bootstrap_info):
    error = 'Bootstrap file '+bootstrap_info.file+' NOT FOUND'
if len(bpm)>0 and os.path.isfile(bpm_info):
    error = 'BPM file '+bpm_info.file+' NOT FOUND'
if len(error)>0:
  if not silent: print error
  return error


# That that NEXTEND for the cal files is big enough for the input files
#=========================================
# LOAD CALIBRATION DATA USED BY ALL FILES
#=========================================

# Load bootstrap file
if len(bootstrap)>0:
  CCDPROC_LOADBOOTSTRAP,bootstrap,bootstr,error=error,silent=silent
  if error!='': return

# Load xTalk values
if len(xTalk)>0:
  CCDPROC_LOADXTALK,xTalk,xstr,error=error,silent=silent
  if error!='': return

# Load fixPix file
if len(fixPix)>0:
  CCDPROC_LOADFIXPIX,fixPix,fixstr,error=error,silent=silent
  if error!='': return


# Print out processing steps
if not silent: print 'Processing steps:'
  if len(xTalk)>0: print 'XTALK ',xTalk
  if len(linCorr)>0: print 'LINCORR ',linCorr
  if len(fixPix)>0: print 'FIXPIX ',fixPix
  if zero!='': print 'ZERO ',zero
  if flat!='': print 'FLAT ',flat
  if illum!='': print 'ILLUM ',illum
  if len(bootstrap)>0: print 'BOOTSTRAP ',bootstrap
  if len(bpm)>0: print 'BPM ',bpm
  if trim: print 'TRIM'
  if overscan: print 'OVERSCAN'




#=================
# PROCESS FILES
#=================

# Loop over input files
error = strarr(nfiles)
#FOR f=0L,nfiles-1:
for f in range(0,nfiles):

  # File information and headers
  info = ccdproc_fileinfo(files[f])
  origfile = info.file
  outfile = info.dir+'/'+info.base+'_temp.fits'

  # File does not exist
  if info.exists==0:
    error[f] = origfile+' NOT FOUND'
    if not silent: print error[f]
    goto,BOMBFILE

  # Not a FITS file
  if info.ext!='fits':
    error[f] = origfile+' NOT A FITS FILE'
    if not silent: print error[f]
    goto,BOMBFILE


  if not silent: print 'Processing ',info.base+'.fits'


  # Initialize output file
  FILE_DELETE,outfile,/allow_nonexistent,/quiet
  if next>1: FITS_WRITE,outfile,0,*(info.hdu[0].head),/no_abort  # for multi-extension

  #---------------------------
  # LOOP OVER THE EXTENSIONS
  #---------------------------
  if next==0:
    loext = 0L
    no_pdu = 0
  else:
    loext = 1L
    no_pdu = 1

#  FOR i=loext,loext+next-1:
    for i in (loext,loext+next):

    # Load the file
    FITS_READ,file,im,head,exten=i,no_pdu=no_pdu,/no_abort,message=error1
    if error1!='': goto,BOMBFILE
    origim = im
    im = float(im)

    # Check the image and header
    # Check that IM is a data (type=1-5 or 12-15) 2D array
    if CHECKPAR(zeroim,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',silent=silent,errstr=error1): goto,BOMBFILE
    # Check that HEAD is a string array
    if CHECKPAR(zerohead,7,1,caller=errprefix+'Header - ',silent=silent,errstr=error1): goto,BOMBFILE


    #str = {im:im,head:head,fixPix:keyword_set(fixPix),overtrim:keyword_set(overtrim),$
    #       zero:'',flat:''}


    # Cross-talk
    #-----------
    if len(xTalk)>0:
       CCDPROC_XTALK,im,head,i,xstr,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Linearity Correction
    #---------------------
    if len(linCorr)>0:
      CCDPROC_LINCORR,im,head,i,linstr,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # FixPix
    #----------
    if len(fixPix)>0:
      CCDPROC_FIXPIX,im,head,fixstr,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Overscan
    #---------
    if overscan:
      CCDPROC_OVERSCAN,im,head,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Trim
    #-----
    if trim:
      CCDPROC_TRIM,im,head,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Zero Correct
    #-------------
    if zero!='':
      CCDPROC_ZERO,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Domeflat Correct
    #-----------------
    if flat!='':
      CCDPROC_FLAT,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Illumination Correction
    #-------------------------
    # maybe this should be called sflatcor
    if illum!='':
      CCDPROC_ILLUM,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Bootstrap
    #----------
    if len(bootstrap)>0:
      CCDPROC_BOOTSTRAP,im,head,bootstr,exten=i,error=error1,silent=silent
      if error1!='': goto,BOMBFILE

    # Bad Pixel Mask
    #----------------
    if len(bpm)>0:
      CCDPROC_BPM,im,head,bpm,exten=i,error=error1,silent=silent
      if error1!='': goto,BOMBFILE


    # SHOULD LINEARITY CORRECTION GO BEFORE XTALK-CORRECTION????
    # Dark correction??
    # Fringe correction?

    # Example of how the header is modified.
    #XTALKCOR= 'Oct  8 21:19 No crosstalk correction required'                       
    #OVSNMEAN=             1503.989                                                  
    #TRIM    = 'Oct  8 21:19 Trim is [25:1048,1:4096]'                               
    #FIXPIX  = 'Oct  8 21:19 Fix mscdb$noao/Mosaic2/CAL0102/bpm3_0102 + sat + bleed' 
    #OVERSCAN= 'Oct  8 21:19 Overscan is [1063:1112,1:4096], mean 1503.989'          
    #ZEROCOR = 'Oct  8 21:19 Zero is Zero[im5]'                                      
    #FLATCOR = 'Oct  8 21:19 Flat is DFlatM.fits[im5], scale 10490.72'               
    #CCDPROC = 'Oct 18 11:34 CCD processing done'                                    
    #PROCID  = 'ct4m.20070817T081040V3'                                              
    #SFLATCOR= 'Oct 18 11:34 Sky flat is Sflatn12M.fits[im5], scale 833.0756'        

    # Add final processing info to header
    date = systime(0)
    datearr = strtrim(strsplit(date,' ',/extract),2)
    timarr = strsplit(datearr[3],':',/extract)
    datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
    fxaddpar,head,'CCDPROC',datestr+' CCD processing done'

    # Do we need to change BITPIX, BSCALE, BZERO, etc??

    # Write output
    MWRFITS,im,outfile,head,/silent

    #stop

  #exit extension for loop

  # THE PROCESSING STEPS SHOULD GO IN THE PRIMARY HEADER!!!

  # Move temporary file to original file
  if not clobber:
    FILE_MOVE,outfile,file,/overwrite,/allow

  BOMBFILE:
  # An error occured
  if error1!='':
    error[f] = error1
    if not silent: print error[f]
    FILE_DELETE,outfile,/allow_nonexistent,/quiet  # delete temporary file

#exit file for loop


