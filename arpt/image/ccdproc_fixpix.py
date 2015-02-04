"""
+

 CCDPROC_FIXPIX

 This program applies a linearity correction to an image.

 INPUTS:
  im           The 2D image array.
  head         The image header string array.
  linstr       The linearity correction structure.
  /silent      Don't print anything to the screen.

 OUTPUTS:
  The input image and header are modified.  The input image is
  scaled using the linarity correction and processing information
  is added to the header.
  =error       The error message if one occurred.

 USAGE:
  IDL>ccdproc_fixpix,im,head,linstr,error=error,silent=silent

 By D. Nidever   April 2014
-
"""

def ccdproc_fixpix(im,head,linstr,error='',silent=True):

    # Initalizing some variables
    errprefix = 'CCDPROC_FIXPIX: '   # error message prefix

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
    if len(im)==0 or len(head)==0 or len(linstr)==0:
        if not silent: $
        print 'Syntax -  ccdproc_fixpix,im,head,linstr,error=error,silent=silent'
        error = errprefix+'Not Enough Inputs'
        return error

    # Check that IM is a data (type=1-5 or 12-15) 2D array
    if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent): return error
    # Check that HEAD is a string array
    if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent): return error

    # Have we done this processing step already?
    fixpix = sxpar(head,'FIXPIX',count=nfixpix)
    if nfixpix>0:
        error = errprefix+'Linearity correction already applied.'
        if not silent: print error
        return error

    # Check the fixpix structure
    if CHECKPAR(im,[8],caller=errprefix+'LINSTR - ',errstr=error,silent=silent): return error
    if tag_exist(linstr,'EXTEN')==0 or tag_exist(linstr,'SCALE')==0:
        error = errprefix+'Linearity structure must have EXTEN and SCALE tags.'
        if not silent: print error
        return error

    # Check that the FIXPIX EXTEN is int/long
    if CHECKPAR(bootstr.exten,[2,3],caller=errprefix+'Fixpix EXTEN - ',silent=silent,errstr=error): return error
    # Check that the FIXPIX SCALE is float/double
    if CHECKPAR(bootstr.scale,[4,5],caller=errprefix+'Fixpix SCALE - ',silent=silent,errstr=error): return error

    # Find the right extension
    if len(exten)>0:
        ind=where(bootstr.exten==exten,nind)
    else:
        ind = where(bootstr.exten==0,nind)
    if nind==0:
        error = errprefix+'Right extension NOT FOUND in Fixpix structure.'
        if not silent: print error
        return error

    # SCALE cannot be zero
    if bootstr[ind[0]].scale==0.0:
        error = errprefix+'Fixpix SCALE but not be zero.'
        if not silent: print error
        return error

    # Scale by FIXPIX value
    #--------------------------
    im *= bootstr[ind[0]].scale     # scale by Fixpix value


    # Add processing information to header
    #--------------------------------------
    #  Current timestamp information
    #  Sun Oct  7 15:38:23 2012
    date = systime(0)
    datearr = strtrim(strsplit(date,' ',/extract),2)
    timarr = strsplit(datearr[3],':',/extract)
    datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
    fxaddpar,head,'FIXPIX',datestr+' Fixpix scale '+strtrim(string(bootstr[ind[0]].scale,format='(G20.2)'),2)

    return error
