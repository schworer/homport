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
    You can use pip to install it:
    pip install git://github.com/schworer/homport homport/

    If you don't want to use pip, clone the repo and add it to your path
    manually:
    git clone git://github.com/schworer/homport homport/

    Then, put this in your 123.py or 456.py Houdini startup script:
        import homport
        homport.bootstrap()
"""

if not 'hou' in globals():
    # import houdini in this module. Ideally, hou should already be in
    # globals, as homport is meant to be run inside a houdini session.
    import hou

def __wrap_node(*args, **kwargs):
    """
    This function is used to monkey patch the hou.node method in order to
    make the Homport module transparent to users. Once monkey patched,
    hou.node will return a NodeWrap object.
    """
    import pdb; pdb.set_trace()
    node = hou.__node(*args, **kwargs)
    return NodeWrap(node)

def bootstrap():
    """
    Bootstrap the current session.
    @warning: This monkey patches the hou.node method.
    """

    # stash the originial function away, we'll call it later
    hou.__node = hou.node

    __wrap_node.func_name = 'node'
    __wrap_node.func_doc = hou.node.func_doc
    hou.node = __wrap_node

class ParmWrap(object):
    """
    TODO document
    """
    def __init__(self, parm):
        """
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

class NodeWrap(object):
    """
    TODO document
    """
    def __init__(self, node):
        """
        TODO document
        """
        self.node = node

    def __getattr__(self, name):
        """
        TODO document
        """
        childNode = self.node.node(name)
        if not childNode:
            childNode = NodeWrap(childNode)

        parm = self.node.parm(name)
        parm = ParmWrap(parm)
        try:
            attribute = getattr(self.node, name)
        except AttributeError:
            attribute = None

        attribs = [x for x in (childNode, parm, attribute) if x]
        if len(attribs) == 0:
            msg = "Node object has no Node, parm or Attribute: %s" % name
            raise AttributeError(msg)

        if len(attribs) > 1:
            msg = "%s is an ambiguous name, it could be one of %s" \
                % (name, attribs)
            raise AttributeError(msg)

        return attribs[0]

    def __rshift__(self, object):
        """
        node >> node2
        connect node's output to node2's input 
        """
        try:
            node = NodeWrap(object)
        except NodeWrapError, e:
            raise NodeWrapError
        else:
            node.setFirstInput(self.node)

    def __lshift__(self, object):
        """
        node << node2
        connect node's input to node2's output 
        """
        try:
            node = NodeWrap(object)
        except NodeWrapError, e:
            raise e
        else:
            self.node.setFirstInput(node)

    def __repr__(self):
        """ """
        return "<Node %s of type %s>" % (self.node.path(),
                                         self.node.type().name())

    def __str__(self):
        """ calls through to the HOM Node's str function """
        return str(self.node)

