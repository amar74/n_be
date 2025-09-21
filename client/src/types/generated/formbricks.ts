import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const Survey = z
  .object({
    id: z.string(),
    environment_id: z.string(),
    createdAt: z.string(),
    updatedAt: z.string(),
    name: z.string(),
  })
  .passthrough();
const SurveyListResponse = z.object({ surveys: z.array(Survey) }).passthrough();
const SurveyLinkResponse = z
  .object({ url: z.string(), token: z.string() })
  .passthrough();

export const schemas = {
  Survey,
  SurveyListResponse,
  SurveyLinkResponse,
};

const endpoints = makeApi([
  {
    method: "get",
    path: "/formbricks/login-token",
    alias: "getFormbricksLoginToken",
    requestFormat: "json",
    response: z.object({ token: z.string() }).passthrough(),
  },
  {
    method: "get",
    path: "/formbricks/surveys",
    alias: "getFormbricksSurveys",
    description: `List Formbricks surveys for the current user&#x27;s organization.

Uses the organization&#x27;s configured Formbricks environment ID.`,
    requestFormat: "json",
    response: SurveyListResponse,
  },
  {
    method: "post",
    path: "/formbricks/surveys",
    alias: "createFormbricksSurvey",
    description: `Create a new Formbricks survey in the current user&#x27;s organization.

Returns the created survey mapped to our Survey schema.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ name: z.string() }).passthrough(),
      },
    ],
    response: Survey,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/formbricks/surveys/:survey_id/link",
    alias: "createFormbricksSurveyLink",
    description: `Generate a link for an existing Formbricks survey for a given email.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ email: z.string() }).passthrough(),
      },
      {
        name: "survey_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: SurveyLinkResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const FormbricksApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
