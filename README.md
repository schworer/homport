# homport

Homport makes it easier to interact with [Houdini](http://sidefx.com) nodes in Python. Run it during interactive sessions to quickly wire up nodes, see the values of parameters, and more.

## Usage
### Connect nodes quickly:
```python
# connects output of 'node' to first input of 'node2'
node >> node2
# connects output of 'node' to the second input of 'node2'
node >> node2.input_two
```

### Deal with parameters more easily:
```python
# set parameters using assignment
node.tx = 500
# get values without calling eval()
print node.tx
```

### Link parameters together:
```python
# connect `ty` of nodeA to `tz` of nodeB
nodeA.ty >> nodeB.tz
```

## Documentation
Documentation is done using pycco -- check it out [here](http://schworer.github.com/homport/docs/homport.html)

## Installation
You can use [pip](http://pypi.python.org/pypi/pip) to install:

    pip install -e git+git://github.com/schworer/homport.git@0.2#egg=homport

If you don't want to use pip, clone the repo and add it to your path
manually:

    git clone git://github.com/schworer/homport homport/

Then, put this in your 123.py or 456.py Houdini startup script:

```python
import homport
homport.start()
```

or, import it directly in the Python pane within Houdini.

### Run the unit tests:

    hython test_homport.py

