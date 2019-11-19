import docker
import os
import shutil
import uuid
import time
from docker.errors import *

# Start up docker client.
client = docker.DockerClient()

# Image uploaded to Docker; contains environment to run code for Java, Python, and C++.
IMAGE_NAME = 'dannyhp/coderpad'
# Code file created in temporary build directory.
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_BUILD_DIR = '%s/tmp' % CURRENT_DIR
# Timeout for docker.
TIMEOUT_SETTING = 'timeout -s 2 5'

SOURCE_FILE_NAMES = {
  "java" : "Solution.java",
  "python" : "solution.py",
  "c_cpp" : "solution.cpp"
}

BINARY_NAMES = {
  "java" : "Solution",
  "python" : "solution.py",
  "c_cpp" : "a.out"
}

BUILD_COMMANDS = {
  "java" : "javac",
  "python" : "python -u",
  "c_cpp" : "g++ -o a.out"
}

EXECUTE_COMMANDS = {
  "java" : "java",
  "python" : "python",
  "c_cpp" : "./"
}

# Run this command separately to load the image if not initially loaded onto system.
def load_image():
  try:
    client.images.get(IMAGE_NAME)
  except ImageNotFound:
    print('Image not found locally, loading from docker hub...')
    client.images.pull(IMAGE_NAME)
  except APIError:
    print('Image not found locally, docker hub is not accessible.')
    return
  print('Image: [%s] loaded.' % IMAGE_NAME)

# Builds docker container and runs the code.
def build_and_execute(code, language):
  result = {'build': None, 'run': None, 'error': None}

  source_file_parent_directory = uuid.uuid4()
  source_file_host_directory = '%s/%s' % (TEMP_BUILD_DIR, source_file_parent_directory)
  source_file_guest_directory = '/test/%s' % (source_file_parent_directory)

  make_dir(source_file_host_directory)

  with open('%s/%s' % (source_file_host_directory, SOURCE_FILE_NAMES[language]), 'w') as source_file:
    source_file.write(code)

  try:
    client.containers.run(
      image=IMAGE_NAME,
      command='%s %s' % (BUILD_COMMANDS[language], SOURCE_FILE_NAMES[language]),
      volumes={source_file_host_directory: {'bind': source_file_guest_directory, 'mode': 'rw'}},
      working_dir=source_file_guest_directory
    )
    print('Source built!')
    result['build'] = 'Compiled successfully!'
  except ContainerError as e:
    print('Build failed!')
    result['build'] = e.stderr
    shutil.rmtree(source_file_host_directory)
    return result
  
  try:
    temp_var = '%s %s %s' % (TIMEOUT_SETTING, EXECUTE_COMMANDS[language], BINARY_NAMES[language])
    print(temp_var)
    if EXECUTE_COMMANDS[language] == './':
      temp_var = '%s %s%s' % (TIMEOUT_SETTING, EXECUTE_COMMANDS[language], BINARY_NAMES[language])
    log = client.containers.run(
      image=IMAGE_NAME,
      command=temp_var,
      volumes={source_file_host_directory: {'bind': source_file_guest_directory, 'mode': 'rw'}},
      working_dir=source_file_guest_directory
    )
    print('Execution succeeded!')
    result['run'] = log
  except:
    print('Execution failed!')
    result['run'] = '[!] Execution Failed - Timeout'
    shutil.rmtree(source_file_host_directory)
    return result
  
  shutil.rmtree(source_file_host_directory)
  return result

def make_dir(directory):
  try:
    os.mkdir(directory)
    print('Temporary build directory [%s] created.' % directory)
  except OSError:
    print('Temporary build directory [%s] exists.' % directory)
