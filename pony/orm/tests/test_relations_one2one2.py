import unittest
from pony.orm.core import *
from testutils import *

db = Database('sqlite', ':memory:')

class Male(db.Entity):
    name = Required(unicode)
    wife = Optional('Female', column='wife')

class Female(db.Entity):
    name = Required(unicode)
    husband = Optional('Male', column='husband')

db.generate_mapping(create_tables=True)

class TestOneToOne2(unittest.TestCase):
    def setUp(self):
        rollback()
        db.execute('delete from Male')
        db.execute('delete from Female')
        db.insert('Male', id=1, name='M1', wife=1)
        db.insert('Male', id=2, name='M2', wife=2)
        db.insert('Male', id=3, name='M3', wife=None)
        db.insert('Female', id=1, name='F1', husband=1)
        db.insert('Female', id=2, name='F2', husband=2)
        db.insert('Female', id=3, name='F3', husband=None)
        commit()
        rollback()
    def test_1(self):
        Male[3].wife = Female[3]

        self.assertEqual(Male[3]._vals_['wife'], Female[3])
        self.assertEqual(Female[3]._vals_['husband'], Male[3])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([1, 2, 3], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([1, 2, 3], husbands)
    def test_2(self):
        Female[3].husband = Male[3]

        self.assertEqual(Male[3]._vals_['wife'], Female[3])
        self.assertEqual(Female[3]._vals_['husband'], Male[3])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([1, 2, 3], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([1, 2, 3], husbands)
    def test_3(self):
        Male[1].wife = None

        self.assertEqual(Male[1]._vals_['wife'], None)
        self.assertEqual(Female[1]._vals_['husband'], None)
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([None, 2, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 2, None], husbands)
    def test_4(self):
        Female[1].husband = None

        self.assertEqual(Male[1]._vals_['wife'], None)
        self.assertEqual(Female[1]._vals_['husband'], None)
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([None, 2, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 2, None], husbands)
    def test_5(self):
        Male[1].wife = Female[3]

        self.assertEqual(Male[1]._vals_['wife'], Female[3])
        self.assertEqual(Female[1]._vals_['husband'], None)
        self.assertEqual(Female[3]._vals_['husband'], Male[1])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([3, 2, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 2, 1], husbands)
    def test_6(self):
        Female[3].husband = Male[1]

        self.assertEqual(Male[1]._vals_['wife'], Female[3])
        self.assertEqual(Female[1]._vals_['husband'], None)
        self.assertEqual(Female[3]._vals_['husband'], Male[1])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([3, 2, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 2, 1], husbands)
    def test_7(self):
        Male[1].wife = Female[2]

        self.assertEqual(Male[1]._vals_['wife'], Female[2])
        self.assertEqual(Male[2]._vals_['wife'], None)
        self.assertEqual(Female[1]._vals_['husband'], None)
        self.assertEqual(Female[2]._vals_['husband'], Male[1])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([2, None, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 1, None], husbands)
    def test_8(self):
        Female[2].husband = Male[1]

        self.assertEqual(Male[1]._vals_['wife'], Female[2])
        self.assertEqual(Male[2]._vals_['wife'], None)
        self.assertEqual(Female[1]._vals_['husband'], None)
        self.assertEqual(Female[2]._vals_['husband'], Male[1])
        commit()
        wives = db.select('wife from Male order by Male.id')
        self.assertEqual([2, None, None], wives)
        husbands = db.select('husband from Female order by Female.id')
        self.assertEqual([None, 1, None], husbands)
    @raises_exception(UnrepeatableReadError, 'Value of Male.wife for Male[1] was updated outside of current transaction')
    def test_9(self):
        db.execute('update Female set husband = 3 where id = 1')
        m1 = Male[1]
        f1 = m1.wife
        f1.name
    def test_10(self):
        db.execute('update Female set husband = 3 where id = 1')
        m1 = Male[1]
        f1 = Female[1]
        f1.name
        self.assert_('wife' not in m1._vals_)


if __name__ == '__main__':
    unittest.main()
