#!/usr/bin/env python
import os, sys
import subprocess
import time
import logging
import errno
import collections

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
    exts.append(".CD{0}.mkv".format(x))
    exts.append(".CD{0}.mp4".format(x))
  
  print("Please wait, searching for unstacked movies on library: %s..."% os.path.normpath(argv[0]).upper())
  Logger.info("Searching for unstacked movies on library: %s..."% os.path.normpath(argv[0]).upper())

  print "Searching movie files on root directory..."
  Logger.info("Searching files on root directory...")
  for f in os.listdir(argv[0]):
    if os.path.isfile(os.path.join(argv[0], f)):
      for ext in exts:
        uppername = f.upper()
        if uppername.find(ext.upper()) != -1:
          fname = os.path.join(argv[0], f)
          dirfiles.append(fname)
          Logger.debug("Added movie part file %s ... !", fname)
      filelist[argv[0]] = dirfiles
  dirfiles=[]
  
  for root, dirs, files in os.walk(argv[0]):
    for dir in dirs:    
      print ("Searching movie files on %s sub-directory..."% dir)
      for ext in exts:
        for name in os.listdir(os.path.join(root, dir)):
          uppername = name.upper()
          if uppername.find(ext.upper()) != -1:
            fname = os.path.join(root, dir, name)
            dirfiles.append(fname)
            filelist[os.path.join(root, dir)] = dirfiles
      dirfiles=[]

  return collections.OrderedDict(sorted(filelist.items(), key = lambda t: t[0]))
 
def remove_file(filepath):

   try:
     os.remove(os.path.realpath(filepath))
     Logger.info("Permanently removed file %s!"% filepath)
   except Exception as e:
     Logger.error("There was a problem removing file: %s!"% filepath)
     pass

def process(movies):

  movie_count = 0
  movie_error_count = 0
  startTime = time.time()
  
  for moviepath in movies.keys():
    movietxt = moviepath + '.txt'
    f = open(movietxt, 'w') 
    for moviepart in movies[moviepath]:
      moviefile = moviepart.replace("'", r"'\''")
      f.write('file ' + "'" + moviefile + "'" + '\n')
    f.flush()	  
    f.close()
    
    extension = os.path.splitext(moviepart)[1].lower()
    movie_output = moviepart.rsplit('.',2)[0] + extension
	
    try:
      print("Please wait, stacking movie: %s..."% moviepath)
      Logger.info("Stacking movie: %s"% moviepath)
      ffmpeg_command = ["bin\\ffmpeg.exe", "-f", "concat", "-i", movietxt, "-c", "copy", "-y", movie_output]
      Logger.info("Running FFMPEG with arguments: %s"% ffmpeg_command)
      #response = subprocess.check_output(ffmpeg_command, stderr=subprocess.STDOUT).decode("utf-8")
      ffmpeg = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      output, errors = ffmpeg.communicate()
      if ffmpeg.returncode == 0:	  
        print("Stacking movie: %s finished successfully!"% moviepath)
        Logger.info("Stacking movie: %s finished successfully!"% moviepath)
        time.sleep(2)
        Logger.info("Cleaning Up movie: %s by removing part files and temporary input file: %s!"% (moviepath, movietxt))
        for moviepart in movies[moviepath]:
          remove_file(moviepart)
          time.sleep(0.5)		  
        remove_file(movietxt)
        Logger.info("Finished cleaning up movie: %s successfully!"% moviepath)
        movie_count += 1		
      else:
        Logger.debug(output + '\n')
        Logger.error("Stacking movie: %s was unsuccessfully!"% moviepath)
        movie_error_count += 1
        pass
    except OSError:
      Logger.debug('OS Error: ' + str(errno) + '] :: [' + strerror + ']' + '\n')
      movie_error_count += 1
      pass
    except subprocess.CalledProcessError as e:
      Logger.debug("Stacking movie: %s was unsuccessfully!"% moviepath + str(e))
      movie_error_count += 1      
      pass
		
  endTime = time.time()
  proc_time = str((round(endTime - startTime)))
  print("#############################################")
  print(" [%i] Movie(s) were stacked successfully!   "% movie_count)
  print("#############################################")
  print(" [%i] Movie(s) generated processing errors! "% movie_error_count)
  print("#############################################")
  Logger.info("##############################################")
  Logger.info("				Runtime: %s seconds		         "% proc_time)
  Logger.info("##############################################")
  Logger.info(" [%i] Movie(s) were stacked successfully.     "% movie_count)
  Logger.info("##############################################")
  Logger.info(" [%i] Movie(s) generated processing errors!   "% movie_error_count)
  Logger.info("##############################################")
  
def main(argv):

  if (len(argv) == 0 or len(argv) >= 2):
    print("============================================================")
    print("== How to use stackit: stackit.py <movies_root_directory> ==")
    print("============================================================")
    sys.exit(1)
  
  movielist = getMovieFiles(argv)
  if not movielist:
    print("No movies on %s to process"% os.path.normpath(argv[0]).upper())
    Logger.info("No movies on %s to process"% os.path.normpath(argv[0]).upper())
  else:
    process(movielist)

if __name__ == "__main__":

  try:
    Logger = create_log(os.path.join(os.getcwd(), 'logs' + os.sep + 'stackit.log'))
    main(sys.argv[1:])
  except (KeyboardInterrupt, SystemExit) as e:
    if type(e) == SystemExit: sys.exit(int(str(e)))
