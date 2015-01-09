;+
;
; CCDPROC_LOADXTALK
;
; This program loads the cross-talk file.
;
; INPUTS:
;  file         The cross-talk filename.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  xstr         The cross-talk structure with VICTIM, SOURCE and SCALE.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_loadxtalk,file,xstr,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_loadxtalk,file,xstr,error=error,silent=silent

; Initalizing some variables
undefine,xstr
error = ''                          ; initialize error variable
errprefix = 'CCDPROC_LOADXTALK: '   ; error message prefix

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
    print,'Syntax -  ccdproc_loadxtalk,file,xstr,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check file
if CCDPROC_CHECKFILE(file,/exists,caller=errprefix,silent=silent,errstr=error) then return

; Read the file
;--------------
READCOL,file,victim,source,scale,format='I,I,F',comment='#',/silent,count=count
if count eq 0 then begin
  error = 'No good lines in '+file+' Cross-talk file'
  if not keyword_set(silent) then print,error
  return
endif

; Make the XSTR structure
xstr = replicate({victim:0L,source:0L,scale:0.0},n_elements(victim))
xstr.victim = victim
xstr.source = source
xstr.scale = scale
; Check that file contents make sense

end
