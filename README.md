simcom - A compiler and interpreter for the SIMPLE language
==============================================

Author: Anthony Burzillo

A product of [Peter Fröhlich's](http://gaming.jhu.edu/~phf/) Spring 2013
[Compilers and Interpreters class](http://gaming.jhu.edu/~phf/2013/spring/cs328/) at Johns Hopkins.

******

## Language

In our implementation, the SIMPLE language is a statically typed imperative language with a single basic data type
INTEGER as well as two constructive data types ARRAY and RECORD.

Please see the grammar for the language in doc/SIMPLE_grammar.txt, the example programs in examples/, or the class
website for more information about the SIMPLE language.

## Executables

Consider the bin program in examples/bin.sim which writes the result of two expressions to the screen:

```SIMPLE
PROGRAM bin;
  CONST a = 5;
        b = 7;
  VAR x : INTEGER;
BEGIN
  WRITE a * x;
  x := 10; 
  WRITE (a * x) MOD b
END bin.
```

### sc - the SIMPLE compiler

Print out all the tokens in a program:


```shell
$ ./sc -s examples/bin.sim
PROGRAM@1
identifier<bin>@1
;@1
CONST@2
identifier<a>@2
=@2
integer<5>@2
;@2
identifier<b>@3
=@3
integer<7>@3
;@3
VAR@4
...
END@9
identifier<bin>@9
.@9
```

Create a graphical representation of the symbol table (with [dot] installed):

[dot]: http://www.graphviz.org/

```shell
$ ./sc -t examples/bin.sim | dot -T jpeg > table.jpg
```

![symbol table](http://i.imgur.com/x9i89hg.jpg)

Create a graphical representation of the syntax tree (with [dot] installed):

```shell
$ ./sc -a examples/bin.sim | dot -T jpeg > tree.jpg
```

![syntax tree](http://i.imgur.com/IQ3oZkV.jpg)

Run the program in with the interpreter:

```shell
$ ./sc -i examples/bin.sim
0
1
```

### test

This program runs all of the executables in examples/ and reports on any that fail to run.
test can be given any option and that option will be run on each executable.

Run the testing suite:

```shell
$ ./test
$$  Test 'args' was successful.
$$  Test 'arrassi' was successful.
$$  Test 'read_in' was successful.
...
$$  Test 't2' was successful.
+++++++++++++++++++++++++++++++++++++++++++
27 tests were run with 27 succesful, 0 failed.
```

## License

The MIT License (MIT)

Copyright (c) 2013 Anthony Burzillo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

