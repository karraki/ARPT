;+
;
; CCDPROC_BPM
;
; This program sets bad pixels to a predefined bad value.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  bpmfile      The name of the bad pixel mask file.
;  =exten       The extension to use for the bpm image file.
;  =badpixval   Value to set bad pixels to in input image.  Default is 65535.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The bad pixels (as
;  defined by the BPM file) are set to a predefined "bad" value.
;  Processing information is added to the header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_bpm,im,head,bpmfile,exten=5,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_bpm,im,head,bpmfile,exten=exten,badpixval=badpixval,error=error,silent=silent

; Initalizing some variables
error = ''                    ; initialize error variable
errprefix = 'CCDPROC_BPM: '   ; error message prefix
if n_elements(badpixval) eq 0 then badpixval = 65535L            ; bad pixel value

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
if n_elements(im) eq 0 or n_elements(head) eq 0 or n_elements(bpmfile) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_bpm,im,head,bpmfile,exten=exten,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return
imsz = size(im) & imsz=imsz[1:imsz[0]]

; Have we done this processing step already?
bpmcor = sxpar(head,'BPM',count=nbpmcor)
if nbpmcor gt 0 then begin
  error = errprefix+'BPM correction already applied.'
  if not keyword_set(silent) then print,error
  return
endif

; Check BPM file
if CCDPROC_CHECKFILE(bpmfile,exten=exten,size=imsz,caller=errprefix,silent=silent,errstr=error) then return


; Read in BPM image
;--------------------
FITS_READ,bpmfile,bpmim,bpmhead,exten=exten,/no_abort,message=message
if message ne '' then begin
  error = errprefix+message
  if not keyword_set(silent) then print,error
  return
endif

; Set bad pixels
;-----------------
bdpix = where(bpmim eq 1,nbdpix)                    ; BPM=1 means bad pixels
if nbdpix gt 0 then im[bdpix] = badpixval           ; set to bad pixel value


; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
fxaddpar,head,'BPM',datestr+' BPM is '+bpmfile+', '+strtrim(nbdpix,2)+' bad pixels'

end
