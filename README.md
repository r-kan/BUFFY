# BUFFY
_~Back Up Files For You~_

# BUFFY? What is it?
A pin tool to back up files  
Created by python  

# How BUFFY makes your life better
* Back up to local and remote space at one time  
* Very simple and straightforward to use  
* Easy monitoring backup status  

# How to use BUFFY?
First, let’s back up a single file to a local disk  
  _buffy -src `my_file.txt` -dst `/my_backup/`_  

It is suggested to back up both locally and remotely, e.g., local disk and aws s3  
  _buffy -src `my_file_dir` -dst `/my_backup/` -dst `s3://my_backup_bucket`_  

It can be painful by various aspects of expense if we back up more than actually required.  
BUFFY resolves the problem by providing a set of custom specifications to restrict the target backup files.  
For example, we can back up file  
* within certain file extension name  
* matches with certain regular expression  
* matches with certain ‘dynamic’ pattern  

The above specification can also be used to construct a ‘excluded’ file list  

# Future direction of BUFFY
Support more remote backup media  
