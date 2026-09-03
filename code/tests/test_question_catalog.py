import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "data" / "questions" / "catalog.v1.json"

REQUIRED_RECIPE_FIELDS = {
    "question_id",
    "desk",
    "intent",
    "required_inputs",
    "data_authority",
    "as_of_policy",
    "calculation",
    "comparison_or_scenario",
    "decision_output",
    "risk_output",
    "provenance_output",
    "freshness_requirement",
    "failure_mode",
}

REQUIRED_DESKS = {
    "portfolio",
    "frontier-lab",
    "fx-desk",
    "rates-desk",
    "valuation",
    "macro",
    "event-lens",
    "products",
    "tax-cashflow",
    "backtest-lab",
    "audit",
}


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


class QuestionCatalogTest(unittest.TestCase):
    def test_catalog_has_stable_schema_and_unique_ids(self):
        catalog = load_catalog()
        recipes = catalog["recipes"]
        self.assertEqual(catalog["schema_version"], "finbi.question-catalog.v1")
        ids = [recipe["question_id"] for recipe in recipes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 10)

    def test_every_recipe_declares_decision_and_provenance_contract(self):
        recipes = load_catalog()["recipes"]
        for recipe in recipes:
            self.assertTrue(REQUIRED_RECIPE_FIELDS <= recipe.keys(), recipe)
            for field in (
                "required_inputs",
                "data_authority",
                "calculation",
                "comparison_or_scenario",
                "decision_output",
                "risk_output",
                "provenance_output",
            ):
                self.assertIsInstance(recipe[field], list)
                self.assertTrue(recipe[field], f"{recipe['question_id']}:{field}")
            for field in (
                "intent",
                "as_of_policy",
                "freshness_requirement",
                "failure_mode",
            ):
                self.assertIsInstance(recipe[field], str)
                self.assertTrue(recipe[field].strip())

    def test_catalog_covers_core_financial_desks(self):
        recipes = load_catalog()["recipes"]
        desks = {recipe["desk"] for recipe in recipes}
        self.assertTrue(REQUIRED_DESKS <= desks)

    def test_rates_two_point_comparison_is_a_recipe_not_the_product_mission(self):
        catalog = load_catalog()
        rates = [
            recipe
            for recipe in catalog["recipes"]
            if recipe["question_id"] == "rates.bonds"
        ]
        self.assertEqual(len(rates), 1)
        self.assertIn("2s10s", rates[0]["comparison_or_scenario"])
        self.assertNotIn("two-date Treasury comparison", catalog["mission"])

    def test_public_private_boundary_forbids_committing_private_raw_data(self):
        boundary = load_catalog()["public_private_boundary"]
        self.assertIs(boundary["public_repository"], True)
        private_rule = boundary["private_inputs"].casefold()
        for phrase in (
            "never commit",
            "account numbers",
            "private transaction exports",
            "tax documents",
            "credentials",
            "personal identifiers",
        ):
            self.assertIn(phrase, private_rule)


if __name__ == "__main__":
    unittest.main()
