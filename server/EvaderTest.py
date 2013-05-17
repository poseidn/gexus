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
        uid = ed.createUser()

        el.generateTasks (ed)
        self.assertEqual(len(ed.currentTasks), 1)


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
