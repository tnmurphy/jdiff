# jdiff - JSON diff

Generates a set of operations as output which convert one JSON component to another. It's still experimental at the moment and handles dictionaries better than lists.

## Example
```
  jdiff file0 file1 [file2....filen]
```

Generates diffs from file0 to file 1, then file0 to file2....etc

It's obviously also possible to do it programatically


## Usage
```
usage: jdiff [-h] [-l] [Files ...]

compare files containing JSON

positional arguments:
  Files       list of files to compare. Changes listed from the first file to each of the others

options:
  -h, --help  show this help message and exit
  -l          line mode - look for the first 2 complete json strings in the standard input and compare
              them

```
