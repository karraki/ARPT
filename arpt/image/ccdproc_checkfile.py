"""
+

 CCDPROC_CHECKFILE

 This function checks various properties of a file.

 INPUTS:
  file        A scalar string of the filename.
  =exten      The FITS file extension to check.
  /exists     The file must exist (this is also checked if /validfits,
                /data, or =size are set).
  /validfits  The file is a valid FITS file (this is also set if
                /data or =size are set).
  /data       The file contains image data and is not binary fits
                file (this is also checked if =size is set).
  =size       An array of number of elements for each dimension,
                e.g. size=[2048,2048].
  =caller     The calling program.  This string as added at the
                beginnning of ERRSTR.
  /silent     Don't print anything to the screen.

 OUTPUTS:
  The return value is 1/TRUE if the file FAILS any of the checks, and
  0/FALSE if it passes all of the tests.
  =errstr     The error string if the file failed one of the criteria
  =info       Structure with information on the file.

 USAGE:
  IDL>info = ccdproc_checkfile(filename,/validfits,info=info)

 By D. Nidever  April 2014
-
"""

def bomb(errval,caller,errstr,silent):
    # There was a failure
    if errval==1:
        if len(caller)>0: errstr=caller+errstr
        if not silent: print errstr
    return


def ccdproc_checkfile(file,exten=exten,exists=exists,validfits=validfits,data=data,size=size,caller=caller,errstr='',error='',info=None,silent=True):

    # Initalizing some variables
    errval = 0
    errprefix = 'CCDPROC_CHECKFILE: '   # error message prefix

    # Error Handling
    #------------------
    # Establish error handler. When errors occur, the index of the  
    # error is returned in the variable error_status:  
    CATCH( error_status )
    #This statement begins the error handler:  
    if error_status==0:
        error = errprefix+!ERROR_STATE.MSG  
        if not silent: print error
        CATCH( CANCEL=True )
        return errsrt='1'

    # No file input
    if len(file)==0:
        if not silent:
            print 'Syntax - val = ccdproc_checkfile(file,exists=exists,validfits=validfits,data=data,size=size,errstr=errstr, caller=caller,info=info,silent=silent)'
        errstr = errprefix+'Not enough inputs.'
        if not silent: print errstr
        return errsrt='1'

    # Get file info
    info = CCDPROC_FILEINFO(file[0])

    # Exists
    #--------
    if exists or validfits or data or len(size)>0 and info.exists==0:
        errstr = info.file+' NOT FOUND.'
        errval = 1
        bomb(errval,caller,errstr,silent)
        return errval

    # Valid FITS
    #------------
    if validfits or data or len(size)>0 and info.validfits==0:
        errstr = info.file+' is NOT a valid FITS file.'
        errval = 1
        bomb(errval,caller,errstr,silent)
        return errval

    # Load the header
    if validfits or data or len(size)>0:
        head = headfits(info.file,errmsg=errmsg,exten=exten)
        if errmsg!='':
            errstr = info.file+' cannot load FITS Header.'
            errval = 1
            bomb(errval,caller,errstr,silent)
            return errval

    # DATA
    #------
    if data or len(size)>0 and info.validfits==1:
        # All valid FITS non-binary files are DATA type
        # if NAXIS=0 or XTENSION='BINTABLE' then errval=1
        # Check that it's not a fits binary table

        naxis = sxpar(head,'NAXIS',count=n_naxis)
        xtension = sxpar(head,'XTENSION',count=n_xtension)
        if naxis==0 or (n_xtension>0 and xtension.split()=='BINTABLE'):
            errstr = info.file+' is not DATA.'
            errval = 1
            bomb(errval,caller,errstr,silent)
            return errval

    # SIZE
    #------
    if len(size)>0 and info.validfits==1:
        naxis = sxpar(head,'NAXIS',count=n_naxis)
        if naxis>0:
            imsize = lonarr(naxis)
            for i in range(0,naxis):
                naxis1 = sxpar(head,'NAXIS'+str(i+1).split(),count=n_naxis1)
                if n_naxis1>0: imsize[i]=long(naxis1)
        nimdim = len(imsize)
        ndim = len(size)

        # Number of dimensions different
        if nimdim!=ndim:
            errstr = info.file+' has wrong number of dimensions.  Must be '+strtrim(ndim,2)+'.'
            errval = 1
            bomb(errval,caller,errstr,silent)
            return errval

        # Sizes different
        if total(abs(imsize-size))!=0:
            errstr = info.file+' has wrong size, must be ['+strjoin(size.split(),',')+'].'
            errval = 1
            bomb(errval,caller,errstr,silent)
            return errval

    return errval

