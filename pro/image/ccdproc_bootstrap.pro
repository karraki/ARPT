;+
;
; CCDPROC_BOOTSTRAP
;
; This program applies a bootstrap correction to an image.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  bootstr      The bootstrap structure.
;  =exten       The extension to use in the bootstrap file
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The input image is
;  scaled by the bootstrap correction and processing information
;  is added to the header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_bootstrap,im,head,bootstr,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_bootstrap,im,head,bootstr,exten=exten,error=error,silent=silent

; Initalizing some variables
error = ''                     ; initialize error variable
errprefix = 'CCDPROC_BOOTSTRAP: '   ; error message prefix

; Error Handling
;------------------
; Establish error handler. When errors occur, the index of the  
; error is returned in the variable Error_status:  
CATCH, Error_status 
;This statement begins the error handler:  
if (Error_status ne 0) then begin 
   error = errprefix+!ERROR_STATE.MSG  
   if not keyword_set(silent) then print,error
   CATCH, /CANCEL 
   return
endif

; Check inputs
;-------------
if n_elements(im) eq 0 or n_elements(head) eq 0 or n_elements(bootstr) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_bootstrap,im,head,bootstr,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return

; Have we done this processing step already?
btstrp = sxpar(head,'BTSTRP',count=nbtstrp)
if nbtstrp gt 0 then begin
  error = errprefix+'Bootstrap correction already applied.'
  if not keyword_set(silent) then print,error
  return
endif

; Check the bootstrap structure
if CHECKPAR(bootstr,8,caller=errprefix+'BOOTSTR - ',errstr=error,silent=silent) then return
if tag_exist(bootstr,'EXTEN') eq 0 or tag_exist(bootstr,'SCALE') eq 0 then begin
  error = errprefix+'Bootstrap structure must have EXTEN and SCALE tags.'
  if not keyword_set(silent) then print,error
  return
endif
; Check that the BOOTSTRAP EXTEN is int/long
if CHECKPAR(bootstr.exten,[2,3],caller=errprefix+'Bootstrap EXTEN - ',silent=silent,errstr=error) then return
; Check that the BOOTSTRAP SCALE is float/double
if CHECKPAR(bootstr.scale,[4,5],caller=errprefix+'Bootstrap SCALE - ',silent=silent,errstr=error) then return

; Find the right extension
if n_elements(exten) gt 0 then ind=where(bootstr.exten eq exten,nind) else $
   ind = where(bootstr.exten eq 0,nind)
if nind eq 0 then begin
  error = errprefix+'Right extension NOT FOUND in Bootstrap structure.'
  if not keyword_set(silent) then print,error
  return
endif

; SCALE cannot be zero
if bootstr[ind[0]].scale eq 0.0 then begin
  error = errprefix+'Bootstrap SCALE but not be zero.'
  if not keyword_set(silent) then print,error
  return
endif

; Scale by BOOTSTRAP value
;--------------------------
im *= bootstr[ind[0]].scale     ; scale by Bootstrap value


; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
fxaddpar,head,'BTSTRP',datestr+' Bootstrap scale '+strtrim(string(bootstr[ind[0]].scale,format='(G20.2)'),2)

end
