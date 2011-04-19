import unittest
import xhr

class EmptyXhrTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_blank(self):
        self.assertTrue(True,
                        msg='Truth is not true!')



def suite():
    test_cases = [
        EmptyXhrTestCase,
    ]
    suites = [unittest.TestLoader().loadTestsFromTestCase(test_case)
              for test_case in test_cases]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
