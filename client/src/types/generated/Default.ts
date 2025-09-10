import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const endpoints = makeApi([
  {
    method: "get",
    path: "/",
    alias: "read_root__get",
    requestFormat: "json",
    response: z.object({ message: z.string() }).passthrough(),
  },
]);

export const DefaultApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
