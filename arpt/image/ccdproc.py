;+
;
; CCDPROC
;
; This is a generic CCD image processing program.
;
; INPUTS:
;  input       The input list of images.
;  =xtalk
;  =lincorr    Apply linearity correction
;  =fixpix
;  /trim
;  /overscan
;  /gaincorr
;  =zero
;  =flat
;  =illum      Apply
;  =bootstrap  Apply bootstrap correction.
;  =bpm        Apply bad pixel mask using 
;  /clobber
;  /verbose
;  /silent     Don't print anything to the screen.
; 
; OUTPUTS:
;  =error      Error if one occured.
;
; USAGE:
;  IDL>
;
; By D.Nidever  Jan 2014,  based in part on IRAF's ccdproc program
;-

pro ccdproc,input,fixpix=fixpix,trim=trim,overscan=overscan,gaincorr=gaincorr,zero=zero,$
                flat=flat,xtalk=xtalk,illum=illum,bootstrap=bootstrap,bpm=bpm,clobber=clobber,verbose=verbose,$
                lincorr=lincorr,silent=silent,error=error


;====================
; CHECK THE INPUTS
;====================

; Not enough inputs
if n_elements(input) eq 0 then begin
  print,'Syntax - ccdproc,files,editgain=editgain,fixpix=fixpix,xtalk=xtalk,trim=trim,overscan=overscan,'
  print,'                 zero=zero,flat=flat,illum=illum,bootstrap=bootstrap,bpm=bpm,'
  print,'                 lincorr=lincorr,clobber=clobber,verbose=verbose,silent=silent,error=error'
  return
endif

; Load the input files
LOADINPUT,input,files,count=nfiles
files = strtrim(files,2)
if nfiles eq 0 then begin
  error = 'No files to process'
  if not keyword_set(silent) then print,error
  return
endif

; No processing steps requested
if not keyword_set(fixpix) and n_elements(xtalk) eq 0 and not keyword_set(trim) and not keyword_set(overscan) and $
   n_elements(zero) eq 0 and and n_elements(flat) eq 0 and n_elements(illum) eq 0 then begin
  error = 'NO PROCESSING STEPS'
  if not keyword_set(silent) then print,error
  return
endif

; Get file information
;   this also works if there is no input or the file doesn't exist
xtalk_info = CCDPROC_FILEINFO(xtalk)
lincorr_info = CCDPROC_FILEINFO(lincorr)
fixpix_info = CCDPROC_FILEINFO(fixpix)
zero_info = CCDPROC_FILEINFO(zero)
flat_info = CCDPROC_FILEINFO(flat)
illum_info = CCDPROC_FILEINFO(illum)
bootstrap_info = CCDPROC_FILEINFO(bootstrap)
bpm_info = CCDPROC_FILEINFO(bpm)

; Check that files exist if input
if n_elements(xtalk) gt 0 and xtalk_info.exists eq 0 then error='XTALK file '+xtalk_info.file+' NOT FOUND'
if n_elements(lincorr) gt 0 and lincorr_info.exists eq 0 then error='LINCORR file '+lincorr_info.file+' NOT FOUND'
if n_elements(fixpix) gt 0 and fixpix_info.exists eq 0 then error='FIXPIX file '+fixpix_info.file+' NOT FOUND'
if n_elements(zero) gt 0 and zero_info.exists eq 0 then error='ZERO file '+zero_info.file+' NOT FOUND'
if n_elements(flat) gt 0 and flat_info.exists eq 0 then error='FLAT file '+flat_info.file+' NOT FOUND'
if n_elements(illum) gt 0 and illum_info.exists eq 0 then error='ILLUM file '+illum_info.file+' NOT FOUND'
if n_elements(bootstrap) gt 0 and bootstrap_info.exists eq 0 then error='Bootstrap file '+bootstrap_info.file+' NOT FOUND'
if n_elements(bpm) gt 0 and bpm_info.exists eq 0 then error='BPM file '+bpm_info.file+' NOT FOUND'
if n_elements(error) gt 0 then begin
  if not keyword_set(silent) then print,error
  return
