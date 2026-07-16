export type TextKey = string;

export type Section = {
  id: string;
  title: TextKey;
  paragraphs?: TextKey[];
  bullets?: TextKey[];
  code?: string;
  note?: TextKey;
};

export type Page = {
  slug: string;
  nav: TextKey;
  group: TextKey;
  eyebrow: TextKey;
  title: TextKey;
  lead: TextKey;
  sections: Section[];
};

const basic = `import niltest
from niltest import expect, scenario

niltest.configure(mode="test")  # @scenarioより前

@scenario("配送料")
def shipping_fee(subtotal: int, premium: bool = False) -> int:
    if expect:
        expect.case(
            "プレミアム会員は無料",
            given={"subtotal": 1_000, "premium": True},
            returns=0,
        )

    return 0 if premium or subtotal >= 5_000 else 500`;

export const pages: Page[] = [
  {
    slug: "",
    nav: "nav.home",
    group: "group.start",
    eyebrow: "home.eyebrow",
    title: "home.title",
    lead: "home.lead",
    sections: [
      {
        id: "why",
        title: "home.why.title",
        paragraphs: ["home.why.p1"],
        bullets: ["home.why.b1", "home.why.b2", "home.why.b3"],
      },
      {
        id: "thirty-seconds",
        title: "home.quick.title",
        paragraphs: ["home.quick.p1"],
        code: basic,
        note: "home.quick.note",
      },
      {
        id: "fit",
        title: "home.fit.title",
        bullets: ["home.fit.b1", "home.fit.b2", "home.fit.b3", "home.fit.b4"],
      },
    ],
  },
  {
    slug: "getting-started",
    nav: "nav.gettingStarted",
    group: "group.start",
    eyebrow: "start.eyebrow",
    title: "start.title",
    lead: "start.lead",
    sections: [
      { id: "install", title: "start.install.title", paragraphs: ["start.install.p1", "start.install.p2", "start.install.p3"], code: `# Windows
python -m pip install niltest

# Ubuntu / macOS
python3 -m pip install niltest

# 仮想環境を有効化済みなら（全OS）
pip install niltest

# 環境によって利用できる別名
pip3 install niltest` },
      { id: "first", title: "start.first.title", paragraphs: ["start.first.p1"], code: basic },
      { id: "run", title: "start.run.title", paragraphs: ["start.run.p1"], code: "niltest run your_package.specs --language ja" },
      { id: "next", title: "start.next.title", bullets: ["start.next.b1", "start.next.b2", "start.next.b3"] },
    ],
  },
  {
    slug: "concepts",
    nav: "nav.concepts",
    group: "group.start",
    eyebrow: "concepts.eyebrow",
    title: "concepts.title",
    lead: "concepts.lead",
    sections: [
      { id: "one-source", title: "concepts.one.title", paragraphs: ["concepts.one.p1", "concepts.one.p2"] },
      { id: "modes", title: "concepts.modes.title", paragraphs: ["concepts.modes.p1"], bullets: ["concepts.modes.b1", "concepts.modes.b2", "concepts.modes.b3"] },
      { id: "pytest", title: "concepts.pytest.title", paragraphs: ["concepts.pytest.p1"], note: "concepts.pytest.note" },
    ],
  },
  {
    slug: "mocking",
    nav: "nav.mocking",
    group: "group.features",
    eyebrow: "mock.eyebrow",
    title: "mock.title",
    lead: "mock.lead",
    sections: [
      { id: "exact", title: "mock.exact.title", paragraphs: ["mock.exact.p1"], code: "import niltest\n\nniltest.configure(mode=\"mock\")  # @scenarioより前\nfrom your_package.shipping import shipping_fee\n\nresult = shipping_fee(1_000, premium=True)\nassert result == 0" },
      { id: "fallback", title: "mock.fallback.title", paragraphs: ["mock.fallback.p1"] },
      { id: "boundaries", title: "mock.boundaries.title", bullets: ["mock.boundaries.b1", "mock.boundaries.b2", "mock.boundaries.b3"] },
    ],
  },
  {
    slug: "testing",
    nav: "nav.testing",
    group: "group.features",
    eyebrow: "test.eyebrow",
    title: "test.title",
    lead: "test.lead",
    sections: [
      { id: "python", title: "test.python.title", code: "import niltest\n\nniltest.configure(mode=\"test\")  # @scenarioより前\nfrom your_package.shipping import shipping_fee\n\nresult = niltest.run_tests(shipping_fee)\nassert result.success\nprint(result.to_dict())" },
      { id: "cli", title: "test.cli.title", paragraphs: ["test.cli.p1"], code: "niltest run your_package.specs\nniltest run your_package.specs --json" },
      { id: "inspect", title: "test.inspect.title", paragraphs: ["test.inspect.p1"], code: "niltest inspect your_package.services\nniltest inspect your_package.services --json" },
      { id: "exit", title: "test.exit.title", bullets: ["test.exit.b1", "test.exit.b2", "test.exit.b3"] },
    ],
  },
  {
    slug: "expectations",
    nav: "nav.expectations",
    group: "group.features",
    eyebrow: "expect.eyebrow",
    title: "expect.title",
    lead: "expect.lead",
    sections: [
      { id: "values", title: "expect.values.title", paragraphs: ["expect.values.p1"], code: "returns={\"id\": 1, \"name\": \"Alice\"}" },
      { id: "types", title: "expect.types.title", paragraphs: ["expect.types.p1"], code: "returns=UserData  # isinstanceで確認" },
      { id: "validators", title: "expect.validators.title", paragraphs: ["expect.validators.p1"], code: "returns=lambda result: result[\"count\"] > 0" },
      { id: "models", title: "expect.models.title", paragraphs: ["expect.models.p1"] },
      { id: "conforms", title: "expect.conforms.title", paragraphs: ["expect.conforms.p1"], code: "from niltest import conforms_to\n\nreturns=conforms_to(list[User])\nreturns=conforms_to(Annotated[int, Field(gt=0)])" },
      { id: "input-validation", title: "expect.inputs.title", paragraphs: ["expect.inputs.p1", "expect.inputs.p2"], code: `class Payload(BaseModel):
    count: int

@scenario("集計")
@docs(case("辞書入力", given={"payload": {"count": 2}}, returns=4))
def process(payload: Payload) -> int:
    # case実行時、payloadは検証済みのPayloadモデル
    return payload.count * 2` },
    ],
  },
  {
    slug: "async",
    nav: "nav.async",
    group: "group.advanced",
    eyebrow: "async.eyebrow",
    title: "async.title",
    lead: "async.lead",
    sections: [
      { id: "define", title: "async.define.title", paragraphs: ["async.define.p1"], code: "@scenario(\"ユーザー取得\")\nasync def fetch_user(user_id: int) -> dict:\n    if expect:\n        expect.case(\"成功\", given={\"user_id\": 1}, returns={\"id\": 1})\n    return await database.fetch_user(user_id)" },
      { id: "concurrency", title: "async.concurrent.title", paragraphs: ["async.concurrent.p1"], note: "async.concurrent.note" },
    ],
  },
  {
    slug: "production",
    nav: "nav.production",
    group: "group.advanced",
    eyebrow: "prod.eyebrow",
    title: "prod.title",
    lead: "prod.lead",
    sections: [
      { id: "enable", title: "prod.enable.title", paragraphs: ["prod.enable.p1"], code: "# macOS / Linux\nNILTEST_MODE=test python app.py\n\n# Windows PowerShell\n$env:NILTEST_MODE = \"test\"; python app.py\n\n# mockを使う場合は test を mock に変更" },
      { id: "declared", title: "prod.declared.title", paragraphs: ["prod.declared.p1", "prod.declared.p2"], code: `from niltest import case, docs, scenario

@scenario("配送料")
@docs(case("プレミアム会員", given={"premium": True}, returns=0))
def shipping_fee(premium: bool) -> int:
    return 0 if premium else 500` },
      { id: "guarantee", title: "prod.guarantee.title", paragraphs: ["prod.guarantee.p1", "prod.guarantee.p2"] },
      { id: "benchmark", title: "prod.benchmark.title", code: "python benchmark_production.py", note: "prod.benchmark.note" },
    ],
  },
  {
    slug: "localization",
    nav: "nav.localization",
    group: "group.advanced",
    eyebrow: "i18n.eyebrow",
    title: "i18n.title",
    lead: "i18n.lead",
    sections: [
      { id: "select", title: "i18n.select.title", paragraphs: ["i18n.select.p1"], code: "niltest.configure(language=\"ja\")\nniltest.configure(language=\"en\")" },
      { id: "extend", title: "i18n.extend.title", paragraphs: ["i18n.extend.p1"], code: "from niltest import register_locale\n\nregister_locale(\"fr\", messages)" },
      { id: "docs-translation", title: "i18n.docs.title", paragraphs: ["i18n.docs.p1"], note: "i18n.docs.note" },
    ],
  },
  {
    slug: "recipes",
    nav: "nav.recipes",
    group: "group.recipes",
    eyebrow: "recipes.eyebrow",
    title: "recipes.title",
    lead: "recipes.lead",
    sections: [
      { id: "api-client", title: "recipes.api.title", paragraphs: ["recipes.api.p1"], code: "@scenario(\"プロフィール取得\")\ndef get_profile(user_id: int) -> dict:\n    if expect:\n        expect.case(\"開発用\", given={\"user_id\": 1}, returns={\"name\": \"Alice\"})\n    return api.get(f\"/users/{user_id}\").json()" },
      { id: "random", title: "recipes.random.title", paragraphs: ["recipes.random.p1"], code: "returns=lambda token: isinstance(token, str) and len(token) >= 32" },
      { id: "ci", title: "recipes.ci.title", paragraphs: ["recipes.ci.p1"], code: "niltest run app.specs --json" },
    ],
  },
  {
    slug: "api",
    nav: "nav.api",
    group: "group.reference",
    eyebrow: "api.eyebrow",
    title: "api.title",
    lead: "api.lead",
    sections: [
      { id: "configure", title: "api.configure.title", code: "configure(mode=None, language=None)", paragraphs: ["api.configure.p1"] },
      { id: "scenario", title: "api.scenario.title", code: "@scenario(title)", paragraphs: ["api.scenario.p1"] },
      { id: "case", title: "api.case.title", code: "expect.case(name, *, desc=\"\", given, returns)", paragraphs: ["api.case.p1"] },
      { id: "run", title: "api.run.title", code: "run_tests(*functions) -> RunResult", paragraphs: ["api.run.p1"] },
      { id: "conforms", title: "api.conforms.title", code: "conforms_to(type_hint, *, strict=False) -> TypeExpectation", paragraphs: ["api.conforms.p1"] },
      { id: "locale", title: "api.locale.title", code: "register_locale(locale, messages, *, overwrite=False)", paragraphs: ["api.locale.p1"] },
    ],
  },
];

export const pageBySlug = new Map(pages.map((page) => [page.slug, page]));
