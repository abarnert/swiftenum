# swiftenum
Swift-style enums with associated values for Python

Swift uses `enum` types with associated values to sneak alegbraic data types into the language in a way that won't scare off people from a Java-ish (or Objective C) background.

API
===

This is a quick&dirty hack to provide enums with associated values, [as in Swift][swift], on top of Python's stdlib [enums][enum]. For example:

    class Barcode(SwiftEnum):
        upca = (int, int, int, int)
        qrcode = (str,)
        handwritten = (str,)

    barcode1 = Barcode.upca(8, 85909, 51226, 3)
    barcode2 = Barcode.qrcode('ABCDEFGHIJKLMNOP')
    barcode3 = Barcode.handwritten('ABCDEFGHIJKLMNOP')

Or, for everyone's favorite:

    class Maybe(SwiftEnum):
        just = (object,)
        nothing = ()

    something = Maybe.just(2)
    nothing = Maybe.nothing()

As with a normal `enum.Enum`, or a Swift `enum`, the `type` of `barcode1` is `Barcode`. However, note that `Barcode.upca` itself is _not_ a `Barcode`, it's a function that takes 4 arguments and _returns_ a `Barcode`. (Also, of course, `Maybe.nothing` is not a `Maybe`, it's a function that takes no arguments and returns a `Maybe`.) Just as with normal function calls in Python, enum constructor calls check the number of arguments, but not the types, which are only there for documentation (although a static type checker, like some future version of `mypy`, could easily do something useful with them).

Note that to write recursive enums, you don't need Swift's `indirect`--but you do need to put the type in quotes (much as with [PEP 484][484] type hints). So, this Swift example:

    enum ArithmeticExpression {
        case Number(Int)
        indirect case Addition(ArithmeticExpression, ArithmeticExpression)
        indirect case Multiplication(ArithmeticExpression, ArithmeticExpression)
    }

... becomes:

    class ArithmeticExpression(SwiftEnum):
        number = (int,)
        addition = ('ArithmeticExpression', 'ArithmeticExpression')
        multiplication = ('ArithmeticExpression', 'ArithmeticExpression')

But you can still use it the same way:

    expr = ArithmeticExpression.addition(
        ArithmeticExpression.number(2), ArithmeticExpression.number(3))

As with all Python `Enum`s, the values have a `value` attribute, equivalent to Swift's `rawvalue`. These are auto-numbered from 1, as with the `AutoNumber` type defined in the docs, so `barcode2.value`, or the `value` of any other `qrcode` or any `addition`, is 2. (And yes, this means you could write `Barcode(2)('ABCDEFGHIJKLMNOP')` and it will work.) Just as in Swift, you're rarely if ever going to care about the raw values when you have associated values.

Just as `IntEnum` values work like `int`s, `SwiftEnum` values work like `tuple`s--but like `tuple`s of their _associated_ values, not their raw value. This is not _quite_ the same as in Swift, because the associate values don't just deconstruct like tuples, they actually match an is-a test (`isinstance(barcode2, tuple) == True`).

Also like all `Enum`s, `SwiftEnum` values have a `name` attribute. In fact, because Python doesn't have pattern matching, this is the one obvious way to switch on different values. So, this example from the Swift docs:

    switch productBarcode {
    case .UPCA(let numberSystem, let manufacturer, let product, let check):
        print("UPC-A: \(numberSystem), \(manufacturer), \(product), \(check).")
    case .QRCode(let productCode):
        print("QR code: \(productCode).")
    }
    
... looks like this in Python:

    if product_barcode.name == 'upca':
        number_system, manufacturer, product, check = product_barcode
        print(f"UPC-A: {numberSystem}, {manufacturer}, {product}, {check}.")
    elif product_barcode.name == 'qrcode':
        product_code, = product_barcode
        print(f"QR code: {product_code).")

Of course `switch` statements have to exhaustively enumerate all the cases or Swift will complain (unless you add a `default` case that does something), while `elif` chains don't care about exhaustive enumeration (unless you add an `else` that raises), and you have to use tuple deconstruction instead of having it be embedded in the case deconstruction, but otherwise, they're pretty much the same.

Equality and hashing work as you'd expect: a barcode only equals another barcode with the same value and equal associated values (so `barcode2 != barcode3`, and `barcode2 != Barcode.qrcode('AAAAAAAAAAAAAAAA')`). I'm not sure about pickling and deep copying. The `repr` and `str` both look like the constructor syntax--in particular, they don't show the raw value.

Polymorphism
============

You may have noticed that I defined `Maybe.just` as taking type `object`. But Swift's `Optional` is a _generic_ `enum`, more like this:

    enum Maybe<T> {
        case Just(T)
        case Nothing
    }

It would be very easy to extend `SwiftEnum` to allow this:

    class Maybe(SwiftEnum[T]):
        just = (T,)
        nothing = ()

You could do this by extending `enum.EnumMeta` with a sub(meta)class that adds `def __getitem__(self, args): return self`. That's all it takes, because, again, the value constructors ignore the actual types they're given.

