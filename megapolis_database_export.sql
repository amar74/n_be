--
-- PostgreSQL database dump
--

\restrict XEG5jO1KldBZC1ke1rm9TTyAenAHtPE22oZDoSwY90oQQF2OCRWkQdEXBSbvxvu

-- Dumped from database version 16.10 (Homebrew)
-- Dumped by pg_dump version 16.10 (Homebrew)

-- Started on 2025-10-20 08:35:17 IST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS megapolis_dev;
--
-- TOC entry 4017 (class 1262 OID 16384)
-- Name: megapolis_dev; Type: DATABASE; Schema: -; Owner: macbookpro
--

CREATE DATABASE megapolis_dev WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE megapolis_dev OWNER TO macbookpro;

\unrestrict XEG5jO1KldBZC1ke1rm9TTyAenAHtPE22oZDoSwY90oQQF2OCRWkQdEXBSbvxvu
\connect megapolis_dev
\restrict XEG5jO1KldBZC1ke1rm9TTyAenAHtPE22oZDoSwY90oQQF2OCRWkQdEXBSbvxvu

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3 (class 3079 OID 16690)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 4018 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- TOC entry 2 (class 3079 OID 16683)
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- TOC entry 4019 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- TOC entry 908 (class 1247 OID 16503)
-- Name: clienttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.clienttype AS ENUM (
    'tier_1',
    'tier_2',
    'tier_3'
);


ALTER TYPE public.clienttype OWNER TO postgres;

--
-- TOC entry 917 (class 1247 OID 16590)
-- Name: invitestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.invitestatus AS ENUM (
    'PENDING',
    'ACCEPTED',
    'EXPIRED'
);


ALTER TYPE public.invitestatus OWNER TO postgres;

--
-- TOC entry 929 (class 1247 OID 24577)
-- Name: opportunity_stage; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.opportunity_stage AS ENUM (
    'lead',
    'qualification',
    'proposal_development',
    'rfp_response',
    'shortlisted',
    'presentation',
    'negotiation',
    'won',
    'lost',
    'on_hold'
);


ALTER TYPE public.opportunity_stage OWNER TO postgres;

--
-- TOC entry 932 (class 1247 OID 24598)
-- Name: risk_level; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.risk_level AS ENUM (
    'low_risk',
    'medium_risk',
    'high_risk'
);


ALTER TYPE public.risk_level OWNER TO postgres;

--
-- TOC entry 2157 (class 3602 OID 16771)
-- Name: english_unaccent; Type: TEXT SEARCH CONFIGURATION; Schema: public; Owner: postgres
--

CREATE TEXT SEARCH CONFIGURATION public.english_unaccent (
    PARSER = pg_catalog."default" );

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR asciiword WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR word WITH public.unaccent, english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR numword WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR email WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR url WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR host WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR sfloat WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR version WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR hword_numpart WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR hword_part WITH public.unaccent, english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR hword_asciipart WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR numhword WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR asciihword WITH english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR hword WITH public.unaccent, english_stem;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR url_path WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR file WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR "float" WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR "int" WITH simple;

ALTER TEXT SEARCH CONFIGURATION public.english_unaccent
    ADD MAPPING FOR uint WITH simple;


ALTER TEXT SEARCH CONFIGURATION public.english_unaccent OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 228 (class 1259 OID 24625)
-- Name: account_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.account_documents (
    id uuid NOT NULL,
    account_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    category character varying(100) NOT NULL,
    date timestamp without time zone NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path character varying(512),
    file_size integer,
    mime_type character varying(100),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.account_documents OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16668)
-- Name: account_notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.account_notes (
    id uuid NOT NULL,
    account_id uuid NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    date timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.account_notes OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16509)
-- Name: accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts (
    account_id uuid NOT NULL,
    company_website character varying(255),
    client_name character varying(255) NOT NULL,
    client_type public.clienttype NOT NULL,
    market_sector character varying(255),
    notes character varying(1024),
    total_value numeric,
    ai_health_score numeric,
    opportunities integer,
    last_contact timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    client_address_id uuid,
    primary_contact_id uuid,
    org_id uuid,
    hosting_area character varying(255),
    account_approver character varying(255),
    approval_date timestamp without time zone,
    health_trend character varying(20),
    risk_level character varying(20),
    last_ai_analysis timestamp without time zone,
    data_quality_score numeric,
    revenue_growth numeric,
    communication_frequency numeric,
    win_rate numeric,
    custom_id character varying(20)
);


ALTER TABLE public.accounts OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16456)
-- Name: address; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.address (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    line1 character varying(255) NOT NULL,
    line2 character varying(255),
    pincode integer,
    org_id uuid,
    city character varying(255),
    state character varying(100)
);


