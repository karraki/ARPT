;+
;
; CCDPROC_OVERSCAN
;
; This program an overscan correction.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The input image is
;  overscan correction and processing information is added to the
;  header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_overscan,im,head,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_overscan,im,head,error=error,silent=silent

; Initalizing some variables
error = ''                         ; initialize error variable
errprefix = 'CCDPROC_OVERSCAN: '   ; error message prefix

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
    print,'Syntax -  ccdproc_overscan,im,head,error=error,silent=silent'
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
overscan = sxpar(head,'OVERSCAN',count=noverscan)
if noverscan gt 0 then begin
  error = errprefix+'Overscan correction already applied.'
  if not keyword_set(silent) then print,error
  return
endif

; Get BIASSEC and TRIMSEC
biassec = CCDPROC_SPLITSEC(sxpar(head,'BIASSEC',count=nbiassec))-1
if (nbiassec eq 0 or biassec[0] eq -1) then begin
  error = errprefix+'Header must have BIASSEC'
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
if (biassec[1] lt biassec[0] or biassec[3] lt biassec[2]) or $
   (trimsec[1] lt trimsec[0] or trimsec[3] lt trimsec[2]) then begin
  error = errprefix+'BIAS/TRIM/DATA section indices are not in INCREASING order'
  if not keyword_set(silent) then print,error
  return
endif

; Make sure the indices are within the bounds of the image
if biassec[0] lt 0 or biassec[1] gt sz[1]-1 or biassec[2] lt 0 or biassec[3] gt sz[2]-1 or $
   trimsec[0] lt 0 or trimsec[1] gt sz[1]-1 or trimsec[2] lt 0 or trimsec[3] gt sz[2]-1 then begin
  error = errprefix+'BIAS/TRIM/DATA section indices out of image bounds'
  if not keyword_set(silent) then print,error
  return
endif

; Get the BIAS and DATA parts of the image
biasim = im[biassec[0]:biassec[1],biassec[2]:biassec[3]]
dataim = im[trimsec[0]:trimsec[1],trimsec[2]:trimsec[3]]


; Which BIAS dimension are we smoothing/integrating over.
; The smaller one
nxbias = biassec[1]-biassec[0]+1
nybias = biassec[3]-biassec[2]+1
; BIAS along columns. Integrate/collapse in X
;---------------------------------------------
if nxbias lt nybias then begin

  ; Make sure the BIAS covers the DATA
  if biassec[2] gt trimsec[2] or biassec[3] lt trimsec[3] then begin
    error = errprefix+'BIASSEC does not cover TRIMSEC in Y'
    if not keyword_set(silent) then print,error
    return
  endif

  ; We need Y portion to be same as DATA, so use TRIMSEC
  biasim = im[biassec[0]:biassec[1],trimsec[2]:trimsec[3]]

  ; Take median along short dimension
  bmed = median(biasim,dim=1)

  ; Subtract bias
  nxdata = trimsec[1]-trimsec[0]+1
  im[trimsec[0]:trimsec[1],trimsec[2]:trimsec[3]] -= replicate(1,nxdata)#bmed


; BIAS along rows. Integrated/collapse in Y
;---------------------------------------------
endif else begin

  ; Make sure the BIAS covers the DATA
  if biassec[0] gt trimsec[0] or biassec[1] lt trimsec[1] then begin
    error = errprefix+'BIASSEC does not cover TRIMSEC in X'
    if not keyword_set(silent) then print,error
    return
  endif

  ; We need X portion to be same as DATA, so use TRIMSEC
  biasim = im[trimsec[0]:trimsec[1],biassec[2]:biassec[3]]

  ; Take median along short dimension
  bmed = median(biasim,dim=2)

  ; Subtract bias
  nydata = trimsec[3]-trimsec[2]+1
  im[trimsec[0]:trimsec[1],trimsec[2]:trimsec[3]] -= bmed#replicate(1,nydata)

endelse

ovsnmean = mean(bmed)  ; mean of overscan

; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
;OVSNMEAN=             1503.989                                                  
;OVERSCAN= 'Oct  8 21:19 Overscan is [1063:1112,1:4096], mean 1503.989'      
sxaddpar,head,'OVSNMEAN',ovsnmean
fxaddpar,head,'OVERSCAN',datestr+' Overscan is '+biassec+', mean '+strtrim(string(ovsnmean,format='(G20.2)'),2)

end
