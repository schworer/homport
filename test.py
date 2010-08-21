import unittest

class NodeWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.assert_('hou' in globals())
        import homport
        homport.bootstrap()

    def testWrapped(self):
        hou.node('/obj').createNode('geo')
        self.assertEquals(hou.node('/obj/geo1'), hou.node('/obj').geo1.node)


if __name__ == "__main__":
    unittest.main()