ALTER TABLE public.address OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16395)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16469)
-- Name: contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contacts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    phone character varying(50),
    email character varying(255),
    org_id uuid,
    account_id uuid,
    name character varying(255),
    title character varying(100)
);


ALTER TABLE public.contacts OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16568)
-- Name: formbricks_projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.formbricks_projects (
    id uuid NOT NULL,
    project_id character varying(255),
    dev_env_id character varying(255),
    prod_env_id character varying(255),
    organization_id uuid NOT NULL
);


ALTER TABLE public.formbricks_projects OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16495)
-- Name: invites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invites (
    id uuid NOT NULL,
    org_id uuid,
    role character varying NOT NULL,
    email character varying NOT NULL,
    invited_by uuid NOT NULL,
    token character varying NOT NULL,
    status public.invitestatus NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.invites OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 24605)
-- Name: opportunities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.opportunities (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    created_by uuid NOT NULL,
    project_name character varying(500) NOT NULL,
    client_name character varying(255) NOT NULL,
    description text,
    stage public.opportunity_stage NOT NULL,
    risk_level public.risk_level,
    project_value numeric(15,2),
    currency character varying(3) NOT NULL,
    my_role character varying(255),
    team_size integer,
    expected_rfp_date timestamp with time zone,
    deadline timestamp with time zone,
    state character varying(100),
    market_sector character varying(255),
    match_score integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    account_id uuid,
    custom_id character varying(20)
);


ALTER TABLE public.opportunities OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 24837)
-- Name: opportunity_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.opportunity_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    opportunity_id uuid NOT NULL,
    file_name character varying(255) NOT NULL,
    original_name character varying(255) NOT NULL,
    file_type character varying(100) NOT NULL,
    file_size integer NOT NULL,
    file_path character varying(500),
    category character varying(100) NOT NULL,
    purpose character varying(100) NOT NULL,
    description text,
    status character varying(50) DEFAULT 'uploaded'::character varying,
    is_available_for_proposal boolean DEFAULT true,
    tags text,
    upload_date timestamp with time zone DEFAULT now(),
    file_url character varying(500),
    uploaded_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.opportunity_documents OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 24792)
-- Name: opportunity_overviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.opportunity_overviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    opportunity_id uuid NOT NULL,
    project_description text,
    project_scope jsonb,
    key_metrics jsonb,
    documents_summary jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.opportunity_overviews OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16436)
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    id uuid NOT NULL,
    owner_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address_id uuid,
    website character varying(255),
    contact_id uuid,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    formbricks_organization_id character varying(255),
    custom_id character varying(20)
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16640)
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_permissions (
    userid uuid NOT NULL,
    accounts character varying[] NOT NULL,
    opportunities character varying[] NOT NULL,
    proposals character varying[] NOT NULL
);


ALTER TABLE public.user_permissions OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16430)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    org_id uuid,
    role character varying(50) NOT NULL,
    formbricks_user_id character varying(255)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 4009 (class 0 OID 24625)
