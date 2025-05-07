


Makefile is for quick commands while developing so i dont have to write it out all over again every time

## Basic flow: 

1. User sends POST request to /url endpoint 


2. Server hands off to celery worker queue
    - Job is queued for background processing, does not block subsequent api requests
    - Creates a placeholder DB row
    - returns a UUID that can be used to access the job result at a later time

3.  Celery 
    


## Development 

Makefile is for quick commands while developing so i dont have to write it out all over again every time