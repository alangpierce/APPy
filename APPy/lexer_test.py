__author__ = 'alangpierce'

import unittest

class MyTestCase(unittest.TestCase):
    def test_simple_tokens(self):
        input_string = '''
            5 + 3
        '''
        self.assertEquals(5, len(input_string))