-- Dependencies: 228
-- Data for Name: account_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_documents (id, account_id, name, category, date, file_name, file_path, file_size, mime_type, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4007 (class 0 OID 16668)
-- Dependencies: 226
-- Data for Name: account_notes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.account_notes (id, account_id, title, content, date, created_at, updated_at) FROM stdin;
8f538d78-a423-4f22-88b5-d30a61dd5422	03bb5220-b667-492f-82cd-3ef3d1b44691	test	test	2025-10-11 00:00:00	2025-10-12 05:05:29.18766	\N
340d1319-f5cf-4d87-b782-9b979b76591f	9a5d52c4-4958-4f10-b306-2dde268e782b	test notes 2	test ww	2025-10-11 00:00:00	2025-10-12 23:41:51.044925	2025-10-12 23:42:06.585722
\.


--
-- TOC entry 4004 (class 0 OID 16509)
-- Dependencies: 223
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts (account_id, company_website, client_name, client_type, market_sector, notes, total_value, ai_health_score, opportunities, last_contact, created_at, updated_at, client_address_id, primary_contact_id, org_id, hosting_area, account_approver, approval_date, health_trend, risk_level, last_ai_analysis, data_quality_score, revenue_growth, communication_frequency, win_rate, custom_id) FROM stdin;
700b5f8f-b44c-45bb-aab1-7027190cbe51	https://softication.in/	testoq	tier_1	Infrastructure	\N	\N	\N	\N	\N	2025-10-12 01:19:30.801619	2025-10-12 01:19:30.801619	80c35530-a85f-43da-8963-64e90c827c80	174bee63-6a31-4d2f-b417-b31983dfb21a	299cfc3a-9791-4379-9602-9123d9e3043b	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	AC-NY002
9a5d52c4-4958-4f10-b306-2dde268e782b	https://arsoltion.com/	AR Soltuins	tier_1	Environmental	\N	\N	\N	\N	\N	2025-10-12 23:37:15.187564	2025-10-12 23:37:15.187564	e90f0ff0-91f1-4caf-8148-34a4bad11396	5f9de8c4-bfe9-46ee-9b9d-efe72c6a6f19	c47d0e0b-212c-455e-9c54-f16907e8e15b	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	AC-NY004
6fecce56-ac8f-48e8-b478-bd65b187e8ef	https://arsoltionaa.com/	AR Soltuins s	tier_2	Aviation	\N	\N	\N	\N	\N	2025-10-12 23:38:31.157602	2025-10-12 23:38:31.157602	ed3ae3b7-c26a-4eb8-a77a-06978d595e90	89d6fa23-0ded-44bf-b443-995ff85d4d25	c47d0e0b-212c-455e-9c54-f16907e8e15b	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	AC-NY005
be9293ff-db94-4a76-81cb-bea3671e57e7	https://softication.com/	SoftiCation Technology	tier_1	Transportation	\N	\N	62.8	\N	\N	2025-10-13 04:26:24.904642	2025-10-13 23:54:30.826001	c10d3b19-e86e-4c6c-b5f5-7f3d8249c5d4	45bdb0b2-acf1-4c95-aa8a-16a0b3600083	bcc561d3-b04d-4f80-9878-f644d41016b9	\N	\N	\N	stable	medium	2025-10-13 18:24:30.826929	\N	\N	\N	\N	AC-NY006
78c5f5cd-0e38-4288-98db-b15a72dc5a53	https://softication.com/	SoftiCation Technology	tier_3	SaaS, AI/ML, Cloud Solutions Provider	\N	\N	55.2	\N	\N	2025-10-13 16:59:49.594298	2025-10-13 17:00:29.120523	5db78931-8d17-48f2-8179-f40c9522037b	c69a1511-65e0-4bb4-ab3e-41a060b30685	bcc561d3-b04d-4f80-9878-f644d41016b9	\N	\N	\N	stable	high	2025-10-13 11:30:29.1218	\N	\N	\N	\N	AC-NY007
a0298d91-b408-45bc-b9e4-88a9f8134c76	https://www.ducatindia.com/	DUCAT	tier_2	IT Training	\N	\N	59	\N	\N	2025-10-14 17:35:19.461282	2025-10-14 17:35:54.293127	f4158df2-0076-4f23-93fe-1aa5cd46e74e	a1a8e2ec-6b92-456a-9f2f-2355ca0de2a2	bcc561d3-b04d-4f80-9878-f644d41016b9	\N	\N	\N	stable	high	2025-10-14 12:05:54.294269	\N	\N	\N	\N	AC-NY008
44a94d02-7a6c-4ecb-a26c-1a7243dc1425	https://softication.com/	testdbk	tier_1	Transportation	\N	\N	62.8	\N	\N	2025-10-12 01:16:17.262768	2025-10-15 20:45:52.951997	ff68b19d-5d5a-45d0-ba27-e2a179d53e6c	69db28a6-09a8-4f1c-8adc-897144f68fe1	299cfc3a-9791-4379-9602-9123d9e3043b	\N	\N	\N	stable	medium	2025-10-15 15:15:52.952791	\N	\N	\N	\N	AC-NY001
03bb5220-b667-492f-82cd-3ef3d1b44691	https://softication.com/	test 01	tier_1	Infrastructure	\N	\N	69	\N	\N	2025-10-12 03:55:11.585783	2025-10-15 21:03:01.295452	276d33e9-0d69-4ef8-a78b-05842c74ba55	a89b69f2-2c3b-4f34-bb4c-74aa40b6bff8	299cfc3a-9791-4379-9602-9123d9e3043b	\N	\N	\N	stable	medium	2025-10-15 15:33:01.29636	\N	\N	\N	\N	AC-NY003
\.


--
-- TOC entry 4001 (class 0 OID 16456)
-- Dependencies: 220
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.address (id, line1, line2, pincode, org_id, city, state) FROM stdin;
b6751c62-988a-4edd-bc4b-19cf2367f9f5	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	20588	fd275679-7bd0-4320-be81-3fff79721974	Baltimore	\N
262ae688-7d45-46ad-b4ad-14d7f1f5e1a8	3rd floor Laxminagarsdasqhj	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	299cfc3a-9791-4379-9602-9123d9e3043b	Broken Arrow	OK
ff68b19d-5d5a-45d0-ba27-e2a179d53e6c	testsdkbk	test	20221	\N	test	\N
80c35530-a85f-43da-8963-64e90c827c80	bjhb	jhvjh	876876	\N	jhbj	\N
276d33e9-0d69-4ef8-a78b-05842c74ba55	3rd floor Laxminagar	\N	10000	\N	\N	\N
dc81a0d6-d07c-4a76-a483-401964ebf031	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	c47d0e0b-212c-455e-9c54-f16907e8e15b	Birmingham	AL
e90f0ff0-91f1-4caf-8148-34a4bad11396	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	\N	Oklahoma City	\N
ed3ae3b7-c26a-4eb8-a77a-06978d595e90	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73002	\N	Norman	\N
14bed3a1-9859-4b21-ae08-fd20b5ee6611	B-6, Block E, E-59	\N	73001	bcc561d3-b04d-4f80-9878-f644d41016b9	Birmingham	AL
c10d3b19-e86e-4c6c-b5f5-7f3d8249c5d4	Building no. 80, office no. 201, vijay block,	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	\N	Oklahoma City	\N
5db78931-8d17-48f2-8179-f40c9522037b	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	\N	Oklahoma City	\N
f4158df2-0076-4f23-93fe-1aa5cd46e74e	3rd floor Laxminagar	jain uniform , near pillar no. 51, 52 laxmi nagar delhi 92	73001	\N	Noida	\N
\.


--
-- TOC entry 3998 (class 0 OID 16395)
-- Dependencies: 217
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
001
\.


--
-- TOC entry 4002 (class 0 OID 16469)
-- Dependencies: 221
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contacts (id, phone, email, org_id, account_id, name, title) FROM stdin;
791cc04c-78de-4cca-896e-3907f5456940	+1 7404664714	info@softication.com	fd275679-7bd0-4320-be81-3fff79721974	\N	\N	\N
6e081bb0-64ce-4777-bd34-4447c5b5cab7	+1 74046647156	info@softicationht.in	299cfc3a-9791-4379-9602-9123d9e3043b	\N	\N	\N
69db28a6-09a8-4f1c-8adc-897144f68fe1	9879879872	jsdhbj@gmail.com	299cfc3a-9791-4379-9602-9123d9e3043b	44a94d02-7a6c-4ecb-a26c-1a7243dc1425	9769879871	\N
94e5c8db-12c3-4a92-b09c-e43200715173	+18987987989	test@gmail.com	299cfc3a-9791-4379-9602-9123d9e3043b	44a94d02-7a6c-4ecb-a26c-1a7243dc1425	test	test
174bee63-6a31-4d2f-b417-b31983dfb21a	7629374824	jhvxdj@gmail.com	299cfc3a-9791-4379-9602-9123d9e3043b	700b5f8f-b44c-45bb-aab1-7027190cbe51	8768877262	\N
a89b69f2-2c3b-4f34-bb4c-74aa40b6bff8	+17868768768	info@softication.com	299cfc3a-9791-4379-9602-9123d9e3043b	03bb5220-b667-492f-82cd-3ef3d1b44691	test 01	\N
07e3d012-8d05-4904-a11f-3f74df20d48e	+17987987989	testq@gmail.com	299cfc3a-9791-4379-9602-9123d9e3043b	03bb5220-b667-492f-82cd-3ef3d1b44691	test	test
7d5d81d7-0c7a-46c9-b923-54a8f954e608	+1 29837982723	info@softication.com	c47d0e0b-212c-455e-9c54-f16907e8e15b	\N	\N	\N
5f9de8c4-bfe9-46ee-9b9d-efe72c6a6f19	+18768777687	info@ars.com	c47d0e0b-212c-455e-9c54-f16907e8e15b	9a5d52c4-4958-4f10-b306-2dde268e782b	Rishabh Singh	\N
89d6fa23-0ded-44bf-b443-995ff85d4d25	+18768777623	info@aars.com	c47d0e0b-212c-455e-9c54-f16907e8e15b	6fecce56-ac8f-48e8-b478-bd65b187e8ef	Rishabh Singh	\N
4272a52b-ba41-4eac-913b-a2af9b1f2892	+18787236122	test2@gmail.com	c47d0e0b-212c-455e-9c54-f16907e8e15b	9a5d52c4-4958-4f10-b306-2dde268e782b	test 2	test 2
622256f2-2b2a-4b59-9969-b5ab7f86e4eb	+1 7404664714	sales@samplizy.com	bcc561d3-b04d-4f80-9878-f644d41016b9	\N	\N	\N
45bdb0b2-acf1-4c95-aa8a-16a0b3600083	+91-7404664714	sales@softication.com	bcc561d3-b04d-4f80-9878-f644d41016b9	be9293ff-db94-4a76-81cb-bea3671e57e7	Rishabh Singh	\N
c69a1511-65e0-4bb4-ab3e-41a060b30685	+917404664714	sales434@softication.com	bcc561d3-b04d-4f80-9878-f644d41016b9	78c5f5cd-0e38-4288-98db-b15a72dc5a53	Rishabh Singh	\N
a1a8e2ec-6b92-456a-9f2f-2355ca0de2a2	+18787878882	infoassa@softication.com	bcc561d3-b04d-4f80-9878-f644d41016b9	a0298d91-b408-45bc-b9e4-88a9f8134c76	Rishabh Singh	\N
\.


--
-- TOC entry 4005 (class 0 OID 16568)
-- Dependencies: 224
-- Data for Name: formbricks_projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.formbricks_projects (id, project_id, dev_env_id, prod_env_id, organization_id) FROM stdin;
\.


--
-- TOC entry 4003 (class 0 OID 16495)
-- Dependencies: 222
-- Data for Name: invites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.invites (id, org_id, role, email, invited_by, token, status, expires_at, created_at) FROM stdin;
\.


--
-- TOC entry 4008 (class 0 OID 24605)
-- Dependencies: 227
-- Data for Name: opportunities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.opportunities (id, org_id, created_by, project_name, client_name, description, stage, risk_level, project_value, currency, my_role, team_size, expected_rfp_date, deadline, state, market_sector, match_score, created_at, updated_at, account_id, custom_id) FROM stdin;
e76e4649-7cd9-41e1-b4d3-211ccce7fcce	bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	Test Metro Expansion Project	LA Metro	A test opportunity for the metro expansion project	lead	low_risk	8500000.00	USD	Project Manager	5	2025-10-14 00:58:11.392034+05:30	2025-10-14 00:58:11.392146+05:30	California	Transportation	85	2025-10-14 00:58:11.392148+05:30	2025-10-13 21:22:53.371304+05:30	78c5f5cd-0e38-4288-98db-b15a72dc5a53	OPP-NY0001
7fefa322-9a3a-4ecc-9f73-f362e3680c7b	bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	Megapolis	SoftiCation Technology	twsrt	lead	\N	565.00	USD	\N	\N	2025-10-14 05:30:00+05:30	\N	test	transportation	\N	2025-10-13 20:52:05.459025+05:30	2025-10-13 21:22:53.371304+05:30	78c5f5cd-0e38-4288-98db-b15a72dc5a53	OPP-NY0003
88928bf0-64c5-46cd-9f1f-0b75f18ce6f8	bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	IT Services & Digital Transformation	SoftiCation Technology	SoftiCation offers comprehensive IT services including digital marketing, web and mobile app development (WordPress, E-Commerce, SaaS, Custom), GenAI, AI/ML, DevOps, UI/UX design, IT consulting, market research platforms, and cloud solutions.	lead	\N	2333.00	USD	\N	\N	2025-10-14 05:30:00+05:30	\N	Noida	Information Technology	\N	2025-10-13 21:32:49.160956+05:30	2025-10-13 21:32:49.160961+05:30	\N	OPP-NY0004
57751e64-e526-47c2-acbc-6863b600e2d8	bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	Digital Web Solutions & Mobile App Development	SoftiCation Technology	Development and implementation of web solutions, e-commerce platforms, WordPress sites, digital marketing strategies, mobile applications, and ERP/CRM systems aimed at boosting businesses and startups.	lead	\N	2344.00	USD	\N	\N	2025-10-14 05:30:00+05:30	\N	Delhi-NCR, India	IT Services; Digital Solutions; Startups	\N	2025-10-13 21:59:04.022912+05:30	2025-10-13 22:57:14.373379+05:30	78c5f5cd-0e38-4288-98db-b15a72dc5a53	OPP-NY0005
b75eb76e-2ef8-4948-a612-0b7d2ca8f2d0	bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	IT Training Programs	DUCAT	IT Training Courses	lead	low_risk	23232.00	USD	\N	\N	2025-10-14 05:30:00+05:30	\N	Noida	IT Training	100	2025-10-14 12:06:46.168616+05:30	2025-10-14 12:06:46.16862+05:30	a0298d91-b408-45bc-b9e4-88a9f8134c76	OPP-NY0006
\.


--
-- TOC entry 4011 (class 0 OID 24837)
-- Dependencies: 230
-- Data for Name: opportunity_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.opportunity_documents (id, opportunity_id, file_name, original_name, file_type, file_size, file_path, category, purpose, description, status, is_available_for_proposal, tags, upload_date, file_url, uploaded_at, updated_at) FROM stdin;
51dcf251-1e12-4385-924d-139fc7327450	b75eb76e-2ef8-4948-a612-0b7d2ca8f2d0	Blue And White Modern Custom Software Development Facebook Ad.jpg	Blue And White Modern Custom Software Development Facebook Ad.jpg	image/jpeg	139837	\N	Technical Drawings	Technical Specification	Uploaded file: Blue And White Modern Custom Software Development Facebook Ad.jpg	uploaded	t	\N	2025-10-18 05:05:18.726341+05:30	\N	2025-10-18 05:05:18.726341+05:30	2025-10-18 05:05:18.726341+05:30
e9c23cfc-425d-4a1f-9c33-f98f2fd4b328	b75eb76e-2ef8-4948-a612-0b7d2ca8f2d0	Creative Lettermark Logo with Intertwined 'PK'.png	Creative Lettermark Logo with Intertwined 'PK'.png	image/png	768070	\N	Images & Photos	Proposal Content	Uploaded file: Creative Lettermark Logo with Intertwined 'PK'.png	uploaded	t	\N	2025-10-18 05:09:41.300205+05:30	\N	2025-10-18 05:09:41.300205+05:30	2025-10-18 05:09:41.300205+05:30
786b7ee6-d896-4c64-9d63-0a77703e6793	e76e4649-7cd9-41e1-b4d3-211ccce7fcce	Creative Lettermark Logo with Intertwined 'PK'.png	Creative Lettermark Logo with Intertwined 'PK'.png	image/png	768070	\N	Technical Drawings	Proposal Content	Uploaded file: Creative Lettermark Logo with Intertwined 'PK'.png	uploaded	t	\N	2025-10-18 05:36:14.001958+05:30	\N	2025-10-18 05:36:14.001958+05:30	2025-10-18 05:36:14.001958+05:30
\.


--
-- TOC entry 4010 (class 0 OID 24792)
-- Dependencies: 229
-- Data for Name: opportunity_overviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.opportunity_overviews (id, opportunity_id, project_description, project_scope, key_metrics, documents_summary, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 4000 (class 0 OID 16436)
-- Dependencies: 219
-- Data for Name: organizations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organizations (id, owner_id, name, address_id, website, contact_id, created_at, formbricks_organization_id, custom_id) FROM stdin;
fd275679-7bd0-4320-be81-3fff79721974	1c6486d8-37bd-439f-8c39-61c35492d4bd	A R Solutions	b6751c62-988a-4edd-bc4b-19cf2367f9f5	https://softication.com/	791cc04c-78de-4cca-896e-3907f5456940	2025-10-11 18:27:57.769409	\N	ORG-NY001
299cfc3a-9791-4379-9602-9123d9e3043b	edbd0834-d830-411b-aad5-a91f711481cf	A R Solutions g tressds	262ae688-7d45-46ad-b4ad-14d7f1f5e1a8	https://hanssports.com/	6e081bb0-64ce-4777-bd34-4447c5b5cab7	2025-10-11 18:56:51.309034	\N	ORG-NY002
c47d0e0b-212c-455e-9c54-f16907e8e15b	4e37368e-8c32-4f38-a593-15558bf38951	Hanssport	dc81a0d6-d07c-4a76-a483-401964ebf031	https://hanssports.com/	7d5d81d7-0c7a-46c9-b923-54a8f954e608	2025-10-12 18:03:48.220927	\N	ORG-NY003
bcc561d3-b04d-4f80-9878-f644d41016b9	a23b40a7-30d3-4e70-8f61-478e43b446ce	Samplizy	14bed3a1-9859-4b21-ae08-fd20b5ee6611	https://samplizy.com	622256f2-2b2a-4b59-9969-b5ab7f86e4eb	2025-10-12 22:36:14.306089	\N	ORG-NY004
\.


--
-- TOC entry 4006 (class 0 OID 16640)
-- Dependencies: 225
-- Data for Name: user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_permissions (userid, accounts, opportunities, proposals) FROM stdin;
\.


--
-- TOC entry 3999 (class 0 OID 16430)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, org_id, role, formbricks_user_id) FROM stdin;
1c6486d8-37bd-439f-8c39-61c35492d4bd	amar@softication.com	fd275679-7bd0-4320-be81-3fff79721974	admin	\N
edbd0834-d830-411b-aad5-a91f711481cf	amar74.soft@gmail.com	299cfc3a-9791-4379-9602-9123d9e3043b	admin	\N
56645cee-1dd5-4935-bbe1-4b8b3d274dad	infoasas@softication.com	\N	vendor	\N
86f2cee1-aa80-453f-b964-1c64c38d0ac9	test11oct@gmail.com	\N	vendor	\N
4e37368e-8c32-4f38-a593-15558bf38951	admin@megapolis.com	c47d0e0b-212c-455e-9c54-f16907e8e15b	admin	\N
a23b40a7-30d3-4e70-8f61-478e43b446ce	test1125oct@gmail.com	bcc561d3-b04d-4f80-9878-f644d41016b9	vendor	\N
\.


--
-- TOC entry 3827 (class 2606 OID 24632)
-- Name: account_documents account_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_documents
    ADD CONSTRAINT account_documents_pkey PRIMARY KEY (id);


--
-- TOC entry 3816 (class 2606 OID 16675)
-- Name: account_notes account_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_notes
    ADD CONSTRAINT account_notes_pkey PRIMARY KEY (id);


--
-- TOC entry 3806 (class 2606 OID 16516)
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 3795 (class 2606 OID 16463)
-- Name: address address_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (id);


--
-- TOC entry 3784 (class 2606 OID 16399)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3798 (class 2606 OID 16474)
-- Name: contacts contact_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- TOC entry 3810 (class 2606 OID 16574)
-- Name: formbricks_projects formbricks_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formbricks_projects
    ADD CONSTRAINT formbricks_projects_pkey PRIMARY KEY (id);


--
-- TOC entry 3801 (class 2606 OID 16501)
-- Name: invites invites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT invites_pkey PRIMARY KEY (id);


--
-- TOC entry 3803 (class 2606 OID 16549)
-- Name: invites invites_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT invites_token_key UNIQUE (token);


--
-- TOC entry 3825 (class 2606 OID 24611)
-- Name: opportunities opportunities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunities
    ADD CONSTRAINT opportunities_pkey PRIMARY KEY (id);


--
-- TOC entry 3833 (class 2606 OID 24847)
-- Name: opportunity_documents opportunity_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunity_documents
    ADD CONSTRAINT opportunity_documents_pkey PRIMARY KEY (id);


--
-- TOC entry 3831 (class 2606 OID 24801)
-- Name: opportunity_overviews opportunity_overviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunity_overviews
    ADD CONSTRAINT opportunity_overviews_pkey PRIMARY KEY (id);


--
-- TOC entry 3793 (class 2606 OID 16443)
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- TOC entry 3814 (class 2606 OID 16646)
-- Name: user_permissions user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (userid);


--
-- TOC entry 3788 (class 2606 OID 16434)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3828 (class 1259 OID 24638)
-- Name: ix_account_documents_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_account_documents_account_id ON public.account_documents USING btree (account_id);


--
-- TOC entry 3829 (class 1259 OID 24639)
-- Name: ix_account_documents_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_account_documents_id ON public.account_documents USING btree (id);


--
-- TOC entry 3817 (class 1259 OID 16681)
-- Name: ix_account_notes_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_account_notes_account_id ON public.account_notes USING btree (account_id);


--
-- TOC entry 3818 (class 1259 OID 16682)
-- Name: ix_account_notes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_account_notes_id ON public.account_notes USING btree (id);


--
-- TOC entry 3807 (class 1259 OID 16527)
-- Name: ix_accounts_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_accounts_account_id ON public.accounts USING btree (account_id);


--
-- TOC entry 3808 (class 1259 OID 24648)
-- Name: ix_accounts_custom_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_accounts_custom_id ON public.accounts USING btree (custom_id);


--
-- TOC entry 3796 (class 1259 OID 16528)
-- Name: ix_address_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_address_id ON public.address USING btree (id);


--
-- TOC entry 3799 (class 1259 OID 16536)
-- Name: ix_contacts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_contacts_id ON public.contacts USING btree (id);


--
-- TOC entry 3811 (class 1259 OID 16575)
-- Name: ix_formbricks_projects_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_formbricks_projects_id ON public.formbricks_projects USING btree (id);


--
-- TOC entry 3804 (class 1259 OID 16547)
-- Name: ix_invites_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_invites_id ON public.invites USING btree (id);


--
-- TOC entry 3819 (class 1259 OID 24640)
-- Name: ix_opportunities_account_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_opportunities_account_id ON public.opportunities USING btree (account_id);


--
-- TOC entry 3820 (class 1259 OID 24622)
-- Name: ix_opportunities_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_opportunities_created_by ON public.opportunities USING btree (created_by);


--
-- TOC entry 3821 (class 1259 OID 24646)
-- Name: ix_opportunities_custom_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_opportunities_custom_id ON public.opportunities USING btree (custom_id);


--
-- TOC entry 3822 (class 1259 OID 24623)
-- Name: ix_opportunities_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_opportunities_id ON public.opportunities USING btree (id);


--
-- TOC entry 3823 (class 1259 OID 24624)
-- Name: ix_opportunities_org_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_opportunities_org_id ON public.opportunities USING btree (org_id);


--
-- TOC entry 3789 (class 1259 OID 24647)
-- Name: ix_organizations_custom_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_organizations_custom_id ON public.organizations USING btree (custom_id);


--
-- TOC entry 3790 (class 1259 OID 16560)
-- Name: ix_organizations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_organizations_id ON public.organizations USING btree (id);


--
-- TOC entry 3791 (class 1259 OID 16583)
-- Name: ix_organizations_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_name ON public.organizations USING btree (name);


--
-- TOC entry 3812 (class 1259 OID 16652)
-- Name: ix_user_permissions_userid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_permissions_userid ON public.user_permissions USING btree (userid);


--
-- TOC entry 3785 (class 1259 OID 16435)
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- TOC entry 3786 (class 1259 OID 16562)
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- TOC entry 3852 (class 2606 OID 24633)
-- Name: account_documents account_documents_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_documents
    ADD CONSTRAINT account_documents_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


--
-- TOC entry 3848 (class 2606 OID 16676)
-- Name: account_notes account_notes_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.account_notes
    ADD CONSTRAINT account_notes_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


--
-- TOC entry 3843 (class 2606 OID 16517)
-- Name: accounts accounts_client_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_client_address_id_fkey FOREIGN KEY (client_address_id) REFERENCES public.address(id);


--
-- TOC entry 3844 (class 2606 OID 16653)
-- Name: accounts accounts_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id);


