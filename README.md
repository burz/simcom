simcom - A compiler and interpreter for the SIMPLE language
==============================================

Author: Anthony Burzillo

A product of [Peter Fröhlich's](http://gaming.jhu.edu/~phf/) Spring 2013
[Compilers and Interpreters class](http://gaming.jhu.edu/~phf/2013/spring/cs328/) at Johns Hopkins.

******

## Language

In our implementation, the SIMPLE language is a statically typed, imperative language with a single basic data type
INTEGER as well as two constructive data types ARRAY and RECORD.

Check out the [the grammar](doc/SIMPLE_grammar.txt) for the language, some of the [tests](tests/), or the class
website for more information about the SIMPLE language.

## Executables

Consider the iffy program in tests/iffy.sim which writes 0 to the screen:

```SIMPLE
PROGRAM iffy;
  VAR x, y, z : INTEGER;
BEGIN
  x := 6;
  IF x MOD 200 >= 56 THEN
    WRITE 1
  ELSE
    WRITE 0
  END 
END iffy.
```

### sc - the SIMPLE compiler

Print out all the tokens in a program:


```shell
$ ./sc -s tests/iffy.sim
PROGRAM@1
identifier<iffy>@1
;@1
VAR@2
identifier<x>@2
,@2
identifier<y>@2
,@2
identifier<z>@2
:@2
identifier<INTEGER>@2
...
WRITE@8
integer<0>@8
END@9
END@10
identifier<iffy>@10
.@10
```

Create a graphical representation of the symbol table (with [dot] installed):

[dot]: http://www.graphviz.org/

```shell
$ ./sc -t tests/iffy.sim | dot -T jpeg > table.jpg
```

![symbol table](http://i.imgur.com/fdKonuB.jpg)

Create a graphical representation of the syntax tree (with [dot] installed):

```shell
$ ./sc -a tests/iffy.sim | dot -T jpeg > tree.jpg
```

![syntax tree](http://i.imgur.com/CjbqH7i.jpg)

Run the program in with the interpreter:

```shell
$ ./sc -i tests/iffy.sim
0
```

Create lazy AMD64 assembly code and run:

```shell
$ ./sc -l tests/iffy.sim > iffy.s
$ gcc -o iffy iffy.s
$ ./iffy
0
```

Create intermediate code:

```shell
$ ./sc -m tests/iffy.sim
Binary(mov): $6 -> !0
Assign: !0 -> x
Binary(mov): $200 -> !1
Division: x / !1
Binary(mov): $56 -> !2
Compare: >%rdx !2
Conditional Jump: >= goto Label: 4540158288
Binary(mov): $1 -> !3
Write: !3
Unconditional Jump: goto Label: 4540158416
Label: 4540158288
Binary(mov): $0 -> !4
Write: !4
Label: 4540158416
```

Create the flow graph block representation of the program (with [dot] installed):

```shell
$ ./sc -f tests/iffy.sim | dot -T jpeg > flow_graph.jpg
```

![flow_graph](http://i.imgur.com/2WgWn4d.jpg)

### test

This program runs all of the executables in tests/ and reports on any that fail to run.
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

