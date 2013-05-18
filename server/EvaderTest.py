import unittest
import Evader

class EvaderTest(unittest.TestCase):

    def test_registerUser(self):
        el = Evader.EvaderLogic()
        ed = Evader.EvaderData()
        uid = el.createUser(ed)
        self.assertFalse(uid == "")
        self.assertEqual(len(ed.player), 1)

    def test_generateTaskCompleteTasks(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic( False)
        uid1 = el.createUser(ed)
        # uid2 = ed.createUser()

        ed.addControl (Evader.Control(uid1, "Flux Control", "1"))
        
        # # task will run for 10 secs
        el.generateTasks (ed, None, 10)
        self.assertEqual(len(ed.currentTasks), 1)
        self.assertEqual(ed.currentTasks[0].isFailed , False)
        self.assertEqual(ed.currentTasks[0].isComplete , False)
        self.assertEqual(ed.currentTasks[0].timeRunning , 0.0)
        self.assertEqual(ed.currentTasks[0].shownToPlayer, uid1) 
        
        for i in range (10):
            el.execute (ed, Evader.EvaderInput(), 1.2)

        self.assertEqual(len(ed.currentTasks), 1)
        self.assertEqual(ed.currentTasks[0].shownToPlayer, uid1) 
        self.assertEqual(ed.currentTasks[0].isFailed , True)
        self.assertEqual(ed.currentTasks[0].isComplete , True)
        self.assertTrue(ed.currentTasks[0].timeRunning  > 10.0)
        
        
        
        # self.assertEqual( ed.currentTasks[1].shownToPlayer, uid1 ) 

    def test_generateControlsForPlayer(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        
        uid1 = el.createUser(ed)
         
        el.generateControl(ed, uid1)

    def test_matchInputToTask(self):
        ed = Evader.EvaderData()
        el = Evader.EvaderLogic()
        uid1 = el.createUser(ed)
        uid2 = el.createUser(ed)
        uid3 = el.createUser(ed)

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
        uid1 = el.createUser(ed)
        uid2 = el.createUser(ed)

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
        uid1 = el.createUser(ed)
        uid2 = el.createUser(ed)

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
