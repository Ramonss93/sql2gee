import unittest
from sql2gee import SQL2GEE
from ee import apitestcase, Filter, FeatureCollection, Feature


class TestSQL2GEE(apitestcase.ApiTestCase):
    def test_table_name_property(self):
        sql2gee = SQL2GEE('select pepe from mytable')
        table_name = sql2gee.table_name
        self.assertEqual(table_name, 'mytable')
        sql2gee = SQL2GEE('SELECT TOP 1 * FROM mytable ORDER BY unique_column DESC')
        table_name = sql2gee.table_name
        self.assertEqual(table_name, 'mytable')
        return

    def test_fields_property(self):
        sql2gee = SQL2GEE('select juan from mytable')
        fields = sql2gee.fields
        self.assertEqual(fields, ['juan'])
        return

    def test_multiple_fields_property(self):
        sql2gee = SQL2GEE('select pepe, juan, bob from mytable')
        fields = sql2gee.fields
        self.assertEqual(fields, ['pepe', 'juan', 'bob'])
        return

    def test_group_select_property(self):
        sql2gee = SQL2GEE('select count(pepe) from mytable')
        groups = sql2gee.group_functions
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'}])

    def test_several_group_select_property(self):
        sql2gee = SQL2GEE('select count(pepe), sum(pepe) from mytable')
        groups = sql2gee.group_functions
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'},
                                  {'function': 'SUM', 'value': 'pepe'}])

    def test_long_group_select(self):
        sql = 'select count(pepe), sum(pepe), avg(pepe), first(pepe), last(pepe), max(pepe), min(pepe) from mytable'
        sql2gee = SQL2GEE(sql)
        groups = sql2gee.group_functions
        self.assertEqual(groups, [{'function': 'COUNT', 'value': 'pepe'},
                                  {'function': 'SUM', 'value': 'pepe'},
                                  {'function': 'AVG', 'value': 'pepe'},
                                  {'function': 'FIRST', 'value': 'pepe'},
                                  {'function': 'LAST', 'value': 'pepe'},
                                  {'function': 'MAX', 'value': 'pepe'},
                                  {'function': 'MIN', 'value': 'pepe'}])

    def test_empty_group_select(self):
        sql2gee = SQL2GEE('select * from mytable')
        groups = sql2gee.group_functions
        self.assertEqual(groups, [])

    def test_where_simple(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2')
        where = sql2gee.where
        correct = Filter().gt('a', 2)
        self.assertEqual(where, correct)

    def test_where_with_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2')
        where = sql2gee.where
        correct = Filter().And(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)

    def test_where_with_or(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 or c = 2')
        where = sql2gee.where
        correct = Filter().Or(Filter().gt('a', 2), Filter().eq('c', 2))
        self.assertEqual(where, correct)

    def test_where_with_or_and_and(self):
        sql2gee = SQL2GEE('select * from mytable where a > 2 and c = 2 or x <= 2')
        where = sql2gee.where
        correct = Filter().Or(Filter().And(Filter().gt('a', 2), Filter().eq('c', 2)), Filter().lte('x', 2))
        self.assertEqual(where, correct)

    def test_where_with_string(self):
        sql2gee = SQL2GEE('select * from mytable where a = "pepe"')
        where = sql2gee.where
        correct = Filter().eq('a', 'pepe')
        self.assertEqual(where, correct)

    def test_simple_feature_collection(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" ')
        query = sql2gee.feature_collection
        correct = FeatureCollection('ft:mytable')
        self.assertEqual(query, correct)
        return

    def test_simple_feature_collection_with_where(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 ')
        query = sql2gee.feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_and_and(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2 and b = 2 ')
        query = sql2gee.feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('a', 2), Filter().eq('b', 2)))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_several_conditions(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where (a > 2 or b < 2) and b = 2 ')
        query = sql2gee.feature_collection
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().Or(Filter().gt('a', 2), Filter().lt('b', 2)), Filter().eq('b', 2)))
        self.assertEqual(query, correct)
        return

    def test_feature_collection_simple_with_where_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a > 2.2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_not_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where not a > 2.2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().gt('a', 2.2).Not())
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_eq(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', '2'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_startsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringStartsWith('a', '2'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_endsWith(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringEndsWith('a', '2'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_contains(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_not_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a not like "%2%" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().stringContains('a', '2').Not())
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_like_and_gt(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a like "%2%" and b > 2 ')
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().stringContains('a', '2'), Filter().gt('b', 2)))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_gt_and_like(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where b > 2 and a like "%2%"')
        correct = FeatureCollection('ft:mytable').filter(Filter().And(Filter().gt('b', 2), Filter().stringContains('a', '2')))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a = "a" ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', "a"))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_in(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1, 2) ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1, 2]))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_in_float(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in (1.2, 2) ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', [1.2, 2]))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_in_string(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a in ("a", "b") ')
        correct = FeatureCollection('ft:mytable').filter(Filter().inList('a', ['a', 'b']))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_is(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is NULL ')
        correct = FeatureCollection('ft:mytable').filter(Filter().eq('a', 'null'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_feature_collection_simple_with_where_is_not(self):
        sql2gee = SQL2GEE('select * from "ft:mytable" where a is not NULL ')
        correct = FeatureCollection('ft:mytable').filter(Filter().neq('a', 'null'))
        query = sql2gee.feature_collection
        self.assertEqual(query, correct)

    def test_fail_generate_feature_collection_with_where_is_incorrect(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select * from "ft:mytable" where a is "2" ')
            query = sql2gee.feature_collection
        self.assertTrue('IS only support NULL value' in context.exception)

    def test_fail_table_not_found(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select * from a,b')
            sql2gee.feature_collection
        self.assertTrue('Table not found' in context.exception)

    def test_fail_table_not_found(self):
        with self.assertRaises(Exception) as context:
            sql2gee = SQL2GEE('select count(*) from a')
            sql2gee.feature_collection
        self.assertTrue('* not allowed' in context.exception)
