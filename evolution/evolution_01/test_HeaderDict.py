import unittest
from bottle import HeaderDict

class TestMultiDict(unittest.TestCase):

    # def test_isheader(self):
    #     """ HeaderDict replaces by default and title()s its keys """
    #     m = HeaderDict(abc_def=5)
    #     m['abc_def'] = 6
    #     self.assertEqual(['6'], m.getall('abc_def'))
    #     m.append('abc_def', 7)
    #     self.assertEqual(['6', '7'], m.getall('abc_def'))
    #     self.assertEqual([('Abc-Def', '6'), ('Abc-Def', '7')], list(m.iterallitems()))

    def test_headergetbug(self):
        ''' Assure HeaderDict.get() to be case insensitive '''
        d = HeaderDict()
        d['UPPER'] = 'UPPER'
        d['lower'] = 'lower'
        self.assertEqual(d['upper'], 'UPPER')
        self.assertEqual(d['LOWER'], 'lower')
        self.assertEqual(d.get('upper'), 'UPPER')
        self.assertEqual(d.get('LOWER'), 'lower')

if __name__ == '__main__':
    unittest.main()
