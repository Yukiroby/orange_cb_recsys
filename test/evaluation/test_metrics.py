from unittest import TestCase
from orange_cb_recsys.evaluation.metrics import *


class Test(TestCase):
    def test_perform_ranking_metrics(self):

        truth_rank = {
            "item0": 1.0,
            "item1": 1.0,
            "item2": 0.85,
            "item3": 0.8,
            "item4": 0.7,
            "item5": 0.65,
            "item6": 0.4,
            "item7": 0.35,
            "item8": 0.2,
            "item9": 0.2,
        }

        # relevant_rank = {item: score for i, (item, score) in enumerate(truth_rank.items()) if score > 0.75}

        predicted_rank = {
            "item2": 0.9,
            "item5": 0.85,
            "item9": 0.75,
            "item0": 0.7,
            "item4": 0.65,
            "item1": 0.5,
            "item8": 0.2,
            "item7": 0.2,
        }

        col = ["item", "rating"]

        results = perform_ranking_metrics(
            pd.DataFrame(predicted_rank.items(), columns=col),
            pd.DataFrame(truth_rank.items(), columns=col),
            relevant_threshold=0.75,
        )

        results_2 = perform_ranking_metrics(
            pd.DataFrame(predicted_rank.items(), columns=col),
            pd.DataFrame(truth_rank.items(), columns=col),
            relevant_threshold=0.75,
            fn=2
        )

        results["F2"] = results_2["F2"]

        real_results = {
            "Precision": 0.375,
            "Recall": 0.75,
            "F1": 0.5,
            "F2": 0.625,
            "NDCG": [0.85, 0.75, 0.64, 0.72, 0.75, 0.81, 0.79, 0.80],
            "MRR": 0.8958333333333333
        }

        tolerance = 0.5
        for metric in real_results.keys():
            # print("{}: {}".format(metric, results[metric]))
            if metric != "NDCG":
                error = abs(results[metric] - real_results[metric])
                self.assertLessEqual(error, tolerance, "{} tolerance overtaking: error = {}, tolerance = {}".
                                     format(metric, error, tolerance))

    def test_perform_rmse(self):
        predictions = pd.Series([5, 5, 4, 3, 3, 2, 1])
        truth = pd.Series([5, 4, 3, 3, 1, 2, 1])
        self.assertEqual(perform_rmse(predictions, truth), 0.9258200997725514)

        predictions = pd.Series([5, 5, 4, 3, 3, 2, 1])
        truth = pd.Series([5, 4, 3, 3, 1, 2])
        with self.assertRaises(Exception):
            perform_rmse(predictions, truth)

    def test_perform_mae(self):
        predictions = pd.Series([5, 5, 4, 3, 3, 2, 1])
        truth = pd.Series([5, 4, 3, 3, 1, 2, 1])
        self.assertEqual(perform_mae(predictions, truth), 0.5714285714285714)

    def test_perform_prediction_metrics(self):
        predictions = pd.Series([5, 4, 4, 3, 3, 2, 1])
        truth = pd.Series([5, 5, 3, 3, 1, 2, 1])
        result = {
            "RMSE": 0.9258200997725514,
            "MAE": 0.5714285714285714
        }
        self.assertEqual(perform_prediction_metrics(predictions, truth), result)