endif

; That that NEXTEND for the cal files is big enough for the input files

; Some defaults
if n_elements(zero) eq 0 then zero=''
if n_elements(flat) eq 0 then flat=''
if n_elements(illum) eq 0 then illum=''


;=========================================
; LOAD CALIBRATION DATA USED BY ALL FILES
;=========================================

; Load bootstrap file
if n_elements(bootstrap) gt 0 then begin
  CCDPROC_LOADBOOTSTRAP,bootstrap,bootstr,error=error,silent=silent
  if error ne '' then return
endif
; Load xtalk values
if n_elements(xtalk) gt 0 then begin
  CCDPROC_LOADXTALK,xtalk,xstr,error=error,silent=silent
  if error ne '' then return
endif
; Load fixpix file
if n_elements(fixpix) gt 0 then begin
  CCDPROC_LOADFIXPIX,fixpix,fixstr,error=error,silent=silent
  if error ne '' then return
endif

; Print out processing steps
if not keyword_set(silent) begin
  then print,'Processing steps:'
  if n_elements(xtalk) gt 0 then print,'XTALK ',xtalk
  if n_elements(lincorr) gt 0 then print,'LINCORR ',lincorr
  if n_elements(fixpix) gt 0 then print,'FIXPIX ',fixpix
  if keyword_set(trim) then print,'TRIM'
  if keyword_set(overscan) then print,'OVERSCAN'
  if zero ne '' then print,'ZERO ',zero
  if flat ne '' then print,'FLAT ',flat
  if illum ne '' then print,'ILLUM ',illum
  if n_elements(bootstrap) gt 0 then print,'BOOTSTRAP ',bootstrap
  if n_elements(bpm) gt 0 then print,'BPM ',bpm
endif


;=================
; PROCESS FILES
;=================

