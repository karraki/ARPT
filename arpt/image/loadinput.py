"""
 NAME:
  LOADINPUT

 PURPOSE:
  This program can be used to load command-line inputs.
  The input can be:
   (1) an array list of files, i.e. ['one.txt','two.txt']
   (2) a globbed list, i.e. "*.txt"
   (3) a comma separated list, i.e.  'one.txt,two.txt'
   (4) the name of a file that contains a list, i.e. "list.txt"
         This can NOT be used in combination with any of the other three options.

 INPUTS:
  input    The input list.  There are three possibilities
            (1) an array list of files
            (2) a globbed list, i.e. "*.txt"
            (3) a comma separated list, i.e.  'one.txt,two.txt'
            (4) the name of a file that contains a list, i.e. "@list.txt"
                  This can NOT be used in combination with any of the other three options.
  =comment Comment string to use when loading a list file. By default comment='#'
  /stp     Stop at the end of the program

 OUTPUTS:
  list     The list of files
  =count   The number of elements in list

 USAGE:
  loadinput('*.fits', list, count=count)

 By D.Nidever   April 2007
-
"""
def loadinput(input0, comment='#', stp=False):

# KENZA Q: undefine,list -> is None close enough?
    list = None
    count = 0

    # Not enough inputs
    if len(input0)==0:
        print 'Syntax - loadinput(input, comment=comment, stp=stp)'
        return list, count
    input = input0

    # Empty string input
    if input[0].split()=='':
        list = None
        count = 0
        return list, count

    # A list file was input
    if input[0][0:1]=='@':
        inp = input[0][1:]
        # Loading the files
# KENZA - change this function
        readline(inp, list, comment=comment, noblank=True)
        nlist = len(list)
    else:
        # Break up comma lists
        ninput = len(input)
        temp = None

        for i in range(0,ninput):
            dum = input[i].split(',')
            push(temp,dum)

        input = temp
        temp = None
        if len(input)==1: input=input[0]

        # Probably an array of filenames
        if len(input)>1:
            # Try to expand as wildcards
# KENZA - change this function
            wildind = where(strpos(input,'*')!=-1 or strpos(input,'?')!=-1, nwild)
            normind = where(strpos(input,'*')!=-1 and strpos(input,'?')!=-1,nnorm)

            # Some wildcards
            if nwild>0:
                list = None
# KENZA - change this function
                if nnorm>0: push(list,input[normind])
                wild = input[wildind]

                # Loop through the wildcards
                for i in range(0,nwild):
# KENZA - change this function
                    wfiles = file_search(wild[i],count=nwfiles)
# KENZA - change this function
                    if nwfiles>0: push(list,wfiles)
      
                nlist = len(list)

            # No wildcards
            else:
                list = input
                nlist = len(list)
            
        # A globbed list or only one file
        else:
# KENZA - change this function
            list = file_search(input, count=nlist)
            if nlist==0: list=input    # Maybe just one filename
            #nlist = len(list)

    count = len(list)
    if count==1: list=list[0]
    if stp: exit()
    return list, count
