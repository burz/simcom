# Print out an error message when DIV by zero occurs
#
# %rdi := the line of the binary expression
#
error_div_by_zero_code = """__error_div_by_zero:
		pushq	%rbx
		movq	%rdi, %rbx
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_div_error, %rsi
		movq	$47, %rdx
		syscall
		movq	%rbx, %rdi
		call	__write_stderr
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_zero_end, %rsi
		movq	$20, %rdx
		syscall
		popq	%rbx
		movq	$60, %rax
		movq	$1, %rdi
		syscall"""

# Print out an error message when MOD by zero occurs
#
# %rdi := the line of the binary expression
#
error_mod_by_zero_code = """__error_mod_by_zero:
		pushq	%rbx
		movq	%rdi, %rbx
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_mod_error, %rsi
		movq	$47, %rdx
		syscall
		movq	%rbx, %rdi
		call	__write_stderr
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_zero_end, %rsi
		movq	$20, %rdx
		syscall
		popq	%rbx
		movq	$60, %rax
		movq	$1, %rdi
		syscall"""

# Print out an error message when an index is out of range
#
# %rdi := line of the binary expression
# %rsi := the value the expression evaluated to
#
error_bad_index_code = """__error_bad_index:
		pushq	%rbx
		movq	%rdi, %rbx
		pushq	%r12
		movq	%rsi, %r12
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_index_range, %rsi
		movq	$50, %rdx
		syscall
		movq	%rbx, %rdi
		call	__write_stderr
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_evaluated_to, %rsi
		movq	$14, %rdx
		syscall
		movq	%r12, %rdi
		call	__write_stderr
		movq	$1, %rax
		movq	$2, %rdi
		movb	$10, -1(%rsp)
		leaq	-1(%rsp), %rsi
		movq	$1, %rdx
		syscall
		popq	%r12
		popq	%rbx
		movq	$60, %rax
		movq	$1, %rdi
		syscall"""

# Write an integer to stdout
#
# %rdi := the integer to write
#
write_stdout_code = """__write_stdout:
		movq	$1, %rsi
		call	__write
		movq	$1, %rax
		movq	$1, %rdi
		movb	$10, -1(%rsp)
		leaq	-1(%rsp), %rsi
		movq	$1, %rdx
		syscall
		ret"""

# Write an integer to stderr
#
# %rdi := the integer to write
#
write_stderr_code = """__write_stderr:
		movq	$2, %rsi
		call	__write
		ret"""

# Write an integer to output
#
# %rdi := the integer to write
# %rsi := where to write to (1 : stdin, 2 : stderr)
#
write_code = """__write:
		pushq	%rbp
		movq	%rsp, %rbp
		pushq	%rbx
		movq	%rdi, %rbx
		pushq	%r13
		movq	%rsi, %r13
		pushq	%r12
		xorq	%r12, %r12
		cmpq	$0, %rbx
		jge		_conversion_loop
		movq	$1, %rax
		movq	%r13, %rdi
		movb	$45, -1(%rsp)
		leaq	-1(%rsp), %rsi
		movq	$1, %rdx
		syscall
		neg		%rbx
_conversion_loop:
		cmpq	$0, %rbx
		je		_write_characters
		movq	%rbx, %rax
		xorq	%rdx, %rdx
		movq	$10, %rcx
		idivq	%rcx
		addq	$48, %rdx
		pushq	%rdx
		incq	%r12
		movq	%rax, %rbx
		jmp		_conversion_loop
_write_characters:
		cmpq	$0, %r12
		jne		_write_loop
		movq	$1, %rax
		movq	%r13, %rdi
		movb	$48, -1(%rsp)
		leaq	-1(%rsp), %rsi
		movq	$1, %rdx
		syscall
		jmp		_write_end
_write_loop:
		movq	$1, %rax
		movq	%r13, %rdi
		popq	%rsi
		movb	%sil, -1(%rsp)
		leaq	-1(%rsp), %rsi
		movq	$1, %rdx
		syscall
		decq	%r12
		jnz		_write_loop
_write_end:
		popq	%r12
		popq	%r13
		popq	%rbx
		movq	%rbp, %rsp
		popq	%rbp
		ret"""

# Print out an error if the input is not an integer
#
error_bad_input_code = """__error_bad_input:
		movq	$1, %rax
		movq	$2, %rdi
		movq	$_bad_input, %rsi
		movq	$37, %rdx
		syscall
		movq	$60, %rax
		movq	$1, %rdi
		syscall"""

# Read in an integer
#
# Returns:
# %rax := the integer read in
#
read_code = """__read:
		pushq	%rbp
		movq	%rsp, %rbp
		subq	$20, %rsp
		xorq	%rax, %rax
		xorq	%rdi, %rdi
		movq	%rsp, %rsi
		movq	$20, %rdx
		syscall
_char_to_int:
		xorq	%rax, %rax
		xorq	%rcx, %rcx
		movq	%rsp, %rsi
		xorq	%rdx, %rdx
		movb	$45, %r8b
		cmpb	(%rsi), %r8b
		jne		_char_loop
		movq	$1, %rdx
		incq	%rsi
		incq	%rcx
_char_loop:
		xorq	%rdi, %rdi
		movb	(%rsi), %dil
		cmpq	$10, %rdi
		je		_finished_char_loop
		cmpq	$20, %rcx
		je		_finished_char_loop
		cmpq	$48, %rdi
		jl		__error_bad_input
		cmpq	$57, %rdi
		jg		__error_bad_input
		subq	$48, %rdi
		movq	$10, %r8
		imulq	%r8, %rax
		addq	%rdi, %rax
		incq	%rsi
		incq	%rcx
		jmp		_char_loop
_finished_char_loop:
		cmp		$1, %rdx
		jne		_finished_conversion
		negq	%rax
_finished_conversion:
		movq	%rbp, %rsp
		popq	%rbp
		ret"""

