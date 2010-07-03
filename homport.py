"""
Homport is a helper module to make manipulating nodes with HOM easier
"""

import hou

# TODO: add input cycling
# try to add input to 0 index, go up until there is an open input
# raise exception if no open inputs available
def connectInput(self, node):
  node.setInput(0, self)

def connectOutput(self, node):
  self.setInput(0, node)

# node >> node2 -- connects input of node2 to output of node
#hou.Node.__rshift__ = connectInput

# node << node2 -- connects input of node to output of node2
#hou.Node.__lshift__ = connectOutput

class ParmWrapper:
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

class NodeWrapper:
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
            childNode = NodeWrapper(childNode)

        parm = self.node.parm(name)
        parm = ParmWrapper(parm)
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
            node = NodeWrapper(object)
        except NodeWrapError:
            raise NodeWrapError
        else:
            node.setFirstInput(self.node)

    def __lshift__(self, object):
        """
        node << node2
        connect node's input to node2's output 
        """
        try:
            node = NodeWrapper(object)
        except NodeWrapError:
            raise NodeWrapError
        else:
            self.node.setFirstInput(node)

root = NodeWrapper(hou.node('/'))
obj = NodeWrapper(hou.node('/obj'))
