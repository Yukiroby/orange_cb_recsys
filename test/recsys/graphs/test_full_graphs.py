from unittest import TestCase

from orange_cb_recsys.content_analyzer.ratings_manager import RatingsImporter
from orange_cb_recsys.content_analyzer.ratings_manager.rating_processor import NumberNormalizer
from orange_cb_recsys.content_analyzer.ratings_manager.ratings_importer import RatingsFieldConfig
from orange_cb_recsys.content_analyzer.raw_information_source import CSVFile
from orange_cb_recsys.evaluation.graph_metrics import nx_degree_centrality, nx_closeness_centrality, nx_dispersion
from orange_cb_recsys.recsys.graphs.full_graphs import NXFullGraph
import os
import pandas as pd
import networkx as nx

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

contents_path = os.path.join(THIS_DIR, '../../../contents')

ratings_filename = os.path.join(contents_path, 'exo_prop/new_ratings_small.csv')
movies_dir = os.path.join(contents_path, 'exo_prop/movielens_exo_1612956350.7812138/')
user_dir = os.path.join(contents_path, 'exo_prop/user_exo_1612956381.4652517/')


class TestNXFullGraph(TestCase):

    def setUp(self) -> None:
        df = pd.DataFrame.from_dict({'from_id': ["1", "1", "2", "2", "2", "3", "4", "4"],
                                     'to_id': ["tt0112281", "tt0112302", "tt0112281", "tt0112346",
                                               "tt0112453", "tt0112453", "tt0112346", "tt0112453"],
                                     'score': [0.8, 0.7, -0.4, 1.0, 0.4, 0.1, -0.3, 0.7]})

        self.g: NXFullGraph = NXFullGraph(df,
                                          user_contents_dir=user_dir,
                                          item_contents_dir=movies_dir,
                                          item_exo_representation="0",
                                          user_exo_representation="0",
                                          item_exo_properties=['starring'],
                                          user_exo_properties=['1']  # It's the column in the users .DAT which
                                                                     # identifies the gender
                                          )

    def test_init(self):
        # Simple assert just to make sure the graph is created
        self.assertGreater(len(self.g.user_nodes), 0)
        self.assertGreater(len(self.g.item_nodes), 0)
        self.assertGreater(len(self.g.property_nodes), 0)

    def test_add_user(self):
        # Add 'user' node
        self.assertFalse(self.g.is_user_node('u0'))
        self.g.add_user_node('u0')
        self.assertTrue(self.g.is_user_node('u0'))

        # Add 'user' node but it already exists as
        # an 'item' node, so it exists as both
        self.assertTrue(self.g.is_item_node('tt0112281'))
        self.g.add_user_node('tt0112281')
        self.assertTrue(self.g.is_user_node('tt0112281'))
        self.assertTrue(self.g.is_item_node('tt0112281'))

    def test_add_item(self):
        # Add 'item' node
        self.assertFalse(self.g.is_item_node('Tenet'))
        self.g.add_item_node('Tenet')
        self.assertTrue(self.g.is_item_node('Tenet'))

        # Add 'item' node but it already exists as
        # a 'user' node, so it exists as both
        self.assertTrue(self.g.is_user_node('1'))
        self.g.add_item_node('1')
        self.assertTrue(self.g.is_item_node('1'))
        self.assertTrue(self.g.is_user_node('1'))

    def test_add_property(self):
        # Add 'property' node
        self.assertFalse(self.g.is_property_node('Nolan'))
        self.g.add_property_node('Nolan')
        self.assertTrue(self.g.is_property_node('Nolan'))

        # Add 'property' node but it already exists as
        # a 'user' node, so it exists as both
        self.assertTrue(self.g.is_user_node('1'))
        self.g.add_property_node('1')
        self.assertTrue(self.g.is_property_node('1'))
        self.assertTrue(self.g.is_user_node('1'))

    def test_add_link_user_item(self):
        # Link existent 'user' node to an existent 'item' node
        self.g.add_user_node('u0')
        self.g.add_item_node('Tenet')
        self.assertIsNone(self.g.get_link_data('u0', 'Tenet'))
        self.g.add_link('u0', 'Tenet')
        expected = {'label': 'score_label', 'weight': 0.5}
        result = self.g.get_link_data('u0', 'Tenet')
        self.assertEqual(expected, result)

        # Link existent 'item' node to an existent 'user' node
        self.g.add_item_node('Tenet')
        self.g.add_user_node('1')
        self.assertIsNone(self.g.get_link_data('Tenet', '1'))
        self.g.add_link('Tenet', '1', 0.5)
        self.assertFalse(self.g.is_user_node('Tenet'))
        self.assertFalse(self.g.is_item_node('1'))
        self.assertIsNotNone(self.g.get_link_data('Tenet', '1'))

        # Try to Link non-existent 'user' node and non-existent 'item' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('u_new'))
        self.assertFalse(self.g.node_exists('i_new'))
        self.g.add_link('u_new', 'i_new', 0.5)
        self.assertFalse(self.g.is_user_node('u_new'))
        self.assertFalse(self.g.is_item_node('i_new'))
        self.assertIsNone(self.g.get_link_data('u_new', 'i_new'))

    def test_add_link_item_prop(self):
        # Link existent 'item' node to existent 'property' node
        self.g.add_item_node('Tenet')
        self.g.add_property_node('Nolan')
        self.g.add_link('Tenet', 'Nolan', weight=0.5, label='Director')
        result = self.g.get_properties('Tenet')
        expected = [{'Director': 'Nolan'}]
        self.assertEqual(expected, result)

        # Link existent 'property' node to existent 'item' node
        self.g.add_property_node('Nolan')
        self.g.add_item_node('Inception')
        self.g.add_link('Nolan', 'Inception', weight=0.5, label='Director of')
        result = self.g.get_link_data('Nolan', 'Inception')
        expected = {'label': 'Director of', 'weight': 0.5}
        self.assertEqual(expected, result)

        # Try to link non-existent 'item' node and non-existent 'property' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('i_new'))
        self.assertFalse(self.g.node_exists('prop_new'))
        self.g.add_link('i_new', 'prop_new', weight=0.5, label="PropertyNew")
        self.assertFalse(self.g.is_item_node('i_new'))
        self.assertFalse(self.g.is_property_node('prop_new'))
        self.assertIsNone(self.g.get_link_data('i_new', 'prop_new'))

    def test_add_link_user_property(self):
        # Link existent 'user' node to existent 'property' node
        self.g.add_user_node('u1')
        self.g.add_property_node('Nolan')
        self.g.add_link('u1', 'Nolan', weight=0.5, label='Friend')
        result = self.g.get_properties('u1')
        expected = [{'Friend': 'Nolan'}]
        self.assertEqual(expected, result)

        # Link existent 'property' node to existent 'user' node
        self.g.add_property_node('Nolan')
        self.g.add_user_node('u2')
        self.g.add_link('Nolan', 'u2', weight=0.5, label='Friend')
        result = self.g.get_link_data('Nolan', 'u2')
        expected = {'label': 'Friend', 'weight': 0.5}
        self.assertEqual(expected, result)

        # Try to link non-existent 'user' node and non-existent 'property' node,
        # so no link is created
        self.assertFalse(self.g.node_exists('u_new'))
        self.assertFalse(self.g.node_exists('prop_new'))
        self.g.add_link('u_new', 'prop_new', weight=0.5, label="PropertyNew")
        self.assertFalse(self.g.is_user_node('u_new'))
        self.assertFalse(self.g.is_property_node('prop_new'))
        self.assertIsNone(self.g.get_link_data('u_new', 'prop_new'))

    def test_pred_succ(self):
        # Get all predecessors of a node
        self.g.add_item_node('Titanic')
        self.g.add_property_node('DiCaprio')
        self.g.add_link('Titanic', 'DiCaprio', 0.5, "Starring")
        result = self.g.get_predecessors('DiCaprio')
        expected = ['Titanic']
        self.assertEqual(expected, result)

        # Get all successors of a node
        self.g.add_user_node('u0')
        self.g.add_item_node('Tenet')
        self.g.add_item_node('Inception')
        self.g.add_link('u0', 'Tenet', 0.5)
        self.g.add_link('u0', 'Inception', 0.5)
        result = self.g.get_successors('u0')
        expected = ['Tenet', 'Inception']
        self.assertEqual(expected, result)

    def test_add_item_tree(self):
        # Add 'item' tree, so add 'item' node and its properties to the graph
        self.assertFalse(self.g.is_item_node('tt0114709'))
        self.assertFalse(self.g.is_property_node('http://dbpedia.org/resource/Tom_Hanks'))
        self.g.add_item_tree('tt0114709')
        self.assertTrue(self.g.is_item_node('tt0114709'))
        self.assertTrue(self.g.is_property_node('http://dbpedia.org/resource/Tom_Hanks'))

        # Try to add 'user' tree
        self.g.add_user_node('20')
        self.assertTrue(self.g.is_user_node('20'))
        self.g.add_item_tree('20')
        expected = []
        result = self.g.get_properties('20')
        self.assertEqual(expected, result)
        self.assertTrue(self.g.is_item_node('20'))

    def test_add_user_tree(self):
        # Add from_tree, so the 'from' node and its properties
        self.assertFalse(self.g.is_user_node('11'))
        self.g.add_user_tree('11')
        self.assertTrue(self.g.is_user_node('11'))
        self.assertTrue(self.g.is_property_node('M'))
        self.assertTrue(self.g.is_property_node('F'))

        # Try to add 'item' tree
        self.g.add_item_node('tt0112641')
        self.assertTrue(self.g.is_item_node('tt0112641'))
        self.g.add_user_tree('tt0112641')
        expected = []
        result = self.g.get_properties('tt0112641')
        self.assertEqual(expected, result)
        self.assertTrue(self.g.is_user_node('tt0112641'))

    def test_graph_creation(self):
        # Test multiple graph creation possibilities

        # Import ratings as DataFrame
        ratings_import = RatingsImporter(
            source=CSVFile(ratings_filename),
            rating_configs=[RatingsFieldConfig(
                field_name='points',
                processor=NumberNormalizer(min_=1, max_=5))],
            from_field_name='user_id',
            to_field_name='item_id',
            timestamp_field_name='timestamp',
        )
        ratings_frame = ratings_import.import_ratings()

        # Create graph without setting the representation
        # EX. Create graph with properties 'producer' and 'starring' from
        # all exo representation, since there can be multiple exo representation
        # containing the same properties
        g = NXFullGraph(
            source_frame=ratings_frame,
            item_contents_dir=movies_dir,
            user_contents_dir=user_dir,
            item_exo_properties=['producer', 'starring'],
            user_exo_properties=['1']  # It's the column in the users DAT which identifies the gender
        )

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertGreater(len(g.property_nodes), 0)

        # Create graph without setting properties,
        # so ALL exo properties of the representation 0 will be retrieved
        g = NXFullGraph(
            source_frame=ratings_frame,
            item_contents_dir=movies_dir,
            user_contents_dir=user_dir,
            item_exo_representation="0",
            user_exo_representation="0"
        )

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertGreater(len(g.property_nodes), 0)

        # Create graph specifying without properties
        g = NXFullGraph(ratings_frame)

        # Simple assert just to make sure the graph is created
        self.assertGreater(len(g.user_nodes), 0)
        self.assertGreater(len(g.item_nodes), 0)
        self.assertEqual(len(g.property_nodes), 0)

    def test__graph(self):
        # Simple assert just to test the _graph method
        self.assertIsInstance(self.g._graph, nx.DiGraph)

    def test_metrics(self):
        # We calculate some metrics, simple assert to make sure they are
        # calculated
        self.assertGreater(len(nx_degree_centrality(self.g)), 0)
        self.assertGreater(len(nx_closeness_centrality(self.g)), 0)
        self.assertGreater(len(nx_dispersion(self.g)), 0)

        # movies_ca_config = ContentAnalyzerConfig(
        #     content_type='Item',
        #     source=JSONFile(movies_filename),
        #     id_field_name_list=['imdbID'],
        #     output_directory=output_dir
        # )
        #
        # movies_ca_config.append_exogenous_properties_retrieval(
        #     DBPediaMappingTechnique(
        #         entity_type='Film',
        #         lang='EN',
        #         label_field='Title'
        #     )
        # )
        #
        # ContentAnalyzer(movies_ca_config).fit()
        #
        # users_ca_config = ContentAnalyzerConfig(
        #     content_type='User',
        #     source=DATFile(user_filename),
        #     id_field_name_list=['0'],
        #     output_directory=output_dir
        # )
        #
        # users_ca_config.append_exogenous_properties_retrieval(
        #     PropertiesFromDataset()
        # )
        #
        # ContentAnalyzer(config=users_ca_config).fit()