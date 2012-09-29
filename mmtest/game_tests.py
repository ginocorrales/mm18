import unittest
import mm18.game.constants
from mm18.game.tower import Tower
from mm18.game.units import Unit
from mm18.game.board import Board
from mm18.game.player import Player
from mm18.game.path import Path

"""Tests for the game code go here"""
class TestGame(unittest.TestCase):

	def setUp(self):
		unittest.TestCase.setUp(self)
		self.testBoard = Board([(0,1),(1,1)], [(0,2),(1,2),(1,3),(0,4)])
		self.testPlayer = Player("testName", self.testBoard)
		self.testTower = Tower(self.testPlayer)
		self.testEngine = Engine()

	def testResourcesIs(self):
		self.testPlayer.resources = mm18.game.constants.BASE_RESOURCES
		self.assertEquals(self.testPlayer.resourcesIs(),mm18.game.constants.BASE_RESOURCES)

	def testAllowedUpgradeIs(self):
		self.testPlayer.allowedUpgrade = 1
		self.assertEquals(self.testPlayer.allowedUpgradeIs(),1)

	def testAddResources(self):
		self.testPlayer.resources = mm18.game.constants.BASE_RESOURCES
		self.testPlayer.addResources(42)
		self.assertEquals(self.testPlayer.resourcesIs(), mm18.game.constants.BASE_RESOURCES+42)

	"""BOARD TESTS"""
# =============================================================================
	def testInvalidBoardCreation(self):
		with self.assertRaises(TypeError):
			test = Board(1)

	def testValidBoardCreation(self):
		self.assertEquals(len(self.testBoard.tower),0)

	def testJsonLoadAndOrderPathSquaresByClosest(self):
		testBoard1 = Board.jsonLoad("board1.json")
		self.assertEquals(testBoard1.base,[(5, 5), (5, 6), (5, 4), (6, 5), (6, 6), (6, 4), (4, 5), (4, 6), (4, 4)])
		self.assertEquals(testBoard1.path,[(5, 7), (5, 3), (7, 5), (3, 5), (5, 8), (5, 2), (8, 5), (2, 5), (5, 9), (5, 1), (9, 5), (1, 5), (5, 10), (5, 0), (10, 5), (0, 5)])

	def testFindPaths(self):
		board = Board.jsonLoad("board1.json")
		paths = board.findPaths()
		self.assertTrue( [(0,5),  (1,5), (2,5), (3,5)] in paths)
		self.assertTrue( [(10,5), (9,5), (8,5), (7,5)] in paths)
		self.assertTrue( [(5,0),  (5,1), (5,2), (5,3)] in paths)
		self.assertTrue( [(5,10), (5,9), (5,8), (5,7)] in paths)

	def testInvalidPosition(self):
		self.assertFalse(self.testBoard.validPosition((mm18.game.constants.BOARD_SIDE,mm18.game.constants.BOARD_SIDE)))

	def testInvalidPosition1(self):
		self.assertFalse(self.testBoard.validPosition((-1,-1)))

	def testInvalidPosition2(self):
		self.assertFalse(self.testBoard.validPosition((2,-1)))

	def testInvalidPosition3(self):
		with self.assertRaises(TypeError):
			self.testBoard.validPosition(5)

	def testValidPosition(self):
		self.assertTrue(self.testBoard.validPosition((0,0)))

	def testInvalidAddItem(self):
		with self.assertRaises(TypeError):
			self.testBoard.addItem("meow")

	def testInvalidAddItem1(self):
		self.assertFalse(self.testBoard.addItem("meow",(0,-1)))

	def testValidAddItem(self):
		self.testBoard.addItem(self.testPlayer,(0,0))
		self.assertEquals(self.testBoard.tower[(0,0)],self.testPlayer)

	def testValidGetItem(self):
		self.assertEquals(self.testBoard.getItem((0,1)),None)

	def testValidRemoveItem(self):
		self.testBoard.addItem(self.testPlayer,(0,0))
		self.testBoard.tower[(0,0)]
		self.testBoard.removeItem((0,0))
		with self.assertRaises(KeyError):
			self.testBoard.tower[(0,0)]

	def testAddHitList(self):
		tower = Tower(self.testPlayer)
		self.testBoard.addItem(tower, (0, 0))
		self.testBoard.addToHitList(tower, (0,0))
		print self.testBoard.hitList

	"""PATH TESTS"""
