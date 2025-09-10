import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const UserInfo = z
  .object({
    id: z.string().uuid(),
    email: z.string(),
    org_id: z.union([z.string(), z.null()]),
    role: z.string(),
  })
  .passthrough();
const UserPermissions = z
  .object({
    accounts: z.array(z.string()),
    opportunities: z.array(z.string()),
    proposals: z.array(z.string()),
  })
  .passthrough();
const UserWithPermissionsResponse = z
  .object({ user: UserInfo, permissions: UserPermissions })
  .passthrough();
const UserWithPermissionsResponseModel = z
  .object({ data: z.array(UserWithPermissionsResponse) })
  .passthrough();
const UserPermissionResponse = z
  .object({
    userid: z.string().uuid(),
    accounts: z.array(z.string()),
    opportunities: z.array(z.string()),
    proposals: z.array(z.string()),
  })
  .passthrough();
const UserPermissionCreateRequest = z
  .object({
    userid: z.string().uuid(),
    accounts: z.array(z.string()).optional(),
    opportunities: z.array(z.string()).optional(),
    proposals: z.array(z.string()).optional(),
  })
  .passthrough();
const UserPermissionUpdateRequest = z
  .object({
    accounts: z.union([z.array(z.string()), z.null()]),
    opportunities: z.union([z.array(z.string()), z.null()]),
    proposals: z.union([z.array(z.string()), z.null()]),
  })
  .partial()
  .passthrough();

export const schemas = {
  UserInfo,
  UserPermissions,
  UserWithPermissionsResponse,
  UserWithPermissionsResponseModel,
  UserPermissionResponse,
  UserPermissionCreateRequest,
  UserPermissionUpdateRequest,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/user-permissions/",
    alias: "createUserPermission",
    description: `Create a new user permission`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserPermissionCreateRequest,
      },
    ],
    response: UserPermissionResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/user-permissions/",
    alias: "listUserPermissions",
    description: `Get all users from current user&#x27;s organization with their permissions`,
    requestFormat: "json",
    parameters: [
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(1000).optional().default(100),
      },
    ],
    response: UserWithPermissionsResponseModel,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/user-permissions/:userid",
    alias: "getUserPermission",
    description: `Get user permission by user ID`,
    requestFormat: "json",
    parameters: [
      {
        name: "userid",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: UserPermissionResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/user-permissions/:userid",
    alias: "updateUserPermission",
    description: `Update user permission by user ID (creates if doesn&#x27;t exist)`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserPermissionUpdateRequest,
      },
      {
        name: "userid",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: UserPermissionResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/user-permissions/:userid",
    alias: "deleteUserPermission",
    description: `Delete user permission by user ID`,
    requestFormat: "json",
    parameters: [
      {
        name: "userid",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const User_permissionsApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
