# np. import 'blockList' from 'blockList.py'
import nodeList

# np. blockList.initBlockList() # initialize blockList

# initialize nodeList
nL = nodeList.NodeList()

# add nodes to nodeList
nL.addNode('100.200.300.400')
nL.addNode('200.300.400.500')

# print nodeList
print(nL)