--
-- TOC entry 3845 (class 2606 OID 16522)
-- Name: accounts accounts_primary_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_primary_contact_id_fkey FOREIGN KEY (primary_contact_id) REFERENCES public.contacts(id);


--
-- TOC entry 3838 (class 2606 OID 16529)
-- Name: address address_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id);


--
-- TOC entry 3839 (class 2606 OID 16663)
-- Name: contacts contacts_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id) ON DELETE CASCADE;


--
-- TOC entry 3840 (class 2606 OID 16658)
-- Name: contacts contacts_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- TOC entry 3846 (class 2606 OID 16578)
-- Name: formbricks_projects formbricks_projects_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.formbricks_projects
    ADD CONSTRAINT formbricks_projects_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3841 (class 2606 OID 16550)
-- Name: invites invites_invited_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT invites_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.users(id);


--
-- TOC entry 3842 (class 2606 OID 16555)
-- Name: invites invites_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invites
    ADD CONSTRAINT invites_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id);


--
-- TOC entry 3849 (class 2606 OID 24641)
-- Name: opportunities opportunities_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunities
    ADD CONSTRAINT opportunities_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id);


--
-- TOC entry 3850 (class 2606 OID 24612)
-- Name: opportunities opportunities_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunities
    ADD CONSTRAINT opportunities_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3851 (class 2606 OID 24617)
