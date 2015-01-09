;+
;
; CCDPROC_LOADFIXPIX
;
; This program loads the fixpix file.
;
; INPUTS:
;  file         The fixpix filename.
;  /silent      Don't print anything to the screen.
;
; OUTPUTS:
;  fixstr       The fixpix structure with XRANGE and YRANGE.
;  =error       The error message if one occurred.
;
; USAGE:
;  IDL>ccdproc_loadfixpix,file,fixstr,error=error,silent=silent
;
; By D. Nidever   April 2014
;-

pro ccdproc_loadfixpix,file,fixstr,error=error,silent=silent

; Initalizing some variables
undefine,fixstr
error = ''                          ; initialize error variable
errprefix = 'CCDPROC_FIXPIX: '   ; error message prefix

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
    print,'Syntax -  ccdproc_loadfixpix,file,fixstr,error=error,silent=silent'
  error = errprefix+'Not Enough Inputs'
  return
endif

; Check file
if CCDPROC_CHECKFILE(file,/exists,caller=errprefix,silent=silent,errstr=error) then return

; Read the file
;--------------
READLINE,file,fixlines,/noblank,count=count
if count eq 0 then begin
  error = 'No good lines in '+file+' fixpix file'
  if not keyword_set(silent) then print,error
  return
endif

; Make the FIXSTR structure
fixstr = replicate({x1:0L,y1:0L,x2:0L,y2:0L,nx:0L,ny:0L},count)
for i=0,count-1 do begin

  ; A  text  file  with lines giving the integer
  ; coordinates of a single pixel or a  rectangular  region.   A  single
  ; pixel  is  specified  by  a  column  and  line  number.  A region is
  ; specified by a starting column, an ending column, a  starting  line,
  ; and  an  ending  line. 

  arr = strsplit(strtrim(fixlines[i],2),' ',/extract)
  narr = n_elements(arr)

  ; Check that the numbers are integers
  valid = valid_num(arr,/integer)
  bad = where(valid eq 0,nbad)
  if nbad gt 0 then begin
    error = errprefix+'The fixpix lines must all be integers'
    if not keyword_set(silent) then print,error
    return
  endif
  ; Check that the numbers are positive
  bad = where(long(arr) le 0,nbad)
  if nbad gt 0 then begin
    error = errprefix+'The fixpix pixel numbers mast be >=1'
    if not keyword_set(silent) then print,error
    return
  endif

  case narr of
  2: begin
    fixstr[i].x1 = long(arr[0])
    fixstr[i].y1 = long(arr[1])
    fixstr[i].nx = 1
    fixstr[i].ny = 1
  end
  4: begin
    fixstr[i].x1 = long(arr[0])
    fixstr[i].x2 = long(arr[1])
    fixstr[i].y1 = long(arr[2])
    fixstr[i].y2 = long(arr[3])
    fixstr[i].nx = fixstr[i].x2-fixstr[i].x1+1
    fixstr[i].ny = fixstr[i].y2-fixstr[i].y1+1
  end
  else: begin
    error = errprefix+'The fixpix lines must have "X Y" or "X1 X2 Y1 Y2"'
    if not keyword_set(silent) then print,error
    return
  end
  endcase

  ; Check that X2>X1 and Y2>Y1
  if (fixstr[i].nx gt 1 and fixstr[i].x2 le fixstr[i].x1) or $
     (fixstr[i].ny gt 1 and fixstr[i].y2 le fixstr[i].y1) then begin
    error = errprefix+'The fixpix pixel numbers have X2>X1 and Y2>Y1'
    if not keyword_set(silent) then print,error
    return
  endif

endfor

end