# =============================================================================
	def testPath(self):
		 p = Path([1,3,2])
		 self.assertEquals(
			 list(p.entries()),
			 [(None, 1), (None, 3), (None, 2)])
		 p.start('A')
		 self.assertEquals(p.advance(), None)
		 self.assertEquals(list(p.entries()),
						   [(None, 1), (None, 3), ('A', 2)])
		 self.assertEquals(p.advance(), None)
		 p.start('B')
		 self.assertEquals(list(p.entries()),
						   [(None, 1), ('A', 3), (None, 2)])
		 self.assertEquals(p.advance(), None)
		 self.assertEquals(list(p.entries()),
						   [('A', 1), (None, 3), ('B', 2)])
		 p.start('C')
		 p.start('D')
		 self.assertEquals(p.advance(), 'A')
		 self.assertEquals(list(p.entries()),
						   [(None, 1), ('B', 3), ('C', 2)])
		 self.assertEquals(p.advance(), None)
		 self.assertEquals(list(p.entries()),
						   [('B', 1), ('C', 3), ('D', 2)])
		 self.assertEquals(p.advance(), 'B')
		 self.assertEquals(p.advance(), 'C')
		 self.assertEquals(p.advance(), 'D')
		 self.assertEquals(list(p.entries()),
						   [(None, 1), (None, 3), (None, 2)])

	"""Unit Tests"""
	#Not enough resources
	def testInvalidPurchaseUnit(self):
		self.testPlayer.resources = 0
		test = Unit.purchaseUnit(1,0,self.testPlayer)
		self.assertEquals(test,None)

	#Level too high
	def testInvalidPurchaseUnit1(self):
		test = Unit.purchaseUnit(3,0,self.testPlayer)
		self.assertEquals(test,None)

	#Invalid spec
	def testInvalidPurchaseUnit2(self):
		testUnit = Unit.purchaseUnit(1,-2,self.testPlayer)
		self.assertEquals(testUnit, None)
		testUnit = Unit.purchaseUnit(1,2,self.testPlayer)
		self.assertEquals(testUnit, None)

	def testValidPurchaseUnit(self):
		testUnit = Unit.purchaseUnit(1,1,self.testPlayer)
		self.assertEquals(testUnit.level,1)
		self.assertEquals(testUnit.specialisation,1)
		self.assertEquals(testUnit.owner, self.testPlayer.name)

	"""TOWER TESTS"""
# =============================================================================
	def testInvalidPurchaseTower(self):
		self.testPlayer.resources = 0
		testTower = self.testPlayer.purchaseTower()
		self.assertEquals(testTower, None)

	def testValidPurchaseTower(self):
		testTower = self.testPlayer.purchaseTower()
		self.assertEquals(self.testPlayer.resources,mm18.game.constants.BASE_RESOURCES - mm18.game.constants.TOWER_BASE_COST)
		self.assertEquals(testTower.upgrade, 1)
		self.assertEquals(testTower.specialisation, 0)

	#Already fully upgraded
	def testInvalidTowerUpgrade(self):
		self.testTower.upgrade = mm18.game.constants.MAX_UPGRADE
		self.assertFalse(self.testTower.upgradeTower(self.testPlayer))

	#Not enough resources
	def testInvalidTowerUpgrade1(self):
		self.testPlayer.resources = 0
		self.assertFalse(self.testTower.upgradeTower(self.testPlayer))

	#Not allowed to upgrade higher
	def testInvalidTowerUpgrade2(self):
		self.assertFalse(self.testTower.upgradeTower(self.testPlayer))

	def testValidTowerUpgrade(self):
		self.testPlayer.allowedUpgrade += 1
		self.assertTrue(self.testTower.upgradeTower(self.testPlayer))

	def testInvalidTowerSpec(self):
		self.testTower.upgrade += 1
		self.assertFalse(self.testTower.specialise(0))

	def testInvalidTowerSpec1(self):
		self.assertFalse(self.testTower.specialise(-2))
		self.assertFalse(self.testTower.specialise(2))
		self.assertFalse(self.testTower.specialise(1.5))

	def testValidTowerSpec(self):
		self.assertTrue(self.testTower.specialise(1))

	def testValidFire(self):
		testUnit = Unit.purchaseUnit(1,0,self.testPlayer)
		testTower = self.testPlayer.purchaseTower()
		self.testTower.fire(testUnit)
		self.assertEqual(testUnit.health, 0)

	def testValidSell(self):
		testTower = self.testPlayer.purchaseTower((1,0))
		self.testPlayer.resources = 0
		self.testPlayer.sellTower((1,0))
		self.assertFalse(self.testPlayer.resources==0)

	"""def testValidMovement(self):
		testUnit=Unit.purchaseUnit(1,0,self.testPlayer,1)
		self.assertTrue(self.testBoard.queueUnit(testUnit, testUnit.pathID))
		self.testBoard.moveUnits()
		testTest=False;
		for unit in self.testBoard.paths[1].moving:
			#if unit==testUnit and pos==(0,2):
				#testTest=True;
			self.assertEquals(unit, testUnit)
			self.assertEquals(pos, (0,2))
			testTest=True;
		self.assertTrue(testTest)
	"""

	"""ENGINE TESTS"""
# =============================================================================

	def testAddPlayer(self):
		self.assertEquals(0, len(self.testEngine.get_player_ids()))
		self.testEngine.add_player(1)
		self.assertEquals(1, len(self.testEngine.get_player_ids()))
	"""def testSupply(self):
		self.testplayer.allowedUpgrade = 1;
		self.testplayer.resources = 0;
		self.testEngine.supply()
		self.assertEquals(self.testplayer.resources, constants.BASE_RESOURCES + constants.UPGRADE_INCREASE*1)
		self.testplayer.allowedUpgrade = 2;
		self.testplayer.resources = 0;
		self.testEngine.supply()
		self.assertEquals(self.testplayer.resources, constants.BASE_RESOURCES + constants.UPGRADE_INCREASE*2)
		self.testplayer.allowedUpgrade = 3;
		self.testplayer.resources = 0;
		self.testEngine.supply()
		self.assertEquals(self.testplayer.resources, constants.BASE_RESOURCES + constants.UPGRADE_INCREASE*3)

	def testMoveUnits(self):
		pass

	def testTowerResponses(self):
		pass
	
	def get_player(self, player_id):
		return self.players.get(player_id

	def board_get(self, player_id):
		return self.get_player(player_id).board"""



	
"""Uncomment & delete this line for concise test output
if __name__ == "__main__":
	unittest.main()
"""
suite = unittest.TestLoader().loadTestsFromTestCase(TestGame)
unittest.TextTestRunner(verbosity=2).run(suite)
