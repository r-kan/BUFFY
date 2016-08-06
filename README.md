# BUFFY? What is it?
BUFFY, stands for 'Back Up Files For You', is a pin tool to back up files  

# How BUFFY makes your life better
* Back up to local and remote spaces at one time  
* Very simple and straightforward to use, yet flexible  
* Easy monitoring backup status  

# How to use BUFFY?
First, let’s back up a single file **my_file.txt** to local disk **/my_backup/**  
```
    buffy -src my_file.txt -dst /my_backup/  
```

It is suggested to back up both locally and remotely, e.g., local disk and <a href='http://aws.amazon.com/s3'>aws s3</a>  
```
    buffy -src my_file_dir -dst /my_backup/ -dst s3://my_backup_bucket  
```

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

In example.json, we have 
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

# Future direction of BUFFY
Support more remote backup media  

# Contact  
Please contact <a href='http://r-kan.github.io'>*rkan*</a> by its_right@msn.com for any question/request/bug without hesitation. 
