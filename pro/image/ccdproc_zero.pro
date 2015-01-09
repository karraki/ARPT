;+
;
; CCDPROC_ZERO
;
; This program subtracts a zero image from an input image. 
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  zerofile     The name of the zero image file.
;  =exten       The extension to use for the zero image file.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The zero image is
;  subtracted and processing information is added to the header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_zero,im,head,zerofile,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_zero,im,head,zerofile,exten=exten,error=error,silent=silent

; Initalizing some variables
error = ''                     ; initialize error variable
errprefix = 'CCDPROC_ZERO: '   ; error message prefix

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
if n_elements(im) eq 0 or n_elements(head) eq 0 or n_elements(zerofile) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_zero,im,head,zerofile,exten=exten,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return
imsz = size(im) & imsz=imsz[1:imsz[0]]

; Have we done this processing step already?
zerocor = sxpar(head,'ZEROCOR',count=nzerocor)
if nzerocor gt 0 then begin
  error = errprefix+'Zero correction already performed.'
  if not keyword_set(silent) then print,error
  return
endif

; Check Zero file
if CCDPROC_CHECKFILE(zerofile,exten=exten,size=imsz,caller=errprefix,silent=silent,errstr=error) then return


; Read in ZERO image
;--------------------
FITS_READ,zerofile,zeroim,zerohead,exten=exten,/no_abort,message=message
if message ne '' then begin
  error = errprefix+message
  if not keyword_set(silent) then print,error
  return
endif

; Subtract ZERO image
;---------------------
im -= round(zeroim)  ; im should be LONG, need to round ZERO if non-integer

; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
fxaddpar,head,'ZEROCOR',datestr+' Zero is '+zerofile

end
