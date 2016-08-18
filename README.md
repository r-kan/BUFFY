# BUFFY? What is it?
BUFFY, stands for 'Back Up Files For You', is a pin tool to back up files.  

# How BUFFY makes your life better
* Back up to local and remote spaces at one time  
* Very simple and straightforward to use, yet flexible  
* Easy monitoring backup status  
* Support all major platforms, e.g., Windows, linux, MacOS

# How to use BUFFY?
First, let’s back up a single file **my_file.txt** to local disk **/my_backup/**  
```
    buffy -src my_file.txt -dst /my_backup/  
```
Note: here, `buffy` stands for `python3 <BUFFY_HOME>/main.py`  

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

The 1st entry is original regular expression, such that **$dyn$** is a keyword, which will be replaced by the runtime evaluation of the 3rd entry. Before that, the 2nd entry will be 'imported' (leave it empty if 'import' is not needed). For instance, file named 'masterpiece_2013-06-14' will be backed up, on the date the highly praised work 'The Last of Us' on PS3 is released, which is 2013/06/14.  

Besides, also try `buffy -h` to find out other functionality!

# Future direction of BUFFY
Support more remote backup media  

# Contact  
Please contact <a href='http://r-kan.github.io'>*rkan*</a> by its_right@msn.com for any question/request/bug without hesitation. 
