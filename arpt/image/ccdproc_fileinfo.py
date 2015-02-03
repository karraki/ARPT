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

def ccdproc_fileinfo(file, xtrafits=False, error=''):

# Initalizing some variables
error = ''                         # initialize error variable
errprefix = 'CCDPROC_FILEINFO: '   # error message prefix
info = {file:'',exists:0B,size:0LL,dir:'',base:'',ext:'',validfits:0,nextend:-1L}   # blank structure

# Error Handling
#------------------
# Establish error handler. When errors occur, the index of the  
# error is returned in the variable Error_status:  
CATCH, Error_status 
#This statement begins the error handler:  
if (Error_status ne 0) then begin 
   error = errprefix+!ERROR_STATE.MSG  
   if not keyword_set(silent) then print,error
   CATCH, /CANCEL 
   return,info
endif

# No file input
if n_elements(file) eq 0 then return,info

# Get basic file information
idl_info = file_info(file[0])
info.file = file[0]
info.exists = idl_info.exists
info.size = idl_info.size
info.dir = file_dirname(file[0])
base = file_basename(file[0])
if strpos(base,'.') ne -1 then begin
  lastdot = strpos(base,'.',/reverse_search)
  info.base = strmid(base,0,lastdot)
  info.ext = strmid(base,lastdot+1)  # extension without the dot
endif else info.base=base

# File not found
if info.exists eq 0 then return,info

# The rest is only for FITS files
if info.ext ne 'fits' then return,info

# Get fits info
fits_open,file[0],fcb,/no_abort,message=message
if message ne '' then return,info   # not valid fits file, return
next = fcb.nextend
fits_close,fcb
info.validfits = 1                  # loaded with no error, valid fits file
info.nextend = long(next)           # number of extensions

# Getting some basic FITS header information
info = CREATE_STRUCT(info,{filter:'',dateobs:'',exptime:0.0})
head = headfits(file[0],exten=0,errmsg=errmsg,/silent)
if errmsg ne '' then return,info
filter = sxpar(head,'FILTER',count=nfilter)
if nfilter gt 0 then info.filter=filter
dateobs = sxpar(head,'DATE-OBS',count=ndateobs)
if ndateobs gt 0 then info.dateobs=dateobs
exptime = sxpar(head,'EXPTIME',count=nexptime)
if nexptime gt 0 then info.exptime=exptime


# Extra FITS information
if info.validfits and keyword_set(xtrafits) then begin

  # Expand structure
  nhdu = next+1  # number of extensions + PDU
  info = CREATE_STRUCT(info,{hdu:replicate({ext:0L,naxis:0L,sz:lonarr(6),head:PTR_NEW(),$
                         xtalk:0B,lincor:0B,trim:0B,overscan:0B,zero:0B,flat:0B,illumcor:0B,btsrp:0B,bpm:0B},nhdu) } )

  # Loop through HDUs
  FOR i=0L,nhdu-1 do begin
    info.hdu[i].ext = i
    head = headfits(file[0],exten=i,errmsg=errmsg,/silent)
    if errmsg ne '' then goto,BOMB
    naxis = sxpar(head,'NAXIS')
    info.hdu[i].naxis = naxis
    sz = lonarr(6)
    sz[0] = naxis
    if naxis gt 0 then for j=1,naxis do sz[j]=sxpar(head,'NAXIS'+strtrim(j,2))
    info.hdu[i].sz = sz
    info.hdu[i].head = PTR_NEW(head)

    # Check processing steps
    xtalk = sxpar(head,'XTALKCOR',count=nxtalk)
    if nxtalk gt 0 then info.hdu[i].xtalk=1
    lincorr = sxpar(head,'LINCORR',count=nlincorr)
    if nlincorr gt 0 then info.hdu[i].lincor=1
    trim = sxpar(head,'TRIM',count=ntrim)
    if ntrim gt 0 then info.hdu[i].trim=1
    overscan = sxpar(head,'OVERSCAN',count=noverscan)
    if noverscan gt 0 then info.hdu[i].overscan=1
    zerocor = sxpar(head,'ZEROCOR',count=nzerocor)
    if nzerocor gt 0 then info.hdu[i].zero=1
    flatcor = sxpar(head,'FLATCOR',count=nflatcor)
    if nflatcor gt 0 then info.hdu[i].flat=1
    illumcor = sxpar(head,'ILLUMCOR',count=nillumcor)
    if nillumcor gt 0 then info.hdu[i].illumcor=1
    btstrp = sxpar(head,'BTSRP',count=nbtstrp)
    if nbtstrp gt 0 then info.hdu[i].btsrp=1
    bpm = sxpar(head,'BPM',count=nbpm)
    if nbpm gt 0 then info.hdu[i].bpm=1

    BOMB:

  ENDFOR

endif

return,info

end
