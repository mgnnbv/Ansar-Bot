--
-- PostgreSQL database cluster dump
--

-- Started on 2026-03-01 16:55:59

\restrict XZQIYDdgn19hzNBDCZccnHn23ryQz7WGXkUe6vNAuz5YVhg4STP6CFuyrw9URZh

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE librarian;
ALTER ROLE librarian WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:M6srLtz9GmwD6vKPffahGA==$ha/hfOGcr7/GaIK5MV3mivv9jYBeuE32ow6A1F0ZqgU=:5Q+y/vzZDtn/4MP/sJX2dJNSeiiIu6YXU+Pr+i0oS2M=';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:/7RC4a/rHUr6VZMycL4UUA==$AG1OXxc6UdljLO5QRu1DWkecZ8O+eYwjnqqW1au4vpk=:n08IKNAoa5ckpzE3BGwmgp1kwHXZw2NnFRYDmEqzCno=';

--
-- User Configurations
--








\unrestrict XZQIYDdgn19hzNBDCZccnHn23ryQz7WGXkUe6vNAuz5YVhg4STP6CFuyrw9URZh

--
-- Databases
--

--
-- Database "template1" dump
--

\connect template1

--
-- PostgreSQL database dump
--

\restrict I9CRPo1NU7RsKRKA9H4zE8dvEnX28fcaO3EHMGdqH12YGLCbznNJMYAhrPCTBBu

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

-- Started on 2026-03-01 16:55:59

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Completed on 2026-03-01 16:56:00

--
-- PostgreSQL database dump complete
--

\unrestrict I9CRPo1NU7RsKRKA9H4zE8dvEnX28fcaO3EHMGdqH12YGLCbznNJMYAhrPCTBBu

--
-- Database "postgres" dump
--

\connect postgres

--
-- PostgreSQL database dump
--

\restrict Cb33qc34bKBUgm2LtO2zaif4YwiaDDGaDgSNr9GZknKayboEOwPIH8M2IuJ9MWS

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

-- Started on 2026-03-01 16:56:00

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 867 (class 1247 OID 73729)
-- Name: orderstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.orderstatus AS ENUM (
    'NEW',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.orderstatus OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 57345)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 57344)
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_id_seq OWNER TO postgres;

--
-- TOC entry 4944 (class 0 OID 0)
-- Dependencies: 217
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- TOC entry 226 (class 1259 OID 73738)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    product_name character varying(255) NOT NULL,
    product_description text,
    product_info text,
    customer_name character varying(100) NOT NULL,
    customer_phone character varying(20) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    status public.orderstatus NOT NULL,
    notes text,
    product_images text
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 73737)
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- TOC entry 4945 (class 0 OID 0)
-- Dependencies: 225
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- TOC entry 224 (class 1259 OID 57382)
-- Name: product_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_images (
    id integer NOT NULL,
    url character varying NOT NULL,
    product_id integer NOT NULL
);


ALTER TABLE public.product_images OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 57381)
-- Name: product_images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_images_id_seq OWNER TO postgres;

--
-- TOC entry 4946 (class 0 OID 0)
-- Dependencies: 223
-- Name: product_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_images_id_seq OWNED BY public.product_images.id;


--
-- TOC entry 222 (class 1259 OID 57368)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying NOT NULL,
    short_description text,
    additional_info text,
    subcategory_id integer,
    category_id integer
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 57367)
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- TOC entry 4947 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- TOC entry 220 (class 1259 OID 57354)
-- Name: subcategories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subcategories (
    id integer NOT NULL,
    name character varying NOT NULL,
    category_id integer NOT NULL
);


ALTER TABLE public.subcategories OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 57353)
-- Name: subcategories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subcategories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subcategories_id_seq OWNER TO postgres;

--
-- TOC entry 4948 (class 0 OID 0)
-- Dependencies: 219
-- Name: subcategories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subcategories_id_seq OWNED BY public.subcategories.id;


--
-- TOC entry 4765 (class 2604 OID 57348)
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- TOC entry 4769 (class 2604 OID 73741)
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- TOC entry 4768 (class 2604 OID 57385)
-- Name: product_images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_images ALTER COLUMN id SET DEFAULT nextval('public.product_images_id_seq'::regclass);


--
-- TOC entry 4767 (class 2604 OID 57371)
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- TOC entry 4766 (class 2604 OID 57357)
-- Name: subcategories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subcategories ALTER COLUMN id SET DEFAULT nextval('public.subcategories_id_seq'::regclass);


