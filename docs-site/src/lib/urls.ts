export function docUrl(locale: string, slug = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const localePath = locale === "ja" ? "" : `${locale}/`;
  const pagePath = slug ? `/${slug}` : "";
  return `${base}/docs/${localePath}${pagePath.replace(/^\//, "")}${slug ? "/" : ""}`;
}
