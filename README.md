On Ubuntu, you must first install a fortran compiler with lapack.
```
$ sudo apt-get install gfortran liblapack-dev
```

To build the stack, run the following command from the top level of the repo.
```
$ src/waf configure clean build
```
