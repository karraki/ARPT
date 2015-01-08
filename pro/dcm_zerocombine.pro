pro dcm_zerocombine,input,outfile,median=median


; Not enough inputs
if n_elements(input) eq 0 or n_elements(outfile) eq 0 then begin
  print,'Syntax - dcm_zerocombine,input,outfile,median=median'
  return
endif

; Load the input
loadinput,input,files,count=nfiles
files = strtrim(files,2)

; Pull out first column
dum = strsplitter(files,' ',/extract)
sz = size(dum)
if sz[0] gt 1 then files = reform(dum[0,*])
files = strtrim(files,2)

origfiles = files
base = file_basename(files,'.fits')
files = base+'.fits'

test = file_test(files)
bd = where(test eq 0,nbd)
if nbd gt 0 then begin
  print,files[bd],' NOT FOUND'
  return
endif

print,'Combining ',files

fits_open,files[0],fcb
next = fcb.nextend
fits_close,fcb

head0 = headfits(files[0],exten=0)

for j=0,nfiles-1 do sxaddpar,head0,'IMCMB'+string(j+1,format='(I03)'),files[j]
sxaddpar,head0,'NCOMBINE',nfiles

; Start output file
fits_write,outfile,0,head0

for i=1,next do begin

  fits_read,files[0],im,head,exten=i,/no_pdu
  sz = size(im)

  imarr = fltarr(sz[1],sz[2],nfiles)
  imarr[*,*,0] = float(im)

  ; Load the files
  for j=1,nfiles-1 do begin
    fits_read,files[j],im,head,exten=i
    imarr[*,*,j] = float(im)
  endfor

  ; Median
  if keyword_set(median) then begin
    fim = median(imarr,dim=3)

  ; Mean
  endif else begin
    fim = total(imarr,3)/nfiles
  endelse

  ; Round to LONG
  fim = round(fim)

  ; Save
  MWRFITS,fim,outfile,head,/silent

  ;stop

endfor


;stop

end
