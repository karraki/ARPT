;+
;
; CCDPROC_CHECKFILE
;
; This function checks various properties of a file.
;
; INPUTS:
;  file        A scalar string of the filename.
;  =exten      The FITS file extension to check.
;  /exists     The file must exist (this is also checked if /validfits,
;                /data, or =size are set).
;  /validfits  The file is a valid FITS file (this is also set if
;                /data or =size are set).
;  /data       The file contains image data and is not binary fits
;                file (this is also checked if =size is set).
;  =size       An array of number of elements for each dimension,
;                e.g. size=[2048,2048].
;  =caller     The calling program.  This string as added at the
;                beginnning of ERRSTR.
;  /silent     Don't print anything to the screen.
;
; OUTPUTS:
;  The return value is 1/TRUE if the file FAILS any of the checks, and
;  0/FALSE if it passes all of the tests.
;  =errstr     The error string if the file failed one of the criteria
;  =info       Structure with information on the file.
;
; USAGE:
;  IDL>info = ccdproc_checkfile(filename,/validfits,info=info)
;
; By D. Nidever  April 2014
;-

function ccdproc_checkfile,file,exten=exten,exists=exists,validfits=validfits,data=data,size=size,$
                           caller=caller,errstr=errstr,info=info,silent=silent

; Initalizing some variables
errval = 0
error = ''                         ; initialize error variable
errprefix = 'CCDPROC_CHECKFILE: '   ; error message prefix
undefine,info

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
   return,1
endif

; No file input
if n_elements(file) eq 0 then begin
  if not keyword_set(silent) then begin
    print,'Syntax - val = ccdproc_checkfile(file,exists=exists,validfits=validfits,data=data,size=size,errstr=errstr,'
    print,'                                 caller=caller,info=info,silent=silent)'
  endif
  errstr = errprefix+'Not enough inputs.'
  if not keyword_set(silent) then print,errstr
  return,1
endif

; Get file info
info = CCDPROC_FILEINFO(file[0])

; Exists
;--------
if (keyword_set(exists) or keyword_set(validfits) or keyword_set(data) or n_elements(size) gt 0) and info.exists eq 0 then begin
  errstr = info.file+' NOT FOUND.'
  errval = 1
  goto,BOMB
endif

; Valid FITS
;------------
if (keyword_set(validfits) or keyword_set(data) or n_elements(size) gt 0) and info.validfits eq 0 then begin
  errstr = info.file+' is NOT a valid FITS file.'
  errval = 1
  goto,BOMB
endif

; Load the header
if keyword_set(validfits) or keyword_set(data) or n_elements(size) gt 0 then begin
  head = headfits(info.file,errmsg=errmsg,exten=exten)
  if errmsg ne '' then begin
    errstr = info.file+' cannot load FITS Header.'
    errval = 1
    goto,BOMB
  endif
endif

; DATA
;------
if (keyword_set(data) or n_elements(size) gt 0) and info.validfits eq 1 then begin
  ; All valid FITS non-binary files are DATA type
  ; if NAXIS=0 or XTENSION='BINTABLE' then errval=1
  ; Check that it's not a fits binary table

  naxis = sxpar(head,'NAXIS',count=n_naxis)
  xtension = sxpar(head,'XTENSION',count=n_xtension)
  if naxis eq 0 or (n_xtension gt 0 and strtrim(xtension,2) eq 'BINTABLE') then begin
    errstr = info.file+' is not DATA.'
    errval = 1
    goto,BOMB
  endif
endif

; SIZE
;------
if n_elements(size) gt 0 and info.validfits eq 1 then begin
  naxis = sxpar(head,'NAXIS',count=n_naxis)
  if naxis gt 0 then begin
    imsize = lonarr(naxis)
    for i=0,naxis-1 do begin
      naxis1 = sxpar(head,'NAXIS'+strtrim(i+1,2),count=n_naxis1)
      if n_naxis1 gt 0 then imsize[i]=long(naxis1)
    endfor
  endif
  nimdim = n_elements(imsize)
  ndim = n_elements(size)

  ; Number of dimensions different
  if nimdim ne ndim then begin
    errstr = info.file+' has wrong number of dimensions.  Must be '+strtrim(ndim,2)+'.'
    errval = 1
    goto,BOMB
  endif
  ; Sizes different
  if total(abs(imsize-size)) ne 0 then begin
    errstr = info.file+' has wrong size, must be ['+strjoin(strtrim(size,2),',')+'].'
    errval = 1
    goto,BOMB
  endif
endif

BOMB:

; There was a failure
if errval eq 1 then begin
  if n_elements(caller) gt 0 then errstr=caller+errstr
  if not keyword_set(silent) then print,errstr
endif

return,errval

end