But if you instead create a metaclass that inherits `typing.GenericMeta` as well as `enum.EnumMeta`, then a `SwiftEnum` subclass will work exactly like a `typing.Generic` subclass. At runtime, that still means nothing (`Maybe[T]` is still the same type as `Maybe`, just as `Mapping[K, T]` is the same type as `Mapping`). And it probably wouldn't do much good even in a current static type-checker like `mypy`, which won't even recognize that `Maybe[int].just` is a callable in the first place, much less that it's a constructor for `Maybe[int]` from one `int`. But if you're going to extend such a type checker to understand `SwiftEnum`, you'd almost certainly want to include generics support.

ADT
===

So, how is this an ADT? `SwiftEnum` builds sum types (and, obviously, they're closed). To build product types, we've already got `tuple`. Or, equivalently, the 0 or more associated values are a product of 0 or more types. Or, if you want names, use a `struct` (or, in Python, a `namedtuple`). (In fact, Swift allows you to name the members of the associated value directly. This works the same as providing keyword names for parameters in function definitions, forcing the caller to pass the arguments by keyword. But that isn't essential, and it's more closely tied to Swift's slightly weird function definition and calling syntax than to its `enum` feature, so I left it out.) The only thing missing is recursion, and `indirect` handles that.

So, a Swift `enum` can do everything a Haskell `data` does. And a `SwiftEnum` in Python--well, it does the same things, but (almost) all at runtime. Sso you can argue about whether it's actually the same or not by just having the usual dynamic vs. static typing argument, instead of needing to think about a new argument to have.

The reason `enum` doesn't just look like `data` is that--like Scala case classes (and probably like whatever C# 7 ends up adding)--it looks friendly to people coming from ObjC or Java. They already know `enum` without associated values. With associated values--well, that's just an ObjC convenience initializer or Java alternate-constructor static method, isn't it? Polymorphic ADTs look, and act, like generic interfaces or classes in ObjC and Java (and C++ and C#). You won't even think about doing recursive types until the first time you actually need them, at which point the idea won't look scary (and you'll be able to find `indirect` in the docs pretty quickly).

The Point
=========

So, what's the point of porting this feature to Python? On its own? None that I can think of. People ask for ADTs in Python, but ADTs by themselves don't do anything.

The point is to experiment with adding other features that work with ADTs: pattern matching, static type checking and inference, dynamic type checking and JIT optimizing, static and dynamic overloading, typing for wire protocols and file formats (think `ctypes.Union`), etc.

For one thing, you can simulate pattern matching just for ADTs by twisting the syntax in a few different ways. For example:

    barcode.upca.match(product_barcode, lambda number_system, manufacturer, product, check:
        print(f"UPC-A: {number_system}, {manufacturer}, {product}, {check}"))
    barcode.qrcode.match(product_barcode, lambda product_code: 
        print(f"QT code: product_code"))

You could even hack in an exhaustiveness check: `with product_barcode.switch:` sets a flag to 1, any `match` that succeeds decrements it, and when the `with` exits, if it's still 1, or negative, your code is broken.

For another example: PEP 484/mypy is supposed to be flexible enough to cover anything important, without having to interpret the full range of stuff you can do at runtime in Python, by special-casing specific decorators, metaclasses, etc. So, can you extend it to handle type-checking constructor calls to arbitrary types built algebraically out of `SwiftEnum`? If so, that pretty much proves that the design flexible enough.

Alternatives
============

It might have been cleaner to not use `enum.Enum` at all here. It would take more code, but we could, e.g., make `Barcode.upca` look more like an alternate constructor classmethod named `Barcode.upca` than like a closure named `<function __main__.SwiftEnum.__new__.<locals>.func>`, and probably provide better error messages when you do things that make no sense, and so on.

The syntax of specifying a tuple of argument types is a little weird--it looks much less like a function declaration than the Swift equivalent, and of course it's clumsy for a single argument. We could actually make it look like a function call. (Remember that we're supplying a metaclass with a custom dict. There's no reason that dict's `__getitem__` couldn't generate each new item as encountered--there are enum modules on PyPI that do this--and then return something whose `__call__` finishes setting up the enum value. This would be hacky, but it would work. Or, of course, we could just use MacroPy and process the AST.) And then the types could become annotations, and we could give the parameters names. In fact, then we _have_ to give them names, and I'm not sure we'd _want_ to. (Most familiar ADT examples use unnamed parameters and arguments in the constructors. After all, what's the name of the thing in `Just(2)`, or of each argument in `Add(Num(2), Num(3))`? In many languages, if you want named arguments, you use a `struct`-like product type instead of a plain `tuple`/separate arguments. In Swift, you can optionally name the arguments, but that works like adding keywords to function parameters: the arguments then have to be passed by keyword in calls.)

Should an enum value really be a tuple of its associated values? It pretty much has to be a sequence of some kind. After all, without some kind of pattern-matching syntax in Python, the only way to extract the associated values is with iterable unpacking or indexing. Of course if you added pattern-matching, you could easily make `enum` values be decomposable but _not_ iterable or indexable (whether because the matching API directly understands `enum` values, or because there's a deconstruction protocol). Would that be an improvement?


  [swift]: https://developer.apple.com/library/ios/documentation/Swift/Conceptual/Swift_Programming_Language/Enumerations.html
  [enum]: https://docs.python.org/3/library/enum.html
  [484]: https://www.python.org/dev/peps/pep-0484/
