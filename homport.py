"""
Homport is a helper module to make manipulating nodes with HOM easier in an
interactive Python session.
"""

def start():
    """
    ### Launch Homport

    Bootstraps the current session. `homport.start()` must be called before
    running any homport-specific functions. You may want to `import homport`
    and run this method in a [startup script.][1]

    __Warning:__ This monkey patches the `hou.node` method.

    [1]: http://www.sidefx.com/docs/houdini11.0/hom/independent
    """

    # Import Houdini in this module. Ideally, `hou` should already be in
    # globals, as `homport` is meant to be run inside a Houdini session.
    if not 'hou' in globals():
        import hou

    # Move the original `hou.node` function out of the way, we'll call it later.
    hou.__node = hou.node

    def _wrap_node(*args, **kwargs):
        """
        This function is used to monkey patch the `hou.node` method in order to
        make the `homport` module transparent to users.
        """

        # Call the original, stashed `hou.node` function, then wrap it with
        # `NodeWrap`
        node = hou.__node(*args, **kwargs)
        return NodeWrap(node)

    # We could use the `@functools.wraps` decorator here, but this will do fine.
    _wrap_node.func_name = 'node'
    _wrap_node.func_doc = hou.node.func_doc
    hou.node = _wrap_node

class NodeWrapError(Exception):
    pass

class NodeWrap(object):
    """
    Wraps a `hou.Node` and provides extra functionality.
    """
    def __init__(self, node):
        """
        Initializes a `NodeWrap` object. You should not need to initialize this
        directly. Once `homport.start()` gets called, every node that gets
        returned will be wrapped by `NodeWrap`.
        """
        if not node:
            raise NodeWrapError('Invalid node given.')

        # Store a reference to the HOM node.
        self.node = node

        # Prime the `input_index`. This gets used later to specify which input
        # you want to make connections to.
        self.input_index = 0

    def createNode(self, name):
        """
        Wraps the node created by hou.Node.createNode in a NodeWrap object.
        """
        node = self.node.createNode(name)
        return NodeWrap(node)

    def __getattr__(self, name):
        """
        Easily get the children or parameters of the node without calling
        extra methods on the node. A useful convenience function.
        Examples:
            node = hou.node('/obj')
            node.geo1 # will return hou.node('/obj/geo1')
            node.tx # will return node.parm('tx')
            node.createNode # will return the bound method on node
        """

        # This is a special case for handling arbitrary inputs on the node.
        # This will usually be invoked in an expression like:
        #   `geo >> sphere.input_two`
        # When `sphere.input_two` gets called, set `input_index = 2` on
        # `sphere` and return it.
        inputs = ('input_one', 'input_two', 'input_three', 'input_four')
        if name in inputs:
            self.input_index = inputs.index(name)
            return self

        found_attrs = []
        # If the attr we're looking for is on the hou.Node object, grab it.
        # We'll put it in a list of `found_attrs` that will be used later.
        if hasattr(self.node, name):
            found_attrs.append(getattr(self.node, name))

        # The attr could be the name of a child `hou.Node` under `self.node`.
        # If we find one, store it in `found_attrs`.
        childNode = self.node.node(name)
        if childNode:
            found_attrs.append(NodeWrap(childNode))

        # If the name we're looking for is a `hou.Parm`, store it as well.
        parm = self.node.parm(name)
        if parm:
            found_attrs.append(ParmWrap(parm))


        # We can't find the name that was given in the places we looked, raise
        # an `AttributeError`.
        if len(found_attrs) == 0:
            msg = "Node object has no, parm, python attr or child Node " \
                  "called %s" % name
            raise AttributeError(msg)

        # Likewise, if we found more than one match for the given name, raise
        # an `AttributeError`.
        if len(attribs) > 1:
            msg = "%s is an ambiguous name, it could be one of %s" \
                % (name, found_attrs)
            raise AttributeError(msg)

        return found_attrs[0]

    def __setattr__(self, name, value):
        """
        This implementation of setattr enables setting of parameters using the
        `=` operator. Usually, you'd set a parm value like this:
            `node.parm('tx').set(50)`

        With this implementation, we can do this: `node.tx = 50`

        __Warning:__ this only works when the attr in question is a `ParmWrap`
        object on a `NodeWrap` object and not a standalone `hou.Parm` or
        `ParmWrap` object.
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
        Uses the `>>` operator to connect the left side's __output__ to the
        right side's __input__.
        Example:
            camera >> sphere

        is the same as calling: `sphere.setInput('0', camera)`
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
        Uses the `<<` operator to connect the left side's __input__ to the
        right side's __output__.
        Example:
            camera << sphere

        is the same as calling: `camera.setInput('0', sphere)`
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
        Disconnects `self` from `object`. Example:
            camera // sphere
        """
        node = object
        # Ensure the given node is connected to `self` before trying to
        # disconnect.
        conn = node.inputConnections()[node.input_index]
        if not conn.inputNode() == self.node:
            raise NodeWrapError('Input node is incorrect')
        else:
            node.setInput(node.input_index, None)

    def __repr__(self):
        """
        Returns a readable representation of the node, supplying its
        path and `NodeType`. Example: `<Node /obj of type obj>`
        """
        return "<Node %s of type %s>" % (self.node.path(),
                                         self.node.type().name())

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
        cur_node = self.parm.node()
        to_node = object.node()
        rel_path = cur_node.relativePathTo(to_node)
        rel_reference = 'ch(%s)' % rel_path
        self.parm.setExpression(rel_reference)

    def __lshift__(self, object):
        """
        node.ty << node2.tx
        """
        pass

    def __getattr__(self, name):
        """
        Gets the attributes of the wrapped parameter.
        """

        if name in dir(self.parm):
            return getattr(self.parm, name)
        else:
            msg = 'ParmWrap object has no attribute %s' % name
            raise AttributeError(msg)

    def __str__(self):
        """
        """
        return str(self.parm.eval())

