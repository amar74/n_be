import { generateZodClientFromOpenAPI, getHandlebars } from 'openapi-zod-client';
const hbs = getHandlebars();

hbs.registerHelper('customAlias', (path: string, method: string) => {
  const map: Record<string, string> = {};
  return map[`${method}:${path}`] || `${method}_${path}`.replace(/[\/:]/g, '_');
});

// Read OpenAPI URL from CLI args or env, fallback to local server
const argv = process.argv.slice(2);
let openApiUrl = process.env.OPENAPI_URL;
for (let i = 0; i < argv.length; i++) {
  const arg = argv[i];
  if (!arg.startsWith('-') && !openApiUrl) {
    openApiUrl = arg;
    break;
  }
  if (arg === '--url' || arg === '-u') {
    openApiUrl = argv[i + 1];
    break;
  }
  const match = arg.match(/^--url=(.+)$/);
  if (match) {
    openApiUrl = match[1];
    break;
  }
}
openApiUrl = openApiUrl || 'http://127.0.0.1:8000/openapi.json';

const res = await fetch(openApiUrl);
const openApiDoc = await res.json(); // cast if you want: as unknown as OpenAPIObject


await generateZodClientFromOpenAPI({
  // @ts-ignore
  openApiDoc,
  distPath: './src/types/generated/',
  handlebars: hbs,
  options: {
    groupStrategy: 'tag-file',
    exportTypes: true,
    withAlias: true,
  }
});