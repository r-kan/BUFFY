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
First, let’s back up a single file to local disk  
        _buffy -src `my_file.txt` -dst `/my_backup/`_  

It is suggested to back up both locally and remotely, e.g., local disk and aws s3  
        _buffy -src `my_file_dir` -dst `/my_backup/` -dst `s3://my_backup_bucket`_  

It can be painful due to various aspects of expense, if we back up more than requirement.  
BUFFY provides a set of simple yet flexible functions to specify the backup target.  
For example, you can tell BUFFY to back up file    
.* with certain extension name  
.* matches with certain regular expression  
.* matches with certain ‘dynamic’ pattern  

Besides, form an ‘excluded’ file list is also possible  

# Future direction of BUFFY
Support more remote backup media  
