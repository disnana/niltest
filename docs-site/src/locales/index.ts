import ja from "./catalogs/ja";

export type Locale = string;
type Catalog = Record<string, string>;

const modules = import.meta.glob<{ default: Catalog }>("./catalogs/*.ts", { eager: true });

const catalogs: Record<string, Catalog> = { ja };
for (const [path, module] of Object.entries(modules)) {
  const locale = path.split("/").pop()?.replace(".ts", "") ?? "";
  if (locale && !locale.startsWith("_")) catalogs[locale] = module.default;
}

export const locales = Object.keys(catalogs).sort((a, b) => (a === "ja" ? -1 : b === "ja" ? 1 : a.localeCompare(b)));
export const defaultLocale = "ja";

export function t(locale: Locale, key: string): string {
  return catalogs[locale]?.[key] ?? ja[key] ?? key;
}

export function languageName(locale: Locale): string {
  return new Intl.DisplayNames([locale], { type: "language" }).of(locale) ?? locale;
}
