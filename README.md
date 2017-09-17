How to use?
-----------
```
usage: mosaic.py [-h] [-o OUT] [-s SIZE] [-f] source_file segments_dir

positional arguments:
  source_file           source file for the mosaic
  segments_dir          directory containing raw segments (images may be any
                        size and format, but only images in the directory)

optional arguments:
  -h, --help            show  help message
  -o OUT, --out OUT     output file (by default out.png)
  -s SIZE, --size SIZE  size of mosaic segment (by default 32)
  -f, --frames          allow rendering frames of segments
```