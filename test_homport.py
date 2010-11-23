import unittest
import homport
homport.start()

class NodeWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue('hou' in globals())

    def testWrapped(self):
        self.assertTrue(isinstance(hou.node('/obj'), homport.NodeWrap))

    def testInvalidNode(self):
        self.assertRaises(homport.NodeWrapError, hou.node, 'test')

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

    def testFloorDiv(self):
        geo = hou.node('/obj').createNode('geo')
        null = hou.node('/obj').createNode('null')
        geo >> null
        self.assertTrue(len(null.inputConnections()) == 1)

        geo // null
        self.assertTrue(len(null.inputConnections()) == 0)

    def testDefinedInputConn(self):
        geo = hou.node('/obj').createNode('geo')
        subnet = hou.node('/obj').createNode('subnet')
        geo >> subnet.input_two
        self.assert_(subnet.inputConnectors()[1])

    def testInputConnectReset(self):
        geo = hou.node('/obj').createNode('geo')
        subnet = hou.node('/obj').createNode('subnet')
        geo >> subnet.input_two
        self.assert_(subnet.inputConnectors()[1])

        # this should properly connect geo to input 0 of the subnet
        geo >> subnet
        self.assert_(subnet.inputConnectors()[0])

class ParmWrapTestCase(unittest.TestCase):
    def setUp(self):
        self.geo1 = hou.node('/obj').createNode('geo')
        self.geo2 = hou.node('/obj').createNode('geo')

    def testParmsWrapped(self):
        self.assertEquals(self.geo1.tx.parm, self.geo1.node.parm('tx'))

    def testSetParm(self):
        self.geo1.tx = 500
        self.assertEquals(self.geo1.tx.eval(), 500)

    def testEvalParm(self):
        self.geo1.tx.set(500.0)
        self.assertEquals(self.geo1.tx.eval(), 500.0)

    def testStrParm(self):
        self.geo1.tx.set(500.0)
        self.assertEquals(str(self.geo1.tx), str(500.0))

    def testLinkParms(self):
        self.geo1.tx >> self.geo2.tx
        self.geo1.tx = 450.0
        self.assertEquals(str(self.geo1.tx), str(self.geo2.tx))

if __name__ == "__main__":
    unittest.main()
