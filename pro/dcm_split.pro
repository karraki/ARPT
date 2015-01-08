pro dcm_split,input


; Not enough inputs
if n_elements(input) eq 0 then begin
  print,'Syntax - dcm_split,files'
  return
endif

; Load the input
loadinput,input,file,count=nfiles

; More than one file input
if nfiles gt 1 then begin
  for i=0,nfiles-1 do dcm_split,file[i]
  return
endif

if file_test(file) eq 0 then begin
  print,file,' NOT FOUND'
  return
endif

base = file_basename(file,'.fits')
dir = file_dirname(file)+'/'

fits_open,file,fcb
next = fcb.nextend
fits_close,fcb

print,'Splitting ',file,' Nextend=',strtrim(next,2)

head0 = headfits(file,exten=0)

for i=1,next do begin

  fits_read,file,im,head,exten=i

  ; Fix header
  sxdelpar,head,'NEXTEND'
  sxdelpar,head,'PCOUNT'
  sxdelpar,head,'GCOUNT'
  sxdelpar,head,'EXTNAME'
  head[0] = 'SIMPLE  =                    T /image conforms to FITS standard'

  bd = where(stregex(head,'^BEGIN MAIN',/boolean) eq 1 or $
             stregex(head,'^BEGIN EXTEN',/boolean) eq 1,nbd)
  if nbd gt 0 then REMOVE,bd,head

  ;; add rdnoise
  ;sxaddpar,head,'rdnoise',sxpar(head,'rdnoisea')

  outfile = base+'_'+strtrim(i,2)+'.fits'
  mwrfits,im,outfile,head,/create
  ; for some reason fits_write is creating a dummy PDU
  ; and putting this in HDU1. mwrfits does it correctly.

  ;stop

endfor

;stop

end
