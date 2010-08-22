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

    def testGetParm(self):
        null = hou.node('/obj').createNode('null')
        self.assertEquals(null.tx.parm, null.parm('tx'))

    def testRshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null

    def testLshift(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo << null

class ParmWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testParmsWrapped(self):
        self.assertEquals(self.geo1.tx.parm, self.geo1.node.parm('tx'))

    def testSetParm(self):
        self.geo1.tx = 500.0
        self.assertEquals(self.geo1.tx.eval(), 500.0)

    def testLinkParms(self):
        self.geo1.tx >> self.geo2.tx
        self.assertEquals(self.geo1.tx, self.geo2.tx)

if __name__ == "__main__":
    unittest.main()
