"""
Homport is a helper module to make manipulating nodes with HOM easier in
an interactive Python session

Connect nodes quickly:
node >> node2 -- connects output of 'node' to first input of 'node2'
node >> node2.input_two -- connects output of 'node' to the second input of
                           'node2'

Deal with parameters more easily:
print node.tx does the same as:
print node.parm('tx').eval()

Installation Instructions:
    You will be able to use pip to install it (when I get around to it):
    pip install git://github.com/schworer/homport homport/

    If you don't want to use pip, clone the repo and add it to your path
    manually:
    git clone git://github.com/schworer/homport homport/

    Then, put this in your 123.py or 456.py Houdini startup script:
        import homport
        homport.bootstrap()
    or, import it directly in the Python pane within Houdini.
"""

if not 'hou' in globals():
    # import houdini in this module. Ideally, hou should already be in
    # globals, as homport is meant to be run inside a houdini session.
    import hou

def bootstrap():
    """
    Bootstrap the current session.
    @warning: This monkey patches the hou.node method.
    """

    # move the original function out of the way, we'll call it later
    hou.__node = hou.node

    def _wrap_node(*args, **kwargs):
        """
        This function is used to monkey patch the hou.node method in order to
        make the Homport module transparent to users. Once monkey patched,
        hou.node will return a NodeWrap object.
        """
        node = hou.__node(*args, **kwargs)
        return NodeWrap(node)

    _wrap_node.func_name = 'node'
    _wrap_node.func_doc = hou.node.func_doc
    hou.node = _wrap_node

class NodeWrapError(Exception):
    pass

class ParmWrap(object):
    """
    TODO document
    """
    def __init__(self, parm):
        """
        TODO document
        """
        self.parm = parm

    def __rshift__(self, object):
        """
        node.tx >> node2.ty
        """
        pass

    def __lshift__(self, object):
        """
        node.ty << node2.tx
        """
        pass

    def __getattr__(self, name):
        """
        TODO document
        """

        if name in dir(self.parm):
            return getattr(self.parm, name)
        else:
            msg = 'ParmWrap object has no attribute %s' % name
            raise AttributeError(msg)

    def __str__(self):
        return str(self.parm.eval())

class NodeWrap(object):
    """
    TODO document
    """
    def __init__(self, node):
        """
        TODO document
        """
        if not node:
            raise NodeWrapError('Invalid node given.')

        self.node = node
        self.input_index = 0

    def createNode(self, name):
        """
        Wraps the node created by hou.Node.createNode in a NodeWrap obj
        """
        node = self.node.createNode(name)
        return NodeWrap(node)

    def __getattr__(self, name):
        """
        Easily get the children or parameters of the node without calling
        extra methods on the node. A useful convenience function.

        examples:
            node = hou.node('/obj')
            node.geo1 # will return hou.node('/obj/geo1')
            node.tx # will return node.parm('tx')
            node.createNode # will return node.createNode
        """

        inputs = ('input_one', 'input_two', 'input_three', 'input_four')
        if name in inputs:
            self.input_index = inputs.index(name)
            return self

        # if the attr we're looking for is a method on the hou.Node object
        # return that first without going further.
        # This might cause problems later, we'll see.
        if name in dir(self.node):
            return getattr(self.node, name)

        childNode = self.node.node(name)
        if childNode:
            childNode = NodeWrap(childNode)

        parm = self.node.parm(name)
        if parm:
            parm = ParmWrap(parm)

        try:
            attribute = getattr(self.node, name)
        except AttributeError:
            attribute = None

        attribs = [x for x in (childNode, parm, attribute) if x]
        if len(attribs) == 0:
            msg = "Node object has no Node, parm or python attr called %s" \
                % name
            raise AttributeError(msg)

        if len(attribs) > 1:
            msg = "%s is an ambiguous name, it could be one of %s" \
                % (name, attribs)
            raise AttributeError(msg)

        return attribs[0]

    def __setattr__(self, name, value):
        """
        This implementation of setattr enables setting of parameters using the
        = (equals) operator. Usually, you'd set a parm value like this:
            node.parm('tx').set(50)
        With this implementation, we can do this:
            node.tx = 50

        @warning: this only works when the attr in question is a ParmWrap 
        object on a NodeWrap object and not a standalone hou.Parm or 
        ParmWrap object.

        For example, it should be obvious that this won't work:
            my_tx = node.tx
            my_tx = 50
        Or this:
            tx = node.parm('tx')
            tx = 50
        """
        if name in ('node', 'input_index'):
            object.__setattr__(self, name, value)
        else:
            attr = self.__getattr__(name)
            if isinstance(attr, ParmWrap):
                attr.parm.set(value)
            else:
                object.__setattr__(self, attr, value)

    def __rshift__(self, object):
        """
        node >> node2
        connect node's output to node2's input 
        """
        if isinstance(object, NodeWrap):
            node = object
        else:
            try:
                node = NodeWrap(object)
            except NodeWrapError, e:
                raise NodeWrapError
        node.setInput(node.input_index, self.node)

    def __lshift__(self, object):
        """
        node << node2
        connect node's input to node2's output 
        """
        if isinstance(object, NodeWrap):
            node = object
        else:
            try:
                node = NodeWrap(object)
            except NodeWrapError, e:
                raise NodeWrapError
        self.node.setInput(self.input_index, node.node)

    def __floordiv__(self, object):
        """
        Disconnect two nodes:
        node = hou.node('/obj/geo1')
        node2 = hou.node('/obj/geo2')
        node >> node2 # connect them
        node // node2 # disconnect them
        """
        # check object's input connections
        node = object
        conn = node.inputConnections()[node.input_index]
        if not conn.inputNode() == self.node:
            raise NodeWrapError('Input node is incorrect')
        else:
            node.setInput(node.input_index, None)

    def __repr__(self):
        """ """
        return "<Node %s of type %s>" % (self.node.path(),
                                         self.node.type().name())

    def __str__(self):
        """ calls through to the HOM Node's str function """
        return str(self.node)

