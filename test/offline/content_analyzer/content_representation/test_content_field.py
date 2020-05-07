from unittest import TestCase

from src.offline.content_analyzer.content_representation.content_field import FeaturesBagField


class TestFeaturesBagField(TestCase):

    def test_add_get_feature(self):
        feature = FeaturesBagField('repr_name')
        feature.add_feature('synsetID', 'global_score')
        self.assertEqual(feature.get_feature('synsetID'), 'global_score', "Error in the features_dict")

    def test_get_feature_dict(self):
        feature = FeaturesBagField('repr_name')
        feature.add_feature('synsetID_1', 'global_score_1')
        feature.add_feature('synsetID_2', 'global_score_2')
        self.assertEqual(feature.get_feature_dict(), {'synsetID_1': 'global_score_1', 'synsetID_2': 'global_score_2'},
                         "Error in the features_dict")