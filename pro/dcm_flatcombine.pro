pro dcm_flatcombine,input,outbase,median=median,verbose=verbose,silent=silent


; Not enough inputs
if n_elements(input) eq 0 then begin
  print,'Syntax - dcm_flatcombine,input,outbase,median=median,verbose=verbose,silent=silent'
  return
endif

if n_elements(outbase) eq 0 then outbase='Dflat'
if n_elements(median) eq 0 then median=1  ; median by default

; Load the input
loadinput,input,files,count=nfiles
files = strtrim(files,2)

; Pull out first column
dum = strsplitter(files,' ',/extract)
sz = size(dum)
if sz[0] gt 1 then files = reform(dum[0,*])
files = strtrim(files,2)

test = file_test(files)
bd = where(test eq 0,nbd)
if nbd gt 0 then begin
  print,files[bd],' NOT FOUND'
  return
endif

; Get the info
info = replicate({file:'',object:'',obstype:'',exptime:0.0,filter:'',shortfilter:''},nfiles)
for i=0,nfiles-1 do begin
  head = headfits(files[i])
  info[i].file = files[i]
  info[i].object = strtrim(sxpar(head,'OBJECT',/silent),2)
  info[i].obstype = strtrim(sxpar(head,'OBSTYPE',/silent),2)
  info[i].exptime = sxpar(head,'EXPTIME',/silent)
  info[i].filter = strtrim(sxpar(head,'FILTER',/silent),2)
  dum = strtrim(strsplitter(info[i].filter,' ' ,/extract),2)
  info[i].shortfilter = dum[0]  ; first character
endfor

ui = uniq(info.shortfilter,sort(info.shortfilter))
shortfilter = info[ui].shortfilter
nshortfilter = n_elements(shortfilter)
print,'Filter ',strjoin(shortfilter,', ')

; Loop through the unique filters
for i=0,nshortfilter-1 do begin

  print,'Filter = ',shortfilter[i]
  ind = where(info.shortfilter eq shortfilter[i],nind)

  if nind lt 2 then begin
    print,'Need at least 2 frames per filter'
    goto,BOMB
  endif

  ifiles = files[ind]

  outfile = outbase+'_'+shortfilter[i]+'.fits'

  fits_open,ifiles[0],fcb
  next = fcb.nextend
  fits_close,fcb

  head0 = headfits(ifiles[0],exten=0)

  for j=0,nind-1-1 do sxaddpar,head0,'IMCMB'+string(j+1,format='(I03)'),ifiles[j]
  sxaddpar,head0,'NCOMBINE',nind

  ; Start output file
  fits_write,outfile,0,head0

  ; Keep track of the means
  mnarr = fltarr(next)

  ; Extension loop
  for j=1,next do begin

    fits_read,ifiles[0],im,head,exten=j,/no_pdu
    sz = size(im)

    imarr = fltarr(sz[1],sz[2],nind)
    exptime = fltarr(nind)

    exptime[0] = sxpar(head,'EXPTIME',/silent)
    imarr[*,*,0] = float(im)/exptime[0]


    ; Load the files
    for k=1,nind-1 do begin
      fits_read,ifiles[k],im,head,exten=j
      exptime[k] = sxpar(head,'EXPTIME',/silent)
      imarr[*,*,k] = float(im)/exptime[k]
    endfor

    ; Median
    if keyword_set(median) then begin
      fim = median(imarr,dim=3,/even)

    ; Mean
    endif else begin
      fim = total(imarr,3)/nind
    endelse

    ; Debugging
    ;diff=imarr
    ;for k=0,nind-1 do diff[*,*,k]-=fim

    ; Divide by the median, NOT DOING THIS ANYMORE
    ;med = median(fim)
    ;fim /= med
    ;mn = mean(fim)
    mn = median(fim,/even)
    mnarr[j-1] = mn
    sxaddpar,head,'CHIPMEAN',mn
    if keyword_set(verbose) then print,string(j,format='(I2)'),' Mean = ',string(mn,format='(F8.1)')

    ; Make sure there aren't any bad pixels
    bdpix = where(fim le 0.1,nbdpix)
    if nbdpix gt 0 then fim[bdpix]=mn  ; set to median

    ;displayc,fim,min=0.8,max=1.2,tit=j

    ;stop

    ;print,sxpar(head,'DETSEC')
    ;detsec = dcm_splitsec(sxpar(head,'DETSEC'))
    ;if detsec[0] gt 1500*8 and detsec[2] gt 2800*8 then stop,'This one'


    ; Save
    MWRFITS,fim,outfile,head,/silent

    ;stop

  endfor ; extension loop

  ; Update PDU with overall mean
  ccdmean = mean(mnarr[0:61])  ; only use the 62 science chips
  head0 = headfits(outfile,exten=0)
  sxaddpar,head0,'CCDMEAN',ccdmean
  MODFITS,outfile,0,head0,exten_no=0

  if not keyword_set(silent) then print,'CCDMEAN = ',string(ccdmean,format='(F9.1)')

  ;stop

  BOMB:

endfor  ; filter loop

;stop

end
