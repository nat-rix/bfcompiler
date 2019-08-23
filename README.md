# bfcompiler
A little brainfuck compiler I found from the past (a [long long](https://en.wikipedia.org/wiki/C_data_types#Basic_types) time ago).

## Usage

Usage: `./compiler.py [FILE]`

This program breaks if something is not as it is supposed.
There are no compiler errors... bullshit in, bullshit out.

## Syntax

Every program begins with the declaration of all variables. You put them into parantheses `()`.
i.e.
```
(a, b, c, d)
…
```

Commands:
* `set <var> <num>` - initialise a variable with a given number
* `setchar <var> "<char>"` - initialise a variable with a given character
* `mov <var> <var>` - Move a value from one variable to another, resetting the first variable to zero
* `cpy <var> <var>` - Copy the value from one variable to another
* `add <var> <var>` - Add the first variable to the second ("add a b" <=> "b = a + b")
* `raw <bf-code>` - Insert raw brainfuck code
* `print_raw <var>` - Print the ASCII-value of a variable
* `print_text "<string>"` - Print text (`\n` is a line break)
* `print_num_1 <var>` - Print the variable as a one digit decimal number
* `print_num <var>` - Print the variable as a decimal number
* `if <var>` - Execute code until `endif`, if the variable is not zero
* `if_clr <var>` - Execute code until `endif`, if the variable is not zero and then set the variable to zero
* `if= <var> <var>` - Execute code until `endif`, if the variables are equal
* `while <var>` - Execute code until `endwhile` until the variable is zero
* `endif` - see `if`
* `endwhile` - see `if`
* `incr <var>` - Increment variable
* `decr <var>` - Decrement variable
* `getchr <var>` - Read a character from input into `var` (exactly identically to `,` in brainfuck)
* `chr_to_int <var>` - Subtract 48 from variable, to convert an ASCII-number to an integer
* `div <var> <var>` - Divides "first / second" writing the result into "first"
* `mod <var> <var>` - Modulo. warning: I am too lazy to test this
* `mult <var> <var>` - Multiplicates "first * second" writing the result into "first"

## Hello World!

You can see examples under `examples/`

```
()

print_text "Hello World!\n"
```
