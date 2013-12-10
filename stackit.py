#!/usr/bin/env python
import os, sys
import subprocess
import time
import logging
import shlex

global movie_count

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

  logging.basicConfig(filename="stackit.log", level=logging.DEBUG, filemode = 'w')

  movie_count = 0
  startTime = time.time()
  
  for moviepath in movies.keys():
    moviename = moviepath + '.txt'
    f = open(moviename, 'w') 
    for moviepart in movies[moviepath]:
      f.write('file ' + "'" + moviepart + "'" + '\n')
    f.flush()	  
    f.close()
    
    extension = os.path.splitext(moviepart)[1].lower()
    movie_output = moviepart.rsplit('.',2)[0] + extension
    movie_count += 1
	
    try:
      print("Please wait, stacking movie: %s..."% moviepath)
      logging.info("Stacking movie: %s"% moviepath)
      ffmpeg_command = ["ffmpeg", "-f", "concat", "-i", moviename, "-c", "copy", "-y", movie_output]
      logging.info("Running FFMPEG with arguments: %s"% ffmpeg_command)
      #response = subprocess.check_output(ffmpeg_command, stderr=subprocess.STDOUT).decode("utf-8")
      ffmpeg = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      output, errors = ffmpeg.communicate()
      if ffmpeg.returncode == 0:	  
        print("Stacking movie: %s finished successfully!"% moviepath)
        logging.info(output + '\n')
        logging.info("Stacking movie: %s finished successfully!\n"% moviepath)
    except OSError:
        logging.debug('OS Error')
    except subprocess.CalledProcessError as e:
      print("[FFMPEG ERROR] Stacking movie: %s was unsuccessfully! \n"% moviepath)
      logging.debug("[FFMPEG ERROR] Stacking movie: %s was unsuccessfully!"% moviepath + str(e))

  endTime = time.time()
  proc_time = str((round(endTime - startTime) / 60))
  print("#############################################")
  print("## [%i] Movie(s) were stacked successfully! ##"% movie_count)
  print("#############################################")
  logging.info("##################################################################")
  logging.info("## [%i] Movie(s) were stacked successfully. Runtime: %s seconds ##"% (movie_count, proc_time))
  logging.info("##################################################################")
  
def main(argv):

  if (len(argv) == 0 or len(argv) >= 2):
    print("============================================================")
    print("== How to use stackit: stackit.py <movies_root_directory> ==")
    print("============================================================")
    sys.exit(1)
  
  movielist = getMovieFiles(argv)
  if not movielist:
    print("No movies on %s to process" % argv[0])
  else:
    process(movielist)

if __name__ == "__main__":

  try:
    main(sys.argv[1:])
  except (KeyboardInterrupt, SystemExit) as e:
    if type(e) == SystemExit: sys.exit(int(str(e)))