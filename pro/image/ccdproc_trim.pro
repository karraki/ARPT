;+
;
; CCDPROC_TRIM
;
; This program trims the image to the TRIM or DATA section.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The input image is
;  trimmed and processing information is added to the
;  header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_trim,im,head,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_trim,im,head,error=error,silent=silent

; Initalizing some variables
error = ''                         ; initialize error variable
errprefix = 'CCDPROC_TRIM: '   ; error message prefix

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
if n_elements(im) eq 0 or n_elements(head) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_trim,im,head,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return
; Image size
sz = size(im)

; Have we done this processing step already?
trim = sxpar(head,'TRIM',count=ntrim)
if ntrim gt 0 then begin
  error = errprefix+'Trimming already performed.'
  if not keyword_set(silent) then print,error
  return
endif

; Get TRIMSEC (or DATASEC)
trimsec = CCDPROC_SPLITSEC(sxpar(head,'TRIMSEC',count=ntrimsec))-1
datasec = CCDPROC_SPLITSEC(sxpar(head,'DATASEC',count=ndatasec))-1
if (ntrimsec eq 0 or trimsec[0] eq -1) and (ndatasec eq 0 or datasec[0] eq -1) then begin
  error = errprefix+'Header must have TRIMSEC or DATASEC'
  if not keyword_set(silent) then print,error
  return
endif
if (ntrimsec eq 0 or trimsec[0] eq -1) then trimsec=datasec  ; use DATASEC instead of TRIMSEC

; Check that the indices are in the proper order
if (trimsec[1] lt trimsec[0] or trimsec[3] lt trimsec[2]) then begin
  error = errprefix+'TRIM/DATA section indices are not in INCREASING order'
  if not keyword_set(silent) then print,error
  return
endif

; Make sure the indices are within the bounds of the image
if trimsec[0] lt 0 or trimsec[1] gt sz[1]-1 or trimsec[2] lt 0 or trimsec[3] gt sz[2]-1 then begin
  error = errprefix+'TRIM/DATA section indices out of image bounds'
  if not keyword_set(silent) then print,error
  return
endif

; Trim the image
;----------------
im = im[trimsec[0]:trimsec[1],trimsec[2]:trimsec[3]]

; Update NAXIS1 and NAXIS2 in the header
sz = size(im)
sxaddpar,head,'NAXIS1',sz[1]
sxaddpar,head,'NAXIS2',sz[2]

; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
fxaddpar,head,'TRIM',datestr+' Trim is '+trimsec

end
