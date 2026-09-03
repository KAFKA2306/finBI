const CATALOG_URL = "./data/questions/catalog.v1.json";
const ROUTER_URL = "./data/questions/router.v1.json";
const LIVE_VIEWS = new Map([
  ["rates.bonds", { href: "#rates-desk", label: "Rates viewを開く" }],
  ["fx.carry_leverage", { href: "#fx-desk", label: "FX viewを開く" }],
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

  const liveView = LIVE_VIEWS.get(recipe.question_id);
  const badge = document.createElement("span");
  badge.className = "route-badge";
  badge.textContent = liveView ? "LIVE" : "PLANNED";

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

  if (liveView) {
    const link = document.createElement("a");
    link.href = liveView.href;
    link.textContent = liveView.label;
    article.append(link);
  } else {
    const state = document.createElement("span");
    state.className = "route-state";
    state.textContent = "BI viewは未接続 — 数値は表示しません";
    article.append(state);
  }
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
    message.textContent = "対応するBI viewがまだありません。BI要件候補として扱います。";
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
    const [catalogResponse, routerResponse] = await Promise.all([
      fetch(CATALOG_URL),
      fetch(ROUTER_URL),
    ]);
    if (!catalogResponse.ok || !routerResponse.ok) {
      throw new Error("BI catalog fetch failed");
    }
    const [catalog, router] = await Promise.all([
      catalogResponse.json(),
      routerResponse.json(),
    ]);
    recipesById = new Map(
      catalog.recipes.map((recipe) => [recipe.question_id, recipe]),
    );
    routes = router.routes;
    results.textContent = `${recipesById.size}個のBI要件を読み込みました。金融の論点を入力してください。`;
  } catch (error) {
    results.textContent = `BIカタログを読み込めません: ${error.message}`;
  }
}

button.addEventListener("click", routeQuestion);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") routeQuestion();
});

[
  "何を買うべき？",
  "USDJPY 3倍は？",
  "効率的フロンティア",
  "益利回りとEPS CAGR",
  "世界のM2は？",
  "予定納税はいくら？",
  "このニュースは信じられる？",
].forEach(addExample);

initQuestionRouter();
