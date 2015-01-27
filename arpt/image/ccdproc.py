"""
 ccdproc

 This is a generic CCD image processing program.

 INPUTS:
  input       The input list of images.
  =xTalk
  =linCorr    Apply linearity correction
  =fixPix
  /trim
  /overscan
  /gainCorr
  =zero
  =flat
  =illum      Apply
  =bootstrap  Apply bootstrap correction.
  =bpm        Apply bad pixel mask using
  /clobber
  /verbose
  /silent     Don't print anything to the screen.

 OUTPUTS:
  =error      Error if one occured.


 By D.Nidever  Jan 2014,  based in part on IRAF's ccdproc program
"""
#KENZA - Q: what is editgain?
#Kenza - Q: is gainCorr a dead variable?

def ccdproc(input, **kwargs):
#input,fixPix=fixPix,trim=trim,overscan=overscan,gainCorr=gainCorr,
#zero=zero,flat=flat,xTalk=xTalk,illum=illum,bootstrap=bootstrap,
#bpm=bpm,clobber=clobber,verbose=verbose,linCorr=linCorr,silent=silent,
#error=error

#====================
# CHECK THE INPUTS
#====================
# Load the input files
    loadinput(input, files, count=nFiles)
#KENZA - Check loadinput later
    files.strip()
    if nFiles==0:
        error = 'No files to process'
        if not kwargs['silent']: print error
        return

    # No processing steps requested
    if not kwargs['fixPix'] and len(xTalk)==0 and not kwargs['trim'] \
          and not kwargs['overscan'] and len(zero)==0 and len(flat)==0 \
          and len(illum)==0:
#KENZA - Q: 'and and'?
        error = 'NO PROCESSING STEPS'
        if not kwargs['silent']: print error
        return

#KENZA - worked up to here

# Get file information
#   this also works if there is no input or the file doesn't exist
xTalk_info = CCDPROC_FILEINFO(xTalk)
linCorr_info = CCDPROC_FILEINFO(linCorr)
fixPix_info = CCDPROC_FILEINFO(fixPix)
zero_info = CCDPROC_FILEINFO(zero)
flat_info = CCDPROC_FILEINFO(flat)
illum_info = CCDPROC_FILEINFO(illum)
bootstrap_info = CCDPROC_FILEINFO(bootstrap)
bpm_info = CCDPROC_FILEINFO(bpm)

# Check that files exist if input
if len(xTalk)>0 and xTalk_info.exists==0 then error='XTALK file '+xTalk_info.file+' NOT FOUND'
if len(linCorr)>0 and linCorr_info.exists==0 then error='LINCORR file '+linCorr_info.file+' NOT FOUND'
if len(fixPix)>0 and fixPix_info.exists==0 then error='FIXPIX file '+fixPix_info.file+' NOT FOUND'
if len(zero)>0 and zero_info.exists==0 then error='ZERO file '+zero_info.file+' NOT FOUND'
if len(flat)>0 and flat_info.exists==0 then error='FLAT file '+flat_info.file+' NOT FOUND'
if len(illum)>0 and illum_info.exists==0 then error='ILLUM file '+illum_info.file+' NOT FOUND'
if len(bootstrap)>0 and bootstrap_info.exists==0 then error='Bootstrap file '+bootstrap_info.file+' NOT FOUND'
if len(bpm)>0 and bpm_info.exists==0 then error='BPM file '+bpm_info.file+' NOT FOUND'
if len(error)>0:
  if not kwargs['silent']: print error
  return
endif

# That that NEXTEND for the cal files is big enough for the input files

# Some defaults
if len(zero)==0 then zero=''
if len(flat)==0 then flat=''
if len(illum)==0 then illum=''


#=========================================
# LOAD CALIBRATION DATA USED BY ALL FILES
#=========================================

# Load bootstrap file
if len(bootstrap)>0:
  CCDPROC_LOADBOOTSTRAP,bootstrap,bootstr,error=error,silent=silent
  if error!='' then return
endif
# Load xTalk values
if len(xTalk)>0:
  CCDPROC_LOADXTALK,xTalk,xstr,error=error,silent=silent
  if error!='' then return
endif
# Load fixPix file
if len(fixPix)>0:
  CCDPROC_LOADFIXPIX,fixPix,fixstr,error=error,silent=silent
  if error!='' then return
endif

