;+
;
; CCDPROC_LOADBSTRAP
;
; This program loads the bootstrap file.
;
; INPUTS:
;  file         The bootstrap filename.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  bootstr      The bootstrap structure with EXTEN and SCALE.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_loadbootstrap,file,bootstr,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_loadbootstrap,file,bootstr,error=error,silent=silent

; Initalizing some variables
undefine,bootstr
error = ''                          ; initialize error variable
errprefix = 'CCDPROC_LOADBOOTSTRAP: '   ; error message prefix

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
if n_elements(file) eq 0 then begin
  if not keyword_set(silent) then $
    print,'Syntax -  ccdproc_loadbootstrap,file,bootstr,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check file
if CCDPROC_CHECKFILE(file,/exists,caller=errprefix,silent=silent,errstr=error) then return

; Read the file
;--------------
; Must be two column format: EXTEN, SCALE
READCOL,bootstrap,exten,scale,format='I,F',/silent,count=count
if count eq 0 then begin
  error = 'No good lines in '+file+' Bootstrap file'
  if not keyword_set(silent) then print,error
  return
endif

; Make the BOOTSTR structure
bootstr = replicate({exten:0L,scale:0.0},n_elements(exten))
bootstr.exten = exten
bootstr.scale = scale

; Check that file contents make sense

end