-- Name: opportunities opportunities_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunities
    ADD CONSTRAINT opportunities_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id);


--
-- TOC entry 3854 (class 2606 OID 24848)
-- Name: opportunity_documents opportunity_documents_opportunity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunity_documents
    ADD CONSTRAINT opportunity_documents_opportunity_id_fkey FOREIGN KEY (opportunity_id) REFERENCES public.opportunities(id);


--
-- TOC entry 3853 (class 2606 OID 24802)
-- Name: opportunity_overviews opportunity_overviews_opportunity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.opportunity_overviews
    ADD CONSTRAINT opportunity_overviews_opportunity_id_fkey FOREIGN KEY (opportunity_id) REFERENCES public.opportunities(id);


--
-- TOC entry 3835 (class 2606 OID 16485)
-- Name: organizations organizations_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(id);


--
-- TOC entry 3836 (class 2606 OID 16490)
-- Name: organizations organizations_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id);


--
-- TOC entry 3837 (class 2606 OID 16451)
-- Name: organizations organizations_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 3847 (class 2606 OID 16647)
-- Name: user_permissions user_roles_userid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_roles_userid_fkey FOREIGN KEY (userid) REFERENCES public.users(id);


--
-- TOC entry 3834 (class 2606 OID 16563)
-- Name: users users_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_org_id_fkey FOREIGN KEY (org_id) REFERENCES public.organizations(id);


-- Completed on 2025-10-20 08:35:17 IST

--
-- PostgreSQL database dump complete
--

\unrestrict XEG5jO1KldBZC1ke1rm9TTyAenAHtPE22oZDoSwY90oQQF2OCRWkQdEXBSbvxvu

