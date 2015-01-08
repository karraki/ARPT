;+
;
; CCDPROC_XTALK
;
; This program applies a linearity correction to an image.
;
; INPUTS:
;  im           The 2D image array.
;  head         The image header string array.
;  exten        The image extension number.
;  xstr         The xtalk structure.
;  file         The image filename.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  The input image and header are modified.  The input image is
;  corrected for cross-talk and processing information is added
;  to the header.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_xtalk,im,head,exten,xstr,file,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_xtalk,im,head,exten,xstr,file,error=error,silent=silent

; Initalizing some variables
error = ''                        ; initialize error variable
errprefix = 'CCDPROC_XTALK: '   ; error message prefix

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
if n_elements(im) eq 0 or n_elements(head) eq 0 or n_elements(exten) eq 0 or $
   n_elements(xstr) eq 0 or n_elements(file) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_xtalk,im,head,exten,xstr,file,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check that IM is a data (type=1-5 or 12-15) 2D array
if CHECKPAR(im,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',errstr=error,silent=silent) then return
; Check that HEAD is a string array
if CHECKPAR(head,7,1,caller=errprefix+'Header - ',errstr=error,silent=silent) then return
; Check that EXTEN is a scalar integer
if CHECKPAR(head,[1,2,3],0,caller=errprefix+'Exten - ',errstr=error,silent=silent) then return
; Check that FILE has valid data
if CCDPROC_CHECKFILE(file,/data,caller=errprefix,errstr=error,silent=silent) then return

; Have we done this processing step already?
xtalkcor = sxpar(head,'XTALKCOR',count=nxtalkcor)
if nxtalkcor gt 0 then begin
  error = errprefix+'Xtalkcor correction already done.'
  if not keyword_set(silent) then print,error
  return
endif

; Check the xtalk structure
if CHECKPAR(xstr,8,caller=errprefix+'XSTR - ',errstr=error,silent=silent) then return
if tag_exist(xstr,'VICTIM') eq 0 or tag_exist(xstr,'SOURCE') eq 0 or tag_exist(xstr,'SCALE') then begin
  error = errprefix+'Cross-talk structure must have VICTIM, SOURCE and SCALE tags'
  if not keyword_set(silent) then print,error
  return
endif
; Check that the XTALK VICTIM is int/long
if CHECKPAR(xstr.victim,[2,3],caller=errprefix+'Xstr VICTIM - ',silent=silent,errstr=error) then return
; Check that the XTALK SOURCE is int/long
if CHECKPAR(xstr.source,[2,3],caller=errprefix+'Xstr SOURCE - ',silent=silent,errstr=error) then return
; Check that the XTALK SCALE is float/double
if CHECKPAR(xstr.scale,[4,5],caller=errprefix+'Xstr SCALE - ',silent=silent,errstr=error) then return

imsz = size(im)
imtype = size(im,/type)

; Find the entries in the xstr structure
ind = where(xstr.victim eq exten,nind)
if nind eq 0 then begin
  ; This is not an error
  if not keyword_set(silent) then print,'No XSTR entry for exten='+strtrim(exten,2)
  return
endif

; Loop through the source extensions
For i=0,nind-1 do begin

  ; Check that FILE 
  if CCDPROC_CHECKFILE(file,sz=imsz,exten=xstr[ind[i]].source,caller=errprefix,errstr=error,silent=silent) then return

  ; Load the "source" imge
  FITS_READ,file[0],srcim,srchead,exten=xstr[ind[i]].source,/no_abort,message=message
  if message ne '' then begin
    error = errprefix+'Error loading exten='+strtrim(xstr[ind[i]].source,2)+' of '+file[0]
    if not keyword_set(silent) then print,error
    return
  endif
  sz = size(srcim)

  ; Check image sizes
  if total(abs(imsz[0:2]-sz[0:2])) ne 0 then begin
    error = errprefix+'Source image not same size as victim image.'
    if not keyword_set(silent) then print,error
    return
  endif

  ; The images need to be aligned in read order or "amplifier coordinates".
  ; The flips are identified by the signs of the keywords ATM1_1 for line flips and ATM2_2 for column flips.

  ; Does the overscan get corrected as well?

  ; Subtract, should we round to nearest integer?
  im -= srcim*xstr[ind[i]].scale

  ;sdatasec = dcm_splitsec(sxpar(srchead,'DATASEC'+xstr[ind[k]].source_amp))-1
  ;sampsec = dcm_splitsec(sxpar(srchead,'AMPSEC'+xstr[ind[k]].source_amp))-1
  ;sim = srcim[sdatasec[0]:sdatasec[1],sdatasec[2]:sdatasec[3]]
  ;; Put source in READ order
  ;if sampsec[0] gt sampsec[1] then sim=reverse(sim,1)
  ;if sampsec[2] gt sampsec[3] then sim=reverse(sim,2)
  ;; Scale and round to integers
  ;sim_scale = round(sim*xstr[ind[k]].scale)
  ;; Subtract and make sure it's non-negative
  ;vim = (vim-sim_scale) > 0
  ;if xtalkhead eq '' then prefix='' else prefix='+'
  ;xtalkhead += prefix+strtrim(string(xstr[ind[k]].scale,format='(G12.3)'),2)+'*'+xstr[ind[k]].source


Endfor

;if xtalkhead eq '' then xtalkhead='No crosstalk correction'
;sxaddpar,head,'XTALKCR'+victim_amp,xtalkhead
;if keyword_set(verbose) then print,victim[j],' ',xtalkhead
;
;; Put victim back in original order
;if vampsec[0] gt vampsec[1] then vim=reverse(vim,1)
;if vampsec[2] gt vampsec[3] then vim=reverse(vim,2)
;; Stuff it back in the original image
;im[vdatasec[0]:vdatasec[1],vdatasec[2]:vdatasec[3]] = vim


im = round(im)   ; round the final image



; Add processing information to header
;--------------------------------------
;  Current timestamp information
;  Sun Oct  7 15:38:23 2012
date = systime(0)
datearr = strtrim(strsplit(date,' ',/extract),2)
timarr = strsplit(datearr[3],':',/extract)
datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
sdum = strjoin('im'+strtrim(xstr[ind].source,2)+'*'+strtrim(string(xstr[ind].scale,format='(G12.3)'),2),'+')
fxaddpar,head,'XTALKCOR',datestr+' Crosstalk is '+sdum

end
