;+
;
; CCDPROC_LINCORR
;
; This program applies a linearity correction to an image.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  exten        The image extension number.
;  linstr       The linearity correction structure with EXTEN and COEF.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The input image is
;  scaled using the linarity correction and processing information
;  is added to the header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_lincorr,im,head,exten,linstr,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_lincorr,im,head,exten,linstr,error=error,silent=silent

; Initalizing some variables
error = ''                        ; initialize error variable
errprefix = 'CCDPROC_LINCORR: '   ; error message prefix

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
if n_elements(im) eq 0 or n_elements(head) eq 0 or n_elements(exten) eq 0 or n_elements(linstr) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_lincorr,im,head,exten,linstr,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return
; Check that EXTEN is a scalar integer
if CHECKPAR(exten,[1,2,3],0,caller=errprefix+'Exten - ',errstr=error,silent=silent) then return

; Have we done this processing step already?
lincorr = sxpar(head,'LINCORR',count=nlincorr)
if nlincorr gt 0 then begin
  error = errprefix+'Linearity correction already applied.'
  if not keyword_set(silent) then print,error
  return
endif

; Check the lincorr structure
if CHECKPAR(linstr,8,caller=errprefix+'LINSTR - ',errstr=error,silent=silent) then return
if tag_exist(linstr,'EXTEN') eq 0 or tag_exist(linstr,'COEF') eq 0 then begin
  error = errprefix+'Linearity structure must have EXTEN and COEF tags.'
  if not keyword_set(silent) then print,error
  return
endif
; Check that the LINCORR EXTEN is int/long
if CHECKPAR(linstr.exten,[2,3],caller=errprefix+'Linstr EXTEN - ',silent=silent,errstr=error) then return
; Check that the LINCORR COEF is float/double
if CHECKPAR(linstr.coef,[4,5],caller=errprefix+'Linstr COEF - ',silent=silent,errstr=error) then return

; Find the entries in the linstr structure
ind = where(linstr.exten eq exten,nind)
if nind eq 0 then begin
  ; This is not an error
  if not keyword_set(silent) then print,'No LINSTR entry for exten='+strtrim(exten,2)
  return
endif


; Apply linearity correction
;----------------------------
im = poly(im,linstr[ind[0]].coef)    ; scale the image


; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
fxaddpar,head,'LINCORR',datestr+' Lincorr scale '+strtrim(string(bootstr[ind[0]].scale,format='(G20.2)'),2)

end
