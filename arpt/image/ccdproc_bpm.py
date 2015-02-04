"""
+

 CCDPROC_BPM

 This program sets bad pixels to a predefined bad value.

 INPUTS:
  im           The 2D image array.
  head         The image header string array.
  bpmfile      The name of the bad pixel mask file.
  =exten       The extension to use for the bpm image file.
  =badpixval   Value to set bad pixels to in input image.  Default is 65535.
  /silent      Don't print anything to the screen.

 OUTPUTS:
  The input image and header are modified.  The bad pixels (as
  defined by the BPM file) are set to a predefined "bad" value.
  Processing information is added to the header.
  =error       The error message if one occurred.

 USAGE:
  IDL>ccdproc_bpm,im,head,bpmfile,exten=5,error=error,silent=silent

 By D. Nidever   April 2014
-
"""

def ccdproc_bpm(im,head,bpmfile,exten=exten,badpixval=badpixval,error='',silent=True):

    # Initalizing some variables
    errprefix = 'CCDPROC_BPM: '   # error message prefix
    if len(badpixval)==0: badpixval = 65535L   # bad pixel value

    # Error Handling
    #------------------
    # Establish error handler. When errors occur, the index of the  
    # error is returned in the variable error_status:  
    CATCH( error_status )
    #This statement begins the error handler:  
    if error_status!=0:
        error = errprefix+!ERROR_STATE.MSG  
        if not silent: print error
        CATCH( CANCEL=True )
        return error

    # Check inputs
    #-------------
    if len(im)==0 or len(head)==0 or len(bpmfile)==0:
        if not silent: $
        print 'Syntax -  ccdproc_bpm,im,head,bpmfile,exten=exten,error=error,silent=silent'
        error = errprefix+'Not Enough Inputs'
        return error

    # Check that IM is a data (type=1-5 or 12-15) 2D array
    if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent): return error
    # Check that HEAD is a string array
    if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent): return error
    imsz = size(im) & imsz=imsz[1:imsz[0]]

    # Have we done this processing step already?
    bpmcor = sxpar(head,'BPM',count=nbpmcor)
    if nbpmcor>0:
        error = errprefix+'BPM correction already applied.'
        if not silent: print error
        return error

    # Check BPM file
    if CCDPROC_CHECKFILE(bpmfile,exten=exten,size=imsz,caller=errprefix,silent=silent,errstr=error): return error


    # Read in BPM image
    #--------------------
    FITS_READ(bpmfile,bpmim,bpmhead,exten=exten,no_abort=True,message=message)
    if message!='':
        error = errprefix+message
        if not silent: print error
        return error

    # Set bad pixels
    #-----------------
    bdpix = where(bpmim==1,nbdpix)           # BPM=1 means bad pixels
    if nbdpix>0: im[bdpix] = badpixval       # set to bad pixel value


    # Add processing information to header
    #--------------------------------------
    #  Current timestamp information
    #  Sun Oct  7 15:38:23 2012
    date = systime(0)
    datearr = strtrim(strsplit(date,' ',/extract),2)
    timarr = strsplit(datearr[3],':',/extract)
    datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
    fxaddpar,head,'BPM',datestr+' BPM is '+bpmfile+', '+strtrim(nbdpix,2)+' bad pixels'

    return error
