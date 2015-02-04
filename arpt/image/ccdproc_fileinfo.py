"""
+

 CCDPROC_FILEINFO

 This returns information on a file.

 INPUTS:
  file        A scalar string of the filename.
  /xtrafits   Return extra information (including headers) for FITS file

 OUTPUTS:
  info        A structure with information on the file.
  =error      The error message if one occured.

 USAGE:
  IDL>info = ccdproc_fileinfo(filename)

 By D. Nidever  April 2014
-
"""

def ccdproc_fileinfo(file, xtrafits=False, silent=False, error=''):

    # Initalizing some variables
    errprefix = 'CCDPROC_FILEINFO: '   # error message prefix
    info = {file:'',exists:0B,size:0LL,dir:'',base:'',ext:'',validfits:0,nextend:-1L}   # blank structure

    # Error Handling
    #------------------
    # Establish error handler. When errors occur, the index of the  
    # error is returned in the variable Error_status:  
#KENZA - check this function out
    CATCH( Error_status )
    #This statement begins the error handler:  
    if (Error_status!=0):
        error = errprefix+!ERROR_STATE.MSG  
        if not silent: print error
        CATCH( CANCEL=True )
        return info

    # No file input
    if len(file)==0: return info

    # Get basic file information
    idl_info = file_info(file[0])
    info.file = file[0]
    info.exists = idl_info.exists
    info.size = idl_info.size
    info.dir = file_dirname(file[0])
    base = file_basename(file[0])
    if strpos(base,'.')!=-1:
        lastdot = strpos(base,'.',/reverse_search)
        info.base = strmid(base,0,lastdot)
        info.ext = strmid(base,lastdot+1)  # extension without the dot
    else: info.base=base

    # File not found
    if info.exists==0: return info

    # The rest is only for FITS files
    if info.ext!='fits': return info

    # Get fits info
    fits_open(file[0],fcb,no_abort=True,message=message)
    if message!='': return info   # not valid fits file, return
    next = fcb.nextend
    fits_close(fcb)
    info.validfits = 1             # loaded with no error, valid fits file
    info.nextend = long(next)      # number of extensions

    # Getting some basic FITS header information
    info = CREATE_STRUCT(info,{filter:'',dateobs:'',exptime:0.0})
    head = headfits(file[0],exten=0,errmsg=errmsg,/silent)
    if errmsg!='': return info
    filter = sxpar(head,'FILTER',count=nfilter)
    if nfilter>0: info.filter=filter
    dateobs = sxpar(head,'DATE-OBS',count=ndateobs)
    if ndateobs>0: info.dateobs=dateobs
    exptime = sxpar(head,'EXPTIME',count=nexptime)
    if nexptime>0: info.exptime=exptime

    # Extra FITS information
    if info.validfits and xtrafits:
        # Expand structure
        nhdu = next + 1  # number of extensions + PDU
        info = CREATE_STRUCT(info,{hdu:replicate({ext:0L,naxis:0L,sz:lonarr(6),head:PTR_NEW(),xtalk:0B,lincor:0B,trim:0B,overscan:0B,zero:0B,flat:0B,illumcor:0B,btsrp:0B,bpm:0B},nhdu) } )

        # Loop through HDUs
        for i in range(0,nhdu):
            info.hdu[i].ext = i
            head = headfits(file[0],exten=i,errmsg=errmsg,silent=True)
            if errmsg!='':
                return info
            naxis = sxpar(head,'NAXIS')
            info.hdu[i].naxis = naxis
            sz = lonarr(6)
            sz[0] = naxis
            if naxis>0:
                for j in range(1,naxis+1):
                    sz[j]=sxpar(head,'NAXIS'+strtrim(j,2))
            info.hdu[i].sz = sz
            info.hdu[i].head = PTR_NEW(head)

            # Check processing steps
            xtalk = sxpar(head,'XTALKCOR',count=nxtalk)
            if nxtalk>0: info.hdu[i].xtalk=1
            lincorr = sxpar(head,'LINCORR',count=nlincorr)
            if nlincorr>0: info.hdu[i].lincor=1
            trim = sxpar(head,'TRIM',count=ntrim)
            if ntrim>0: info.hdu[i].trim=1
            overscan = sxpar(head,'OVERSCAN',count=noverscan)
            if noverscan>0: info.hdu[i].overscan=1
            zerocor = sxpar(head,'ZEROCOR',count=nzerocor)
            if nzerocor>0: info.hdu[i].zero=1
            flatcor = sxpar(head,'FLATCOR',count=nflatcor)
            if nflatcor>0: info.hdu[i].flat=1
            illumcor = sxpar(head,'ILLUMCOR',count=nillumcor)
            if nillumcor>0: info.hdu[i].illumcor=1
            btstrp = sxpar(head,'BTSRP',count=nbtstrp)
            if nbtstrp>0: info.hdu[i].btsrp=1
            bpm = sxpar(head,'BPM',count=nbpm)
            if nbpm>0: info.hdu[i].bpm=1

    return info