--
-- TOC entry 4930 (class 0 OID 57345)
-- Dependencies: 218
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (id, name) FROM stdin;
4	Столы и стулья
5	Тумбы и комоды
6	Матрасы
7	Шкафы
3	Мягкая мебель
2	Кухонная мебель
1	Спальная мебель
\.


--
-- TOC entry 4938 (class 0 OID 73738)
-- Dependencies: 226
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (id, product_name, product_description, product_info, customer_name, customer_phone, created_at, updated_at, status, notes, product_images) FROM stdin;
\.


--
-- TOC entry 4936 (class 0 OID 57382)
-- Dependencies: 224
-- Data for Name: product_images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_images (id, url, product_id) FROM stdin;
70	AgACAgIAAxkBAAIDq2lNwo9qbVa-ruvS8lcp0GZTKpNlAAIzFmsb8aBoSjkx6Nm5BIbmAQADAgADeQADNgQ	31
74	AgACAgIAAxkBAAICpmlM-hD1hrYjx84BRDXp3-0JYX4MAAJSDGsb8aBoSgHJDxI9EiIyAQADAgADeQADNgQ	29
77	AgACAgIAAxkBAAIFZmlSftT0AAHbGrt9Otk_09cMxMZC9gAC0AtrG0JemUpAnlu_iV5PcgEAAwIAA3cAAzYE	36
78	AgACAgIAAxkBAAIHGGlUEPNjdBesb_RVNmFLXwosNZOKAALeDWsbPZigSuRNKAJE9FRQAQADAgADeQADOAQ	34
\.


--
-- TOC entry 4934 (class 0 OID 57368)
-- Dependencies: 222
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (id, name, short_description, additional_info, subcategory_id, category_id) FROM stdin;
29	Китайский стул	Стул китайский деревянный на 3 ножках	Белый цвет из дерева	\N	4
31	Матрас делофе	Матрас из шелка	200 на 54 см	\N	6
32	xfcbnxhfvxnhmf	dfzbzdfbfb	bzdfgbzsdfbad	\N	6
36	андийский шкаф	шкаф из андийског одерев		\N	7
37	dfthdtrfhdtjy	thdyfthjdyjfthdy	hgdxfghfghgfx	\N	6
34	sfsdvadsfvadfvaf	вапиывапиыпкавиык	asdfvasdfvadfv	\N	6
38	аидьявпи	шнра78еншгса87е76	щопигшщепмасенгсогаес	\N	6
\.


--
-- TOC entry 4932 (class 0 OID 57354)
-- Dependencies: 220
-- Data for Name: subcategories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subcategories (id, name, category_id) FROM stdin;
1	🇷🇺 Российская	1
2	🇹🇷 Турецкая	1
3	Кровати	1
4	📐 Прямая	2
5	🔽 Угловая	2
\.


--
-- TOC entry 4949 (class 0 OID 0)
-- Dependencies: 217
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_id_seq', 7, true);


--
-- TOC entry 4950 (class 0 OID 0)
-- Dependencies: 225
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- TOC entry 4951 (class 0 OID 0)
-- Dependencies: 223
-- Name: product_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_images_id_seq', 78, true);


--
-- TOC entry 4952 (class 0 OID 0)
-- Dependencies: 221
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 38, true);


--
-- TOC entry 4953 (class 0 OID 0)
-- Dependencies: 219
-- Name: subcategories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subcategories_id_seq', 26, true);


--
-- TOC entry 4771 (class 2606 OID 57352)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- TOC entry 4779 (class 2606 OID 73745)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 4777 (class 2606 OID 57389)
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- TOC entry 4775 (class 2606 OID 57375)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4773 (class 2606 OID 57361)
-- Name: subcategories subcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subcategories
    ADD CONSTRAINT subcategories_pkey PRIMARY KEY (id);


--
-- TOC entry 4781 (class 2606 OID 65536)
-- Name: products fk_products_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- TOC entry 4783 (class 2606 OID 57390)
-- Name: product_images product_images_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- TOC entry 4782 (class 2606 OID 57376)
-- Name: products products_subcategory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_subcategory_id_fkey FOREIGN KEY (subcategory_id) REFERENCES public.subcategories(id);


--
-- TOC entry 4780 (class 2606 OID 57362)
-- Name: subcategories subcategories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subcategories
    ADD CONSTRAINT subcategories_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


-- Completed on 2026-03-01 16:56:01

--
-- PostgreSQL database dump complete
--

\unrestrict Cb33qc34bKBUgm2LtO2zaif4YwiaDDGaDgSNr9GZknKayboEOwPIH8M2IuJ9MWS

-- Completed on 2026-03-01 16:56:02

--
-- PostgreSQL database cluster dump complete
--

