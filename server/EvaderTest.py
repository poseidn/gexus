import unittest
import Evader

class EvaderTest(unittest.TestCase):

    def test_registerUser(self):
        ed = Evader.EvaderData()
        uid = ed.createUser()
        self.assertFalse(uid == "")
        self.assertEqual(len(ed.player), 1)

    def test_generateTask(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        uid1 = ed.createUser()
        # uid2 = ed.createUser()

        ed.addControl (Evader.Control(uid1, "Flux Control", "1"))
        el.generateTasks (ed)
        self.assertEqual(len(ed.currentTasks), 1)
        
        self.assertEqual(ed.currentTasks[0].shownToPlayer, uid1) 
        # self.assertEqual( ed.currentTasks[1].shownToPlayer, uid1 ) 

    def test_generateControlsForPlayer(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        
        uid1 = ed.createUser()
         
        el.generateControl(ed, uid1)

    def test_matchInputToTask(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        uid1 = ed.createUser()
        uid2 = ed.createUser()
        uid3 = ed.createUser()

        ed.addControl (Evader.Control(uid1, "Flux Control", "1"))
        ed.addControl (Evader.Control(uid2, "My Flux Control", "2"))
        ed.addControl (Evader.Control(uid2, "My Flux Control", "5"))

        el.generateTasks (ed, 0)

        self.assertEqual(len(ed.currentTasks), 3)
        
        actionList = { uid1 : "1", uid2 : "2" }
        
        self.assertTrue(ed.currentTasks[0].doesMatch (actionList))

        # possibleAct = ed.getPossibleActions()

    def test_executeLogic(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        uid1 = ed.createUser()
        uid2 = ed.createUser()

        ed.addControl (Evader.Control(uid1, "Flux Control", "1"))
        ed.addControl (Evader.Control(uid2, "My Flux Control", "2"))

        eInput = Evader.EvaderInput()
        actionList = {}
        eInput.content = actionList

        el.execute (ed, eInput, 1.0)

        self.assertEqual(len(ed.currentTasks), 2)
        
        actionList = { uid1 : "1", uid2:"2" }
        eInput.content = actionList
        
        el.execute (ed, eInput, 1.0)

        self.assertEqual(len(ed.currentTasks), 4)
        self.assertEqual(len(ed.getCompletedTasks()), 2)
        self.assertEqual(len(ed.getUncompletedTasks()), 2)


    def test_addRemoveControls(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        uid1 = ed.createUser()
        uid2 = ed.createUser()

        ed.addControl (Evader.Control(uid1, "Flux Control", "0"))
        ed.addControl (Evader.Control(uid2, "My Flux Control", "1"))
        ed.addControl (Evader.Control(uid2, "More Flux Control", "3"))
        ed.addControl (Evader.Control(uid1, "lux Control", "4"))
        ed.addControl (Evader.Control(uid1, "slider Control", "5", "slider"))

        possibleAct = ed.getPossibleActions()
        self.assertEqual(len(possibleAct), 14)

        self.assertEqual(len(ed.possibleControls), 5)

        ed.removeControlsOfPlayer(uid2)

        self.assertEqual(len(ed.possibleControls), 2)


if __name__ == '__main__':
    unittest.main()
