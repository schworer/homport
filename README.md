# homport

Homport makes it easier to interact with [Houdini](http://sidefx.com) nodes in Python. Run it during interactive sessions to quickly wire up nodes, see the values of parameters, and more.

## Usage
### Connect nodes quickly:
    # connects output of 'node' to first input of 'node2'
    node >> node2
    # connects output of 'node' to the second input of 'node2'
    node >> node2.input_two

### Deal with parameters more easily:
    # set parameters using assignment
    node.tx = 500
    # get values without calling eval()
    print node.tx

## Installation Instructions:
You will be able to use pip to install it (when I get around to it):
    pip install git://github.com/schworer/homport homport/

If you don't want to use pip, clone the repo and add it to your path
manually:
    git clone git://github.com/schworer/homport homport/

Then, put this in your 123.py or 456.py Houdini startup script:
    import homport
    homport.bootstrap()
or, import it directly in the Python pane within Houdini.

### I like unit tests, run them like so:
    hython test_homport.py
