#!/usr/bin/env python
import os, sys
import subprocess
import time
import logging
import errno

global movie_count

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else: 
      raise 

def create_log(logfile):
    mkdir_p(os.path.join(os.getcwd(), "logs"))
    logging.basicConfig(filename=logfile,
                        filemode='w',
                        format='%(asctime)s,%(msecs)d :: [%(name)s] :: [%(levelname)s] %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    return logging.getLogger(__name__)
	
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
 
def remove_file(filepath):
   try:
     os.remove(os.path.realpath(filepath))
     Logger.info("Permanently removed file %s!"% filepath)
   except Exception as e:
     Logger.error("There was a problem removing file: %s!"% filepath)
     raise

def process(movies):

  movie_count = 0
  movie_error_count = 0
  startTime = time.time()
  
  for moviepath in movies.keys():
    movietxt = moviepath + '.txt'
    f = open(movietxt, 'w') 
    for moviepart in movies[moviepath]:
      f.write('file ' + "'" + moviepart + "'" + '\n')
    f.flush()	  
    f.close()
    
    extension = os.path.splitext(moviepart)[1].lower()
    movie_output = moviepart.rsplit('.',2)[0] + extension
	
    try:
      print("Please wait, stacking movie: %s..."% moviepath)
      Logger.info("Stacking movie: %s"% moviepath)
      ffmpeg_command = ["ffmpeg", "-f", "concat", "-i", movietxt, "-c", "copy", "-y", movie_output]
      Logger.info("Running FFMPEG with arguments: %s"% ffmpeg_command)
      #response = subprocess.check_output(ffmpeg_command, stderr=subprocess.STDOUT).decode("utf-8")
      ffmpeg = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      output, errors = ffmpeg.communicate()
      if ffmpeg.returncode == 0:	  
        print("Stacking movie: %s finished successfully!"% moviepath)
        Logger.info(output + '\n')
        Logger.info("Stacking movie: %s finished successfully!"% moviepath)
        time.sleep(2)
        Logger.info("Cleaning Up movie: %s by removing part files and temporary input file: %s!"% (moviepath, movietxt))
        for moviepart in movies[moviepath]:
          remove_file(moviepart)  
        remove_file(movietxt)
        Logger.info("Finished cleaning up movie: %s successfully!"% moviepath)
        movie_count += 1		
      else:
        Logger.error(output + '\n')
        Logger.error("Stacking movie: %s was unsuccessfully!"% moviepath)
    except OSError:
        Logger.debug('OS Error')
        raise
        movie_error_count += 1
    except subprocess.CalledProcessError as e:
      print("[FFMPEG ERROR] Stacking movie: %s was unsuccessfully!"% moviepath)
      Logger.debug("[FFMPEG ERROR] Stacking movie: %s was unsuccessfully!"% moviepath + str(e))
      raise
      movie_error_count += 1
		
  endTime = time.time()
  proc_time = str((round(endTime - startTime)))
  print("###############################################")
  print("## [%i] Movie(s) were stacked successfully!   ##"% movie_count)
  print("###############################################")
  print("## [%i] Movie(s) generated processing errors! ##"% movie_error_count)
  print("###############################################")
  Logger.info("##################################################################")
  Logger.info("## [%i] Movie(s) were stacked successfully. Runtime: %s seconds  ##"% (movie_count, proc_time))
  Logger.info("##################################################################")
  Logger.info("## [%i] Movie(s) generated processing errors!                    ##"% movie_error_count)
  Logger.info("##################################################################")
  
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
    if sys.platform == "win32":
      Logger = create_log(os.path.join(os.getcwd(), "logs\stackit.log"))
    else:
      Logger = create_log(os.path.join(os.getcwd(), "logs/stackit.log"))
    main(sys.argv[1:])
  except (KeyboardInterrupt, SystemExit) as e:
    if type(e) == SystemExit: sys.exit(int(str(e)))
