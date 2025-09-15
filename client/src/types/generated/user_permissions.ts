import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const Permission = z.enum(["view", "edit"]);
const UserPermissionCreateRequest = z
  .object({
    userid: z.string().uuid(),
    accounts: z.array(Permission).optional(),
    opportunities: z.array(Permission).optional(),
    proposals: z.array(Permission).optional(),
  })
  .passthrough();
const UserPermissionResponse = z
  .object({
    userid: z.string().uuid(),
    accounts: z.array(Permission),
    opportunities: z.array(Permission),
    proposals: z.array(Permission),
  })
  .passthrough();
const UserPermissionUpdateRequest = z
  .object({
    accounts: z.union([z.array(Permission), z.null()]),
    opportunities: z.union([z.array(Permission), z.null()]),
    proposals: z.union([z.array(Permission), z.null()]),
  })
  .partial()
  .passthrough();
const UserPermissions = z
  .object({
    accounts: z.array(Permission),
    opportunities: z.array(Permission),
    proposals: z.array(Permission),
  })
  .passthrough();
const UserInfo = z
  .object({
    id: z.string().uuid(),
    email: z.string(),
    org_id: z.union([z.string(), z.null()]),
    role: z.string(),
  })
  .passthrough();
const UserWithPermissionsResponse = z
  .object({ user: UserInfo, permissions: UserPermissions })
  .passthrough();
const UserWithPermissionsResponseModel = z
  .object({ data: z.array(UserWithPermissionsResponse) })
  .passthrough();

export const schemas = {
  Permission,
  UserPermissionCreateRequest,
  UserPermissionResponse,
  UserPermissionUpdateRequest,
  UserPermissions,
  UserInfo,
  UserWithPermissionsResponse,
  UserWithPermissionsResponseModel,
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
