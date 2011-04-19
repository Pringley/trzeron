import unittest
import test_objects
import test_req
import test_xhr

if __name__ == '__main__':
    suite = unittest.TestSuite([
        test_req.suite(),
        test_objects.suite(),
        test_xhr.suite()
    ])
    unittest.TextTestRunner(verbosity=2).run(suite)
