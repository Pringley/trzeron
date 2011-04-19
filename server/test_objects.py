import unittest
import objects

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.user = objects.User.client()
        self.user2 = objects.User.client()
        self.user3 = objects.User.client()

    def test_login(self):
        username = 'bob123'
        password = 'pwd101'
        wrong_password = 'aaagh42'
        self.assertTrue(self.user.login(username, password),
                        msg='registration not successful')
        self.assertTrue(self.user2.login(username, password),
                        msg='logging in again not successful')
        self.assertFalse(self.user3.login(username, wrong_password),
                        msg='a wrong password was accepted!')


        

def suite():
    test_cases = [UserTestCase]
    suites = [unittest.TestLoader().loadTestsFromTestCase(test_case)
              for test_case in test_cases]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
