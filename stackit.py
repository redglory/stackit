#!/usr/bin/env python
import os, sys
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
          uppername = name.upper()
          if uppername.find(ext.upper()) != -1:
            dirfiles.append(os.path.join(root, dir, name))
            filelist[os.path.join(root, dir)] = dirfiles
      dirfiles=[]

  movielist = sorted(filelist.items(), key = lambda t: t[0])
  return dict(movielist)

def process(movies):
  for moviepath in movies.keys():
    moviename = moviepath + '.txt'	  
    f = open(moviename, 'w') 
    for moviepart in movies[moviepath]:
      f.write('file ' + "'" + moviepart + "'" + '\n')	
    f.close
    
    extension = os.path.splitext(moviepart)[1].lower()
    movie_output = moviepart.rsplit('.',2)[0] + extension
    
    command = "ffmpeg -f concat -i {0} -c copy {1} -loglevel verbose".format(unicode(moviename), unicode(movie_output))
    print(command)
    subprocess.call(command, shell=True)

def usage(EXIT_CODE):

  print("===============================================")
  print("== Usage: stackit.py <movies_root_directory> ==")
  print("===============================================")
  sys.exit(EXIT_CODE)

def main(argv):

  if (len(argv) == 0 or len(argv) >= 2): usage(1)
  
  movielist = getMovieFiles(argv)
  #print(movielist)
  if not movielist:
    print("No movies on %s to process" % argv[0])
  else:
    process(movielist)

if __name__ == "__main__":
  try:
    main(sys.argv[1:])
  except (KeyboardInterrupt, SystemExit) as e:
    if type(e) == SystemExit: sys.exit(int(str(e)))