function ccdproc_splitsec,str

; This function splits an IRAF sector
; string like [1:1024,1:4096] into a 4-element
; integer array

if n_elements(str) ne 1 then return,-1

str = strtrim(str,2)
len = strlen(str)
str2 = strmid(str,1,len-2)
dum = strsplit(str2,',',/extract)
if n_elements(dum) ne 2 then return,-1
str_x = strsplit(dum[0],':',/extract)
str_y = strsplit(dum[1],':',/extract)
out = [str_x,str_y]
if n_elements(out) ne 4 then return,-1
if total(valid_num(out,/integer)) ne 4 then return,-1

return,out

end
