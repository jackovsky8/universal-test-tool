# Substitution

Data used for multiple test cases can be stored within the ````data``` Object.

If you want to access any of this data during a test step you can do this via substitution. This is done before any further action of the teststep is made.

## Substitution Brackets

Substitution is triggered anywhere there, where brackets are found ```{{ variable_name }}```.

### Options for the variable

Within the brackets you can access ***str***, ***int***, ***float***, ***list*** and ***dict*** elements from your ***data-Object***

#### Accessing Dicts

To navigate through dicts you can concatinate the keys with the ```.``` Operator. You can access the element bar of an object foo with ```{{ foo.bar }}```

#### Accessing Lists

To navigate through lists you can add the ```[x]``` Operator, where an index ***x*** whith ***x>=0*** represents the index of the element in the list and an index ***x*** whith ***x<0*** represents the index from the back of the list.

e.g.:
You can access the second element of a list with ```{{ foo.bar[1] }}``` or the last element of a list with ```{{ foo.bar[-1] }}```

#### Accessing Strs, Ints and Floats

All other elements are returned as they are.

### Type of the value

Since the accessed elements can be all the types ***str***, ***int***, ***float***, ***list*** and ***dict*** we want to control what type is substituted

#### Substituting within a string

If you substitute a variable within a string ```"This is a {{ foo }} String"```, then always the string representation of the element is inserted. So if foo is a ***dict***, then you will get ```"This is a {'bar': 1} String"```.

#### Standalone substituting

If you substitute a standalone variable (Note: It doesn't matter if it is surrounded by "") ```"{{ foo }}"```, then the type is the same as it was in the ***data-Object***.

### Pipes 

To force other types (Imaginable also for other function like rnd() which are not implemented yet) you can use pipes. ```"{{ foo | int }}"``` would convert the value into an integer if possible.

Available Pipes:
- int
- float
- str
- bool
- round:x - where x is the number of decimals

### Errors

We lay the responsibility of existing values and and correct typing to the Designer of the test case.

#### Not Found
If a Value is not found a KeyError is raised. 

#### Index out of Range
If a List element is not existing an IndexError is raised.

#### Pipe not existing
If a none existing pipe is called a KeyError is raised

#### Wrong number of arguments for pipe
If a pipe recieves a wrong number of arguments a TypeError is raised

#### Wrong type into pipe
If a pipe can't handle a value a ValueError is raised.

