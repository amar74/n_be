import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { AuthUserResponse } from "./common";
import { ValidationError } from "./common";

const CurrentUserResponse = z.object({ user: AuthUserResponse }).passthrough();
const OnSignupSuccessResponse = z
  .object({ message: z.string(), user: AuthUserResponse })
  .passthrough();
const OnSignupErrorResponse = z
  .object({ message: z.string(), error: z.string() })
  .passthrough();

export const schemas = {
  CurrentUserResponse,
  OnSignupSuccessResponse,
  OnSignupErrorResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/auth/onsignup",
    alias: "onsignup_auth_onsignup_post",
    description: `Handle user signup from external auth provider`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ email: z.string() }).passthrough(),
      },
    ],
    response: OnSignupSuccessResponse,
    errors: [
      {
        status: 400,
        description: `Bad Request`,
        schema: OnSignupErrorResponse,
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/auth/verify_supabase_token",
    alias: "verify_supabase_token_auth_verify_supabase_token_get",
    description: `Verify token from Supabase and generate our own JWT`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/auth/me",
    alias: "getCurrentUser",
    description: `Get current authenticated user info`,
    requestFormat: "json",
    response: CurrentUserResponse,
  },
]);

export const AuthApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
