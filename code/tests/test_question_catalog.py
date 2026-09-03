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


class QuestionCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.recipes = cls.catalog["recipes"]

    def test_catalog_has_stable_schema_and_unique_ids(self):
        self.assertEqual(
            self.catalog["schema_version"], "finbi.question-catalog.v1"
        )
        ids = [recipe["question_id"] for recipe in self.recipes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 10)

    def test_every_recipe_declares_decision_and_provenance_contract(self):
        for recipe in self.recipes:
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
        desks = {recipe["desk"] for recipe in self.recipes}
        self.assertTrue(REQUIRED_DESKS <= desks)

    def test_rates_two_point_comparison_is_a_recipe_not_the_product_mission(self):
        rates = [r for r in self.recipes if r["question_id"] == "rates.bonds"]
        self.assertEqual(len(rates), 1)
        self.assertIn("2s10s", rates[0]["comparison_or_scenario"])
        self.assertNotIn("two-date Treasury comparison", self.catalog["mission"])

    def test_public_private_boundary_forbids_committing_private_raw_data(self):
        boundary = self.catalog["public_private_boundary"]
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
