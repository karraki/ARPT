pro dcm_ccdlist,input

if n_elements(input) eq 0 then input='*.fits'

loadinput,input,files,count=nfiles,/exist

for i=0,nfiles-1 do begin

  ;fits_open,files[i],fcb
  ;next = fcb.nextend
  ;fits_close,fcb

  if file_test(files[i]) eq 0 then begin
    print,files[i],' NOT FOUND'
    goto,BOMB
  endif

  head0 = headfits(files[i],exten=0)
  head = headfits(files[i],exten=1,errmsg=errmsg)

  psteps=''
  if errmsg eq '' then begin
    dum = sxpar(head,'TRIM',count=count,/silent)
    if count gt 0 then psteps+='T'
    dum = sxpar(head,'OVERSCAN',count=count,/silent)
    if count gt 0 then psteps+='O'
    dum = sxpar(head,'ZEROCOR',count=count,/silent)
    if count gt 0 then psteps+='Z'
    dum = sxpar(head,'FLATCOR',count=count,/silent)
    if count gt 0 then psteps+='F'
    dum = sxpar(head,'BTPSTEPSP',count=count,/silent)
    if count gt 0 then psteps+='S'
    dum = sxpar(head,'BPM',count=count,/silent)
    if count gt 0 then psteps+='B'
    dum = sxpar(head0,'NCOMBINE',count=count,/silent)  ; PDU
    if count gt 0 then psteps+='C'
    bitpix = sxpar(head,'BITPIX')
    bzero = sxpar(head,'BZERO')
    naxis1 = sxpar(head,'NAXIS1')
    naxis2 = sxpar(head,'NAXIS2')
  endif
  object = sxpar(head0,'OBJECT')

  filter = strtrim(sxpar(head0,'FILTER'),2)
  dum = strtrim(strsplitter(filter,' ' ,/extract),2)
  sfilter = dum[0]
  obstype = strtrim(sxpar(head0,'OBSTYPE'),2)
  if obstype eq 'dome flat' then obstype='dflat'
  exptime = strtrim(string(sxpar(head0,'EXPTIME'),format='(F8.2)'),2)

  base = file_basename(files[i])

  size = strtrim(naxis1,2)+','+strtrim(naxis2,2)
  case bitpix of
  8: type='byte'
  16: type='int'
  32: type='long'
  -32: type='real'
  -64: type='double'
  else: type=''
  endcase

  ;fmt = '(A-20,A-10,A-50)'
  print,base,'['+size+']','['+type+']','['+obstype+']','['+sfilter+']',$
        '['+psteps+']',': ',object,'  ',exptime

  BOMB:

endfor

;stop

end
