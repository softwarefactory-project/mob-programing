# This files is a python program to demonstrate what can be done using lambdas
#
# The rules is that we only use lambda:
# - No builtin like `+`
# - No builtin types like `int` or `list`
# - No values likes `3` or `"hello"`
# - Basically, just lambda
#
#
# There are three elements in this system:
# - Variable:                       `x`
# - Abstraction:                    `lambda x: x`
#   -> This let you define a function
#   -> This can also be written as  `λx.x`
# - Application:                    `f(x)`
#   -> This let you call a function
#   -> This can also be written as  `f x`
#
# There are two types of variables:
# In `λx.x`      the right hand side x is bound
# In `λx.y`      the right hand side y is free
#
# Function that takes multiple parameter are defined like this:
#  -     `lambda x: lambda y: x`
#  - or: `λxy.x`
#
# The rules of application are:
#  - given a variable f bound to `lambda x: lambda y: x`
#  - the application `f(z)` becomes:       `lambda y: z`
#  - that is, all the variable in the abstraction are replaced by the application argument.
#
# Here are other examples:
#  - `(λf.f f)(a)`        -> (replace all the fs with `a`) -> `a a`
#  - `(λf.f (f f))(a)`    -> `a (a a)`
#  - `(λf.(f f) f)(a)`    -> `(a a) a`  which is equivalent to `a a a`, because application is left associative
#  - `(λxyx.x)(a)(b)(c)`  -> `c`        because the return value is bound to the last abstraction param
#  - `(λf.f)(λx.x)(a)`    -> (replace f with `λx.x`), which gives: `(λx.x)(a)` -> `a`
#  - `(λf.f f)(λa.a a)`   -> `(λa.a a)(λa.a a)`
#
# In this file, we enable global binding with `=`, like this:
IDENTITY = lambda x: x


# -------------------------------------------
# - Boolean logic                           -
# -------------------------------------------

# Using lambda abstraction, we can encode boolean value
TRUE  = lambda x: lambda y: x   #λxy.x
FALSE = lambda x: lambda y: y   #λxy.y

NOT   = lambda b: b(FALSE)(TRUE)
AND   = lambda b: lambda c: b(c)(b)
OR    = lambda b: lambda c: b(b)(c)

# 1: OR(FALSE)(TRUE)
# 2: (λb. λc. b(b)(c)) (λxy.y) (λxy.x)
# 3: (    λc.  (λxy.y)((λxy.y))(c))  (λxy.x)
# 4:           (λxy.y) (λxy.y) (λxy.x)
# 5:           (λ y.y)         (λxy.x)
# 6:                           (λxy.x)  -> TRUE



# -------------------------------------------
# - Natural algebra                         -
# -------------------------------------------

# Using lambda abstraction, we can encode number, called chruch numerals

ZERO  = lambda f: lambda x: (x)
ONE   = lambda f: lambda x: f(x)
TWO   = lambda f: lambda x: f(f(x))   # λfx.f(f x)
THREE = lambda f: lambda x: f(f(f(x)))
FOUR  = lambda f: lambda x: f(f(f(f(x))))

# You can think of `f` as a crank, and `x` as the starting value.

# And we can do arithmetics with simple application
INCR  = lambda x:   lambda f: lambda s: f(x(f)(s))
ADD   = lambda m: lambda n: m(INCR)(n)
MUL   = lambda m: lambda n: lambda f: m(n(f))
EXP   = lambda m: lambda n: n(m)


# 1: INCR(TWO)
# 2: (λx: λf: λs: f(  x                 (f) (s)  )) (λf: λx: f(f(x)))
# 3: (    λf: λs: f(  (λf: λx: f(f(x))) (f) (s)  ))
# 4: (    λf: λs: f(      (λx: f(f(x)))     (s) ))
# 4: (    λf: λs: f(           f(f(s)))      ))

# 1: EXP(TWO)(FOUR)
# 2: (λm: λn: n(m))          (λ f: λ x: f(f(x)))       (λ f: λ x: f(f(f(f(x)))))
# 3: (    λn: n((λ f: λ x: f(f(x)))) )                 (λ f: λ x: f(f(f(f(x)))))
# 4: (        (λ f: λ x:            f(      f(      f(     f(x)))))                ((λ f: λ x: f(f(x)))) # TWO )


# And build big numbers:
EIGHT = ADD(FOUR)(FOUR)
SIXTEEN = MUL(TWO)(EIGHT)


# -------------------------------------------
# - Pair encoding                           -
# -------------------------------------------

# Using lambda abstraction, we can encode pairs (or tuple)
CONS = lambda a: lambda b:   lambda selector: selector(a)(b)
CAR = lambda p: p(TRUE)
CDR = lambda p: p(FALSE)

# Demo
my_pair = CONS(ONE)(FOUR)
assert CDR(my_pair) == FOUR


# We can do substraction
T = lambda p: CONS(INCR(CAR(p)))(CAR(p))
DECR = lambda n:   CDR(  n(T)   (CONS(ZERO)(ZERO)))

SUB  = lambda n: lambda m: m(DECR)(n)



# -------------------------------------------
# - Control flow encoding                   -
# -------------------------------------------
LAZY_TRUE  = lambda x: lambda y: x(TRUE)
LAZY_FALSE = lambda x: lambda y: y(TRUE)
LAZY_ISZERO = lambda n: n(lambda b: LAZY_FALSE)(LAZY_TRUE)


def fact(n):
    if n == 0:
        return 1
    else:
        return n * fact(n - 1)

# -------------------------------------------
# - Recursion                               -
# -------------------------------------------

R = lambda rec: lambda n: LAZY_ISZERO(n) (lambda a: ONE) (lambda a: MUL(n)(  rec(DECR(n))))
Y = lambda f: (lambda x: f(lambda z: x(x)(z))) (lambda x: f(lambda z: x(x)(z)))

FACT = Y(R)



def show_church_numeral(c):
    # A little non lambda calculus function to simply see the numbers
    return c(lambda x: x + 1)(0)
