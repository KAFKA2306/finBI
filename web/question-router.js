const CATALOG_URL = "./data/questions/catalog.v1.json";
const PUBLIC_VIEWS = new Map([
  ["rates.bonds", { href: "#rates-desk", label: "米国債の保存データを比較", state: "保存データ" }],
  ["fx.carry_leverage", { href: "#fx-desk", label: "米ドル比率の検証状況を確認", state: "上流の検証状況" }],
]);

const input = document.querySelector("#question-query");
const button = document.querySelector("#question-route");
const results = document.querySelector("#question-results");
const examples = document.querySelector("#question-examples");

let recipesById = new Map();
let routes = [];

function normalized(value) {
  return String(value)
    .toLowerCase()
    .replace(/[\s　/_・,，。?？!！:：()（）+-]/g, "");
}

function scoreRoute(query, route) {
  const q = normalized(query);
  if (!q) return 0;
  let score = 0;
  for (const term of route.terms) {
    const t = normalized(term);
    if (!t) continue;
    if (q.includes(t)) score += Math.max(6, t.length);
    else if (t.includes(q) && q.length >= 2) score += 3;
  }
  const recipe = recipesById.get(route.question_id);
  if (recipe) {
    const body = normalized(JSON.stringify(recipe));
    if (body.includes(q)) score += 2;
  }
  return score;
}

function createResult(recipe, rank) {
  const article = document.createElement("article");
  article.className = "route-result";

  const top = document.createElement("div");
  top.className = "route-result-top";

  const view = PUBLIC_VIEWS.get(recipe.question_id);
  const badge = document.createElement("span");
  badge.className = "route-badge";
  badge.textContent = view.state;

  const desk = document.createElement("span");
  desk.className = "route-desk";
  desk.textContent = recipe.desk;
  top.append(badge, desk);

  const title = document.createElement("strong");
  title.textContent = `${rank}. ${recipe.intent}`;

  const needs = document.createElement("p");
  needs.textContent = `見るべきデータ: ${recipe.required_inputs.join(" / ")}`;

  const output = document.createElement("p");
  output.textContent = `BI指標: ${recipe.calculation.join(" / ")} · Risk: ${recipe.risk_output.join(" / ")}`;

  article.append(top, title, needs, output);

  const link = document.createElement("a");
  link.href = view.href;
  link.textContent = view.label;
  article.append(link);
  return article;
}

function routeQuestion() {
  if (!recipesById.size || !routes.length) {
    results.textContent = "BIカタログをまだ読み込めていません。";
    return;
  }

  const query = input.value.trim();
  if (!query) {
    results.textContent = "金融の論点を入力してください。";
    return;
  }

  const ranked = routes
    .map((route) => ({ route, score: scoreRoute(query, route) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  results.replaceChildren();
  if (!ranked.length) {
    const message = document.createElement("p");
    message.textContent = "該当する公開画面はありません。";
    results.append(message);
    return;
  }

  ranked.forEach((item, index) => {
    const recipe = recipesById.get(item.route.question_id);
    if (recipe) results.append(createResult(recipe, index + 1));
  });
}

function addExample(label) {
  const example = document.createElement("button");
  example.type = "button";
  example.className = "chip ask-example";
  example.textContent = label;
  example.addEventListener("click", () => {
    input.value = label;
    routeQuestion();
  });
  examples.append(example);
}

async function initQuestionRouter() {
  try {
    const response = await fetch(CATALOG_URL);
    if (!response.ok) throw new Error("BI catalog fetch failed");
    const catalog = await response.json();
    recipesById = new Map(
      catalog.recipes.map((recipe) => [recipe.question_id, recipe]),
    );
    routes = catalog.routes.filter((route) => PUBLIC_VIEWS.has(route.question_id));
    results.textContent = "米国債利回りか米ドル比率を入力してください。";
  } catch (error) {
    results.textContent = `BIカタログを読み込めません: ${error.message}`;
  }
}

button.addEventListener("click", routeQuestion);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") routeQuestion();
});

[
  "米国債",
  "米ドル比率 FX",
].forEach(addExample);

initQuestionRouter();
