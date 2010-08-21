import unittest
import homport
homport.bootstrap()

class NodeWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue('hou' in globals())

    def testWrapped(self):
        self.assertTrue(isinstance(hou.node('/obj'), homport.NodeWrap))

    def testGetNode(self):
        hou.node('/obj').createNode('geo')
        self.assertEquals(hou.node('/obj/geo1').node, hou.node('/obj').geo1.node)

    def testConnection(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null

if __name__ == "__main__":
    unittest.main()
