# BUFFY? What is it?
BUFFY, stands for 'Back Up Files For You', is a command line tool to back up files.  

# How BUFFY makes your life better
* Back up to local and remote spaces at one time  
* Very simple and straightforward to use, yet flexible  
* Easy monitoring backup status  
* Support all major platforms with python3.x, e.g., Windows, linux, Mac OS

# How to use BUFFY?
First, let’s back up a single file **my_file.txt** to local disk **/my_backup/**  
```
    buffy -src my_file.txt -dst /my_backup/  
```
Note: from now, `buffy` stands for `python3 <BUFFY_HOME>/main.py`  

It is suggested to back up both locally and remotely, e.g., local disk and <a href='http://aws.amazon.com/s3'>Amazon S3</a>  
```
    buffy -src my_file_dir -dst /my_backup/ -dst s3://my_backup_bucket  
```
Note: to back up to s3, <a href='https://aws.amazon.com/cli'>awscli</a> must be installed  

It could be bad due to various aspects of expense, if we back up beyond requirement.  
BUFFY provides a set of simple yet flexible functions to specify the backup target.  
For example, you can tell BUFFY to back up file:    
* with certain extension name  
* matches with certain regular expression  
* matches with certain ‘dynamic pattern'  

Besides, form an excluded file list for backup is also possible.  

This is accomplished by giving a json configuration file to BUFFY.  
```
    buffy -c example.json  
```

In <a href='https://github.com/r-kan/BUFFY/blob/master/example.json'>example.json</a>, we have 
```
    "src":
    {
        "root": "/my_file_dir",             <== the base directory of backup source
        "file": ["password.txt", "email/"], <== file, or directory can be specified
        "ext": ["jpg", "png"],              <== back up the pictures
        "re": [".*/credential.+"],          <== back up file basename ends with 'credential'
        "exclude":
        {
            "re": ".*.DS_Store$"            <== not back up the Mac OS system file '.DS_Store'
        }
    },
```

We haven't talked about the usage of 'dynamic pattern', right? It is the most powerful though fallable function. So one must use it with caution. Basically, it performs runtime evaluation to decide regular expressions. For example,

```
    "src":
    {
        ...
        "dyn": ["masterpiece_$dyn$", "datetime", "str(datetime.date.today())"],
        ...
    },
```

Take a look at the value of 'dyn': the 1st entry is original regular expression, such that **$dyn$** is a keyword, which will be replaced by the runtime evaluation outcome of the 3rd entry. Before that, the 2nd entry will be 'imported' (leave it empty if 'import' is not needed). For instance, file named 'masterpiece_2013-06-14' will be backed up, on the date the highly praised work 'The Last of Us' on PS3 is released, which is 2013/06/14.  

# Command line usage
```
usage: buffy [-h] [-src SRC] [-dst DST] [-n NAME] [-e] [-cmp] [-r RPT] [-v]
               [-s] [-d] [-c CONFIG_FILE]

BUFFY --- Back Up Files For You

optional arguments:
  -h, --help            show this help message and exit
  -src SRC              backup source
  -dst DST              backup destination
  -n NAME, --name NAME  backup name
  -e, --encoding        name encoding with date (default: False)
  -cmp, --compress      compress backup files (default: False)
  -r RPT, --report RPT  report path
  -v, --verbose         verbose mode
  -s, --silent          silent mode
  -d, --dry_run         perform a dry run
  -c CONFIG_FILE, --config CONFIG_FILE
                        config file (this option overwrites others)
```

# Future direction of BUFFY
Support more remote backup media, e.g., dropbox  
Provide incrmental backup optionally  

# Contact  
Please contact <a href='http://r-kan.github.io'>*Rodney Kan*</a> by its_right@msn.com for any question/request/bug without hesitation. 
