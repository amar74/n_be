import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const endpoints = makeApi([
  {
    method: "get",
    path: "/formbricks/login-token",
    alias: "getFormbricksLoginToken",
    requestFormat: "json",
    response: z.object({ token: z.string() }).passthrough(),
  },
]);

export const FormbricksApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
