#!/usr/bin/env python
import os
import sys
import subprocess

def getMovieFiles(argv):

  exts=[]
  filelist={}
  dirfiles=[]

  for x in range(1,10):
    exts.append(".CD{0}.avi".format(x))

  for root, dirs, files in os.walk(argv[0]):
    for dir in dirs:    
      for ext in exts:
        for name in os.listdir(os.path.join(root, dir)):
          if name.find(ext) != -1:
            dirfiles.append(os.path.join(root, dir, name))
            filelist[os.path.join(root, dir)] = dirfiles
      dirfiles=[]

  movielist = sorted(filelist.items(), key = lambda t: t[0])
  return dict(movielist)

def process(movies):
  for movie in movies.keys():
    moviename = movie + '.txt'	  
    f = open(moviename, 'w') 
    for moviepart in movies[movie]:
      f.write('file ' + moviepart + '\n')	
    f.close
    
    ext = os.path.splitext(moviepart)[1].lower()
    moviename_output = movie + "/" + movie + ext
    #movienamepath = os.path.join(root, moviename)
    print(moviename)
    #moviename_outputpath = os.path.join(root, moviename_output)
    print(moviename_output)
    command = "ffmpeg -f concat -i {0} -c copy {1}".format(unicode(moviename), unicode(moviename_output))
    print(command)
    p = subprocess.call(command)

def usage(EXIT_CODE):

  print("")
  print("Usage: flatten.py <movies_root_directory>")
  sys.exit(EXIT_CODE)

def main(argv):

  if (len(argv) == 0 or len(argv) >= 2): usage(1)
  
  movielist = getMovieFiles(argv)
  if not movielist:
    print("No movies to process")
  else:
    process(movielist)

if __name__ == "__main__":
  try:
    main(sys.argv[1:])
  except (KeyboardInterrupt, SystemExit) as e:
    if type(e) == SystemExit: sys.exit(int(str(e)))