# Print out processing steps
if not keyword_set(silent) begin
  then print 'Processing steps:'
  if len(xTalk)>0 then print 'XTALK ',xTalk
  if len(linCorr)>0 then print 'LINCORR ',linCorr
  if len(fixPix)>0 then print 'FIXPIX ',fixPix
  if keyword_set(trim) then print 'TRIM'
  if keyword_set(overscan) then print 'OVERSCAN'
  if zero!='' then print 'ZERO ',zero
  if flat!='' then print 'FLAT ',flat
  if illum!='' then print 'ILLUM ',illum
  if len(bootstrap)>0 then print 'BOOTSTRAP ',bootstrap
  if len(bpm)>0 then print 'BPM ',bpm
endif


#=================
# PROCESS FILES
#=================

# Loop over input files
error = strarr(nfiles)
FOR f=0L,nfiles-1 do begin

  # File information and headers
  info = CCDPROC_FILEINFO(files[f])
  origfile = info.file
  outfile = info.dir+'/'+info.base+'_temp.fits'

  # File does not exist
  if info.exists==0:
    error[f] = origfile+' NOT FOUND'
    if not kwargs['silent']: print error[f]
    goto,BOMBFILE
  endif
  # Not a FITS file
  if info.ext!='fits':
    error[f] = origfile+' NOT A FITS FILE'
    if not kwargs['silent']: print error[f]
    goto,BOMBFILE
  endif

  if not keyword_set(silent) then print 'Processing ',info.base+'.fits'


  # Initialize output file
  FILE_DELETE,outfile,/allow_nonexistent,/quiet
  if next>1 then FITS_WRITE,outfile,0,*(info.hdu[0].head),/no_abort  # for multi-extension

  #---------------------------
  # LOOP OVER THE EXTENSIONS
  #---------------------------
  if next==0:
    loext = 0L
    no_pdu = 0
  endif else begin
    loext = 1L
    no_pdu = 1
  endelse
  FOR i=loext,loext+next-1 do begin

    # Load the file
    FITS_READ,file,im,head,exten=i,no_pdu=no_pdu,/no_abort,message=error1
    if error1!='' then goto,BOMBFILE
    origim = im
    im = float(im)

    # Check the image and header
    # Check that IM is a data (type=1-5 or 12-15) 2D array
    if CHECKPAR(zeroim,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',silent=silent,errstr=error1) then goto,BOMBFILE
    # Check that HEAD is a string array
    if CHECKPAR(zerohead,7,1,caller=errprefix+'Header - ',silent=silent,errstr=error1) then goto,BOMBFILE


    #str = {im:im,head:head,fixPix:keyword_set(fixPix),overtrim:keyword_set(overtrim),$
    #       zero:'',flat:''}


    # Cross-talk
    #-----------
    if len(xTalk)>0:
       CCDPROC_XTALK,im,head,i,xstr,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Linearity Correction
    #---------------------
    if len(linCorr)>0:
      CCDPROC_LINCORR,im,head,i,linstr,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # FixPix
    #----------
    if len(fixPix)>0:
      CCDPROC_FIXPIX,im,head,fixstr,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Overscan
    #---------
    if keyword_set(overscan):
      CCDPROC_OVERSCAN,im,head,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Trim
    #-----
    if keyword_set(trim):
      CCDPROC_TRIM,im,head,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Zero Correct
    #-------------
    if zero!='':
      CCDPROC_ZERO,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Domeflat Correct
    #-----------------
    if flat!='':
      CCDPROC_FLAT,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Illumination Correction
    #-------------------------
    # maybe this should be called sflatcor
    if illum!='':
      CCDPROC_ILLUM,im,head,zero,exten=i,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Bootstrap
    #----------
    if len(bootstrap)>0:
      CCDPROC_BOOTSTRAP,im,head,bootstr,exten=i,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif
    # Bad Pixel Mask
    #----------------
    if len(bpm)>0:
      CCDPROC_BPM,im,head,bpm,exten=i,error=error1,silent=silent
      if error1!='' then goto,BOMBFILE
    endif

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

  ENDFOR  # extension loop

  # THE PROCESSING STEPS SHOULD GO IN THE PRIMARY HEADER!!!

  # Move temporary file to original file
  if not keyword_set(clobber) then $
    FILE_MOVE,outfile,file,/overwrite,/allow

  BOMBFILE:
  # An error occured
  if error1!='':
    error[f] = error1
    if not keyword_set(silent): print error[f]
    FILE_DELETE,outfile,/allow_nonexistent,/quiet  # delete temporary file

ENDFOR  # file loop

#stop

end