; Loop over input files
error = strarr(nfiles)
FOR f=0L,nfiles-1 do begin

  ; File information and headers
  info = CCDPROC_FILEINFO(files[f])
  origfile = info.file
  outfile = info.dir+'/'+info.base+'_temp.fits'

  ; File does not exist
  if info.exists eq 0 then begin
    error[f] = origfile+' NOT FOUND'
    if not keyword_set(silent) then print,error[f]
    goto,BOMBFILE
  endif
  ; Not a FITS file
  if info.ext ne 'fits' then begin
    error[f] = origfile+' NOT A FITS FILE'
    if not keyword_set(silent) then print,error[f]
    goto,BOMBFILE
  endif

  if not keyword_set(silent) then print,'Processing ',info.base+'.fits'


  ; Initialize output file
  FILE_DELETE,outfile,/allow_nonexistent,/quiet
  if next gt 1 then FITS_WRITE,outfile,0,*(info.hdu[0].head),/no_abort  ; for multi-extension

  ;---------------------------
  ; LOOP OVER THE EXTENSIONS
  ;---------------------------
  if next eq 0 then begin
    loext = 0L
    no_pdu = 0
  endif else begin
    loext = 1L
    no_pdu = 1
  endelse
  FOR i=loext,loext+next-1 do begin

    ; Load the file
    FITS_READ,file,im,head,exten=i,no_pdu=no_pdu,/no_abort,message=error1
    if error1 ne '' then goto,BOMBFILE
    origim = im
    im = float(im)

    ; Check the image and header
    ; Check that IM is a data (type=1-5 or 12-15) 2D array
    if CHECKPAR(zeroim,[1,2,3,4,5,12,13,14,15],[2],caller=errprefix+'Image - ',silent=silent,errstr=error1) then goto,BOMBFILE
    ; Check that HEAD is a string array
    if CHECKPAR(zerohead,7,1,caller=errprefix+'Header - ',silent=silent,errstr=error1) then goto,BOMBFILE


    ;str = {im:im,head:head,fixpix:keyword_set(fixpix),overtrim:keyword_set(overtrim),$
    ;       zero:'',flat:''}


    ; Cross-talk
    ;-----------
    if n_elements(xtalk) gt 0 then begin
       CCDPROC_XTALK,im,head,i,xstr,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Linearity Correction
    ;---------------------
    if n_elements(lincorr) gt 0 then begin
      CCDPROC_LINCORR,im,head,i,linstr,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Fixpix
    ;----------
    if n_elements(fixpix) gt 0 then begin
      CCDPROC_FIXPIX,im,head,fixstr,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Overscan
    ;---------
    if keyword_set(overscan) then begin
      CCDPROC_OVERSCAN,im,head,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Trim
    ;-----
    if keyword_set(trim) then begin
      CCDPROC_TRIM,im,head,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Zero Correct
    ;-------------
    if zero ne '' then begin
      CCDPROC_ZERO,im,head,zero,exten=i,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Domeflat Correct
    ;-----------------
    if flat ne '' then begin
      CCDPROC_FLAT,im,head,zero,exten=i,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Illumination Correction
    ;-------------------------
    ; maybe this should be called sflatcor
    if illum ne '' then begin
      CCDPROC_ILLUM,im,head,zero,exten=i,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Bootstrap
    ;----------
    if n_elements(bootstrap) gt 0 then begin
      CCDPROC_BOOTSTRAP,im,head,bootstr,exten=i,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif
    ; Bad Pixel Mask
    ;----------------
    if n_elements(bpm) gt 0 then begin
      CCDPROC_BPM,im,head,bpm,exten=i,error=error1,silent=silent
      if error1 ne '' then goto,BOMBFILE
    endif

    ; SHOULD LINEARITY CORRECTION GO BEFORE XTALK-CORRECTION????
    ; Dark correction??
    ; Fringe correction?

    ; Example of how the header is modified.
    ;XTALKCOR= 'Oct  8 21:19 No crosstalk correction required'                       
    ;OVSNMEAN=             1503.989                                                  
    ;TRIM    = 'Oct  8 21:19 Trim is [25:1048,1:4096]'                               
    ;FIXPIX  = 'Oct  8 21:19 Fix mscdb$noao/Mosaic2/CAL0102/bpm3_0102 + sat + bleed' 
    ;OVERSCAN= 'Oct  8 21:19 Overscan is [1063:1112,1:4096], mean 1503.989'          
    ;ZEROCOR = 'Oct  8 21:19 Zero is Zero[im5]'                                      
    ;FLATCOR = 'Oct  8 21:19 Flat is DFlatM.fits[im5], scale 10490.72'               
    ;CCDPROC = 'Oct 18 11:34 CCD processing done'                                    
    ;PROCID  = 'ct4m.20070817T081040V3'                                              
    ;SFLATCOR= 'Oct 18 11:34 Sky flat is Sflatn12M.fits[im5], scale 833.0756'        

    ; Add final processing info to header
    date = systime(0)
    datearr = strtrim(strsplit(date,' ',/extract),2)
    timarr = strsplit(datearr[3],':',/extract)
    datestr = datearr[1]+' '+datearr[2]+' '+strjoin(timarr[0:1],':')
    fxaddpar,head,'CCDPROC',datestr+' CCD processing done'

    ; Do we need to change BITPIX, BSCALE, BZERO, etc??

    ; Write output
    MWRFITS,im,outfile,head,/silent

    ;stop

  ENDFOR  ; extension loop

  ; THE PROCESSING STEPS SHOULD GO IN THE PRIMARY HEADER!!!

  ; Move temporary file to original file
  if not keyword_set(clobber) then $
    FILE_MOVE,outfile,file,/overwrite,/allow

  BOMBFILE:
  ; An error occured
  if error1 ne '' then begin
    error[f] = error1
    if not keyword_set(silent) then print,error[f]
    FILE_DELETE,outfile,/allow_nonexistent,/quiet  ; delete temporary file
  endif

ENDFOR  ; file loop

;stop

end
