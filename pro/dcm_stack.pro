pro dcm_stack,coords,width,fileinput

; Stack DECam images
; Use a tile system.  Input the coordinates of the center and the
; width, as well as list of images.
; Do each filter separately
; Loop through the images/chips and figure out which ones over the
; tile, then interpolate it onto the new grid
; Use aperture photometry of the stars to scale it appropariately
; What to do about the background?
; Maybe create a giant stack/cube first and then do things with
; sources detection/photometry, scaling, background subtraction
; afterwards (could use up a lot of memory though).


if n_elements(coords) eq 0 or n_elements(width) eq 0 or n_elements(fileinput) eq 0 then begin
  print,'Syntax - dcm_stack,coords,width,fileinput'
  return
endif

loadinput,fileinput,files,count=nfiles,/exist

; Loop through the files
for i=0,nfiles-1 do begin

  file = files[i]
  
  fits_open,file,fcb
  next = fcb.nextend
  fits_close,fcb

  head0 = headfits(file,exten=0)

  ; Load the headers
  str = PTR_NEW({file:file,head:head0})
  for j=1,next do begin
    head = headfits(file,exten=j)
    naxis1 = sxpar(head,'NAXIS1')
    naxis2 = sxpar(head,'NAXIS2')
    x = [0,naxis1-1,naxis1-1,0]
    y = [0,0,naxis2-1,naxis2-1]
    head_xyad,head,x,y,rr,dd,/deg
    head_xyad,head,(naxis1-1)*0.5,(naxis2-1)*0.5,cenra,cendec,/deg
    stop
    PUSH,str,PTR_NEW({file:file,head:head,cenra:cenra,cendec:cendec,ra:rr,dec:dd})
  endfor

  dir = file_dirname(file)+'/'
  base = file_basename(file,'.fits')
  if outfile eq '' then outfile=dir+base+'_bin.fits'

  stop

endfor


stop

end
