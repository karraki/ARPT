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

def bombfile(error1):
    # An error occured
    if error1!='':
        error[f] = error1
        if not silent: print error[f]
        # delete temporary file
        FILE_DELETE(outfile, allow_nonexistent=True, quiet=True)


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
if len(xTalk)>0 and xTalk_info.exists:
    error = 'XTALK file '+xTalk_info.file+' NOT FOUND'
if len(linCorr)>0 and linCorr_info.exists:
    error = 'LINCORR file '+linCorr_info.file+' NOT FOUND'
if len(fixPix)>0 and fixPix_info.exists:
    error = 'FIXPIX file '+fixPix_info.file+' NOT FOUND'
if len(zero)>0 and zero_info.exists:
    error = 'ZERO file '+zero_info.file+' NOT FOUND'
if len(flat)>0 and flat_info.exists:
    error = 'FLAT file '+flat_info.file+' NOT FOUND'
if len(illum)>0 and illum_info.exists:
    error = 'ILLUM file '+illum_info.file+' NOT FOUND'
if len(bootstrap)>0 and bootstrap_info.exists:
    error = 'Bootstrap file '+bootstrap_info.file+' NOT FOUND'
if len(bpm)>0 and bpm_info.exists:
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
    ccdproc_loadbootstrap(bootstrap, bootstr, error=error, silent=silent)
    if error!='': return error1

# Load xTalk values
if len(xTalk)>0:
    ccdproc_loadxtalk(xTalk, xstr, error=error, silent=silent)
    if error!='': return error1

# Load fixPix file
if len(fixPix)>0:
    ccdproc_loadfixpix(fixPix, fixstr, error=error, silent=silent)
    if error!='': return error1


# Print out processing steps
if not silent:
    print 'Processing steps:'
    if len(xTalk)>0: print 'XTALK ',xTalk
    if len(linCorr)>0: print 'LINCORR ',linCorr
    if len(fixPix)>0: print 'FIXPIX ',fixPix
    if len(zero)>0: print 'ZERO ',zero
    if len(flat)>0: print 'FLAT ',flat
    if len(illum)>0: print 'ILLUM ',illum
    if len(bootstrap)>0: print 'BOOTSTRAP ',bootstrap
    if len(bpm)>0: print 'BPM ',bpm
    if trim: print 'TRIM'
    if overscan: print 'OVERSCAN'

#=================
# PROCESS FILES
#=================

# Loop over input files
error = strarr(nfiles)

for f in range(0,nfiles):

    # File information and headers
    info = ccdproc_fileinfo(files[f])
    origfile = info.file
    outfile = info.dir+'/'+info.base+'_temp.fits'

    # File does not exist
    if info.exists==0:
        error[f] = origfile+' NOT FOUND'
        if not silent: print error[f]
        bombfile(error[f])

    # Not a FITS file
    if info.ext!='fits':
        error[f] = origfile+' NOT A FITS FILE'
        if not silent: print error[f]
        bombfile(error[f])


    if not silent: print 'Processing ',info.base+'.fits'


    # Initialize output file
    FILE_DELETE(outfile, allow_nonexistent=True, quiet=True)
    # for multi-extension
    if next>1:
        FITS_WRITE(outfile, 0, *(info.hdu[0].head), no_abort=True)

    #---------------------------
    # LOOP OVER THE EXTENSIONS
    #---------------------------
    if next==0:
        loext = 0L
        no_pdu = 0
    else:
        loext = 1L
        no_pdu = 1

    for i in (loext,loext+next):
        # Load the file
        FITS_READ(file, im, head, exten=i, no_pdu=no_pdu, no_abort=True, \
                      message=error1)
        if error1!='': bombfile(error1)
        origim = im
        im = float(im)

        # Check the image and header
        # Check that IM is a data (type=1-5 or 12-15) 2D array
        if CHECKPAR(zeroim, [1,2,3,4,5,12,13,14,15], [2], \
                        caller=errprefix+'Image - ', silent=silent, \
                        errstr=error1): bombfile(error1)
        # Check that HEAD is a string array
        if CHECKPAR(zerohead, 7, 1, caller=errprefix+'Header - ', \
                        silent=silent, errstr=error1): bombfile(error1)

        #str = {im:im, head:head, fixPix:keyword_set(fixPix), overtrim:keyword_set(overtrim), zero:'', flat:''}

        # Cross-talk
        #-----------
        if len(xTalk)>0:
            ccdproc_xtalk(im, head, i, xstr, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Linearity Correction
        #---------------------
        if len(linCorr)>0:
            ccdproc_lincorr(im, head, i, linstr, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # FixPix
        #----------
        if len(fixPix)>0:
            ccdproc_fixpix(im, head, fixstr, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Overscan
        #---------
        if overscan:
            ccdproc_overscan(im, head, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Trim
        #-----
        if trim:
            ccdproc_trim(im, head, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Zero Correct
        #-------------
        if zero!='':
            ccdproc_zero(im, head, zero, exten=i, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Domeflat Correct
        #-----------------
        if flat!='':
            ccdproc_flat(im, head, zero, exten=i, error=error1, silent=silent)
            if error1!='': bombfile(error1)

        # Illumination Correction
        #-------------------------
        # maybe this should be called sflatcor
        if illum!='':
            ccdproc_illum(im, head, zero, exten=i, error=error1, \
                              silent=silent)
            if error1!='': bombfile(error1)

        # Bootstrap
        #----------
        if len(bootstrap)>0:
            ccdproc_bootstrap(im, head, bootstr, exten=i, error=error1, \
                                  silent=silent)
            if error1!='': bombfile(error1)

        # Bad Pixel Mask
        #----------------
        if len(bpm)>0:
            ccdproc_bpm(im, head, bpm, exten=i, error=error1, silent=silent)
            if error1!='': bombfile(error1)


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
        MWRFITS(im, outfile, head, silent=True)

    #exit extension for loop
    # THE PROCESSING STEPS SHOULD GO IN THE PRIMARY HEADER!!!

    # Move temporary file to original file
    if not clobber:
        FILE_MOVE(outfile, file, overwrite=True, allow=True)

#exit file for loop


