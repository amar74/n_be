import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const AddressCreate = z
  .object({
    line1: z.string().min(1).max(255),
    line2: z.union([z.string(), z.null()]).optional(),
    city: z.union([z.string(), z.null()]).optional(),
    pincode: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const ContactCreate = z
  .object({
    name: z.string().min(1).max(255),
    email: z.string().max(255),
    phone: z.string().min(10).max(15),
    title: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ClientType = z.enum(["tier_1", "tier_2", "tier_3"]);
const AccountCreate = z
  .object({
    company_website: z.union([z.string(), z.null()]).optional(),
    client_name: z.string().min(1).max(255),
    client_address: AddressCreate,
    primary_contact: ContactCreate,
    secondary_contacts: z.array(ContactCreate).max(10).optional(),
    client_type: ClientType,
    market_sector: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AddressResponse = z
  .object({
    line1: z.string().min(1).max(255),
    line2: z.union([z.string(), z.null()]).optional(),
    city: z.union([z.string(), z.null()]).optional(),
    pincode: z.union([z.number(), z.null()]).optional(),
    address_id: z.string().uuid(),
  })
  .passthrough();
const ContactResponse = z
  .object({
    name: z.string().min(1).max(255),
    email: z.string().max(255),
    phone: z.string().min(10).max(15),
    title: z.union([z.string(), z.null()]).optional(),
    contact_id: z.string().uuid(),
  })
  .passthrough();
const AccountDetailResponse = z
  .object({
    account_id: z.string().uuid(),
    company_website: z.union([z.string(), z.null()]).optional(),
    client_name: z.string(),
    client_address: z.union([AddressResponse, z.null()]).optional(),
    primary_contact: z.union([ContactResponse, z.null()]).optional(),
    secondary_contacts: z.array(ContactResponse).optional(),
    client_type: ClientType,
    market_sector: z.union([z.string(), z.null()]).optional(),
    notes: z.union([z.string(), z.null()]).optional(),
    total_value: z.union([z.number(), z.null()]).optional(),
    opportunities: z.union([z.number(), z.null()]).optional(),
    last_contact: z.union([z.string(), z.null()]).optional(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AccountListItem = z
  .object({
    account_id: z.string().uuid(),
    client_name: z.string(),
    client_address: z.union([AddressResponse, z.null()]).optional(),
    primary_contact_name: z.union([z.string(), z.null()]).optional(),
    primary_contact_email: z.union([z.string(), z.null()]).optional(),
    client_type: ClientType,
    market_sector: z.union([z.string(), z.null()]).optional(),
    total_value: z.union([z.number(), z.null()]).optional(),
    ai_health_score: z.union([z.number(), z.null()]).optional(),
    last_contact: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AccountListResponse = z
  .object({
    accounts: z.array(AccountListItem),
    pagination: z.object({}).partial().passthrough(),
  })
  .passthrough();
const AccountUpdate = z
  .object({
    company_website: z.union([z.string(), z.null()]),
    client_name: z.union([z.string(), z.null()]),
    client_address: z.union([AddressCreate, z.null()]),
    primary_contact: z.union([ContactCreate, z.null()]),
    client_type: z.union([ClientType, z.null()]),
    market_sector: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ContactAddRequest = z.object({ contact: ContactCreate }).passthrough();
const ContactListResponse = z
  .object({ contacts: z.array(ContactResponse) })
  .passthrough();
const AccountCreateResponse = z
  .object({
    status_code: z.number().int().optional().default(201),
    account_id: z.string(),
    message: z.string(),
  })
  .passthrough();
const search = z.union([z.string(), z.null()]).optional();
const AccountUpdateResponse = z
  .object({
    status_code: z.number().int().optional().default(200),
    account_id: z.string(),
    message: z.string(),
  })
  .passthrough();
const AccountDeleteResponse = z
  .object({
    status_code: z.number().int().optional().default(200),
    message: z.string(),
  })
  .passthrough();
const ContactCreateResponse = z
  .object({
    status_code: z.number().int().optional().default(201),
    contact_id: z.string(),
    message: z.string(),
  })
  .passthrough();
const ContactUpdateResponse = z
  .object({
    status_code: z.number().int().optional().default(200),
    contact_id: z.string(),
    message: z.string(),
  })
  .passthrough();
const ContactUpdateRequest = z
  .object({
    name: z.union([z.string(), z.null()]),
    email: z.union([z.string(), z.null()]),
    phone: z.union([z.string(), z.null()]),
    title: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ContactDeleteResponse = z
  .object({
    status_code: z.number().int().optional().default(200),
    message: z.string(),
  })
  .passthrough();

export const schemas = {
  AddressCreate,
  ContactCreate,
  ClientType,
  AccountCreate,
  AddressResponse,
  ContactResponse,
  AccountDetailResponse,
  AccountListItem,
  AccountListResponse,
  AccountUpdate,
  ContactAddRequest,
  ContactListResponse,
  AccountCreateResponse,
  search,
  AccountUpdateResponse,
  AccountDeleteResponse,
  ContactCreateResponse,
  ContactUpdateResponse,
  ContactUpdateRequest,
  ContactDeleteResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/accounts/",
    alias: "createAccount",
    description: `Create a new account with primary contact and optional secondary contacts`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AccountCreate,
      },
    ],
    response: AccountCreateResponse,
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
    path: "/accounts/",
    alias: "listAccounts",
    description: `List accounts with pagination and optional search`,
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(10),
      },
      {
        name: "search",
        type: "Query",
        schema: search,
      },
      {
        name: "tier",
        type: "Query",
        schema: search,
      },
    ],
    response: AccountListResponse,
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
    path: "/accounts/:account_id",
    alias: "getAccountById",
    description: `Get account details with all contacts (primary and secondary)`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountDetailResponse,
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
    path: "/accounts/:account_id",
    alias: "updateAccount",
    description: `Update account details including address and primary contact`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AccountUpdate,
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountUpdateResponse,
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
    path: "/accounts/:account_id",
    alias: "deleteAccount",
    description: `Delete account and all associated contacts`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountDeleteResponse,
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
    path: "/accounts/:account_id/contacts",
    alias: "addSecondaryContact",
    description: `Add a new secondary contact to an account`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactAddRequest,
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactCreateResponse,
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
    path: "/accounts/:account_id/contacts",
    alias: "getAccountContacts",
    description: `Get all contacts for an account (primary and secondary)`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactListResponse,
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
    path: "/accounts/:account_id/contacts/:contact_id",
    alias: "updateContact",
    description: `Update a contact (primary or secondary)`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactUpdateRequest,
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactUpdateResponse,
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
    path: "/accounts/:account_id/contacts/:contact_id",
    alias: "deleteContact",
    description: `Delete a secondary contact from an account (cannot delete primary contact)`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "contact_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: ContactDeleteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const AccountsApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
