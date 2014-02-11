powerpoetry-twitter-demo
------------------------

This application polls twitter for recent tweets for a given search query, and ranks these
tweets based on how poetic they are. Follow the instructions below o build all the dependencies.

On Ubuntu, you must first install a fortran compiler with lapack.
```
$ sudo apt-get install gfortran liblapack-dev
```

To build the stack on MacOSX or Ubuntu, run the following command from the repo root.
```
$ ./waf configure clean build
```

Once the environment is built, you should have a python virtualenv in the "env" directory with
all required packages installed.

The poller needs a config file to run. Provide it one that looks something like this:

[Twitter]
consumer_key = <twitter-key>
consumer_secret = <twitter-secret>
access_token = <twitter-access-key>
access_token_secret = <twitter-access-secret>


[Poller]
processes = <# number of processes to spawn>
interval = <interval to fetch tweets at in seconds>
query = <query to search for, example: #basketball>
