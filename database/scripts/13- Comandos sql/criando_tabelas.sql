

-- =====================================================
-- 1. APG
-- Cadastro das 17 APGs de Campinas
-- =====================================================

CREATE TABLE apg (
    id_apg INTEGER PRIMARY KEY,
    codigo_apg VARCHAR(40) UNIQUE NOT NULL,
    nome_apg VARCHAR(150) NOT NULL,

    pop_1970 INTEGER,
    pop_1980 INTEGER,
    pop_1991 INTEGER,
    pop_1996 INTEGER,
    pop_2000 INTEGER,
    pop_2010 INTEGER,
    pop_2022 INTEGER,

    geometry_wkt TEXT NOT NULL,

    geometria GEOMETRY(MULTIPOLYGON, 31983)
        GENERATED ALWAYS AS (
            ST_GeomFromText(geometry_wkt, 31983)
        ) STORED
);

-- =====================================================
-- 2. SETOR CENSITARIO
-- Cadastro dos 2.592 setores censitarios
-- =====================================================

CREATE TABLE setor_censitario (
    codigo_setor VARCHAR(15) PRIMARY KEY,
    id_apg INTEGER NOT NULL,

    situacao VARCHAR(50),
    codigo_situacao VARCHAR(10),
    codigo_tipo VARCHAR(10),
    area_km2 NUMERIC(24,15),

    codigo_municipio VARCHAR(7),
    municipio VARCHAR(100),
    codigo_distrito VARCHAR(12),
    distrito VARCHAR(100),

    percentual_area_na_apg NUMERIC(10,6),

    geometry_wkt TEXT NOT NULL,

    geometria GEOMETRY(MULTIPOLYGON, 31983)
        GENERATED ALWAYS AS (
            ST_GeomFromText(geometry_wkt, 31983)
        ) STORED,

    CONSTRAINT fk_setor_apg
        FOREIGN KEY (id_apg)
        REFERENCES apg(id_apg)
);

-- =====================================================
-- 3. DADOS SETOR 2022
-- Dados demograficos e socioeconomicos do IBGE
-- =====================================================

CREATE TABLE dados_setor_2022 (
    codigo_setor VARCHAR(15) PRIMARY KEY,

    populacao_total INTEGER NOT NULL,

    total_domicilios INTEGER,
    domicilios_particulares INTEGER,
    domicilios_coletivos INTEGER,

    media_moradores NUMERIC(10,4),
    percentual_domicilios_imputados NUMERIC(10,6),

    domicilios_particulares_ocupados INTEGER,

    moradores_demografia INTEGER,
    homens_total INTEGER,
    mulheres_total INTEGER,

    homens_60_69 INTEGER,
    homens_70_mais INTEGER,
    mulheres_60_69 INTEGER,
    mulheres_70_mais INTEGER,

    pop_0_4 INTEGER,
    pop_5_9 INTEGER,
    pop_10_14 INTEGER,
    pop_15_19 INTEGER,
    pop_20_24 INTEGER,
    pop_25_29 INTEGER,
    pop_30_39 INTEGER,
    pop_40_49 INTEGER,
    pop_50_59 INTEGER,
    pop_60_69 INTEGER,
    pop_70_mais INTEGER,

    sem_linha_demografica BOOLEAN NOT NULL,
    sem_demografia_pop_zero BOOLEAN NOT NULL,
    revisar_sem_demografia BOOLEAN NOT NULL,
    possui_valor_inibido BOOLEAN NOT NULL,

    pop_60_mais INTEGER,
    homens_60_mais INTEGER,
    mulheres_60_mais INTEGER,

    responsaveis_domicilios_ocupados INTEGER,
    moradores_domicilios_ocupados INTEGER,

    variancia_moradores NUMERIC(20,6),
    renda_media_responsavel NUMERIC(18,2),
    variancia_renda_responsavel NUMERIC(24,6),

    registro_renda_publicado BOOLEAN NOT NULL,

    CONSTRAINT fk_dados_setor
        FOREIGN KEY (codigo_setor)
        REFERENCES setor_censitario(codigo_setor)
);

-- =====================================================
-- 4. PROJECAO POPULACIONAL
-- Projecoes municipais oficiais do SEADE
-- =====================================================

CREATE TABLE projecao_populacional (
    id_projecao BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    cod_ibge VARCHAR(7) NOT NULL,
    ano SMALLINT NOT NULL,
    sexo VARCHAR(20) NOT NULL,
    faixa_etaria VARCHAR(30) NOT NULL,

    populacao INTEGER NOT NULL,
    fonte VARCHAR(150) NOT NULL,

    CONSTRAINT uq_projecao
        UNIQUE (cod_ibge, ano, sexo, faixa_etaria)
);

-- =====================================================
-- 5. PARAMETRO PERFIL DE CUIDADO
-- Parametros calculados a partir da PNS 2019
-- =====================================================

CREATE TABLE parametro_perfil_cuidado (
    id_parametro BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    faixa_etaria VARCHAR(20) NOT NULL,
    sexo VARCHAR(20) NOT NULL,
    perfil_cuidado VARCHAR(40) NOT NULL,

    n_amostra_grupo INTEGER NOT NULL,
    n_amostra_perfil INTEGER NOT NULL,

    peso_expandido_grupo NUMERIC(20,2) NOT NULL,
    peso_expandido_perfil NUMERIC(20,2) NOT NULL,

    proporcao NUMERIC(12,9) NOT NULL,
    percentual NUMERIC(8,4) NOT NULL,

    criterio_perfil TEXT NOT NULL,
    fonte VARCHAR(150) NOT NULL,

    CONSTRAINT uq_parametro
        UNIQUE (faixa_etaria, sexo, perfil_cuidado)
);

-- =====================================================
-- 6. SERVICO PUBLICO
-- Servicos e entidades cadastrados
-- =====================================================

CREATE TABLE servico_publico (
    id_servico BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    chave_servico VARCHAR(32) UNIQUE NOT NULL,

    nome_servico VARCHAR(200) NOT NULL,
    tipo_servico VARCHAR(100) NOT NULL,
    nivel_registro VARCHAR(30) NOT NULL,

    publico_alvo VARCHAR(255),
    cnpj VARCHAR(20),
    endereco VARCHAR(300),
    bairro VARCHAR(150),
    telefone VARCHAR(80),

    id_apg INTEGER,

    fonte VARCHAR(200) NOT NULL,
    pagina_fonte VARCHAR(60),

    review_required BOOLEAN NOT NULL,

    CONSTRAINT fk_servico_apg
        FOREIGN KEY (id_apg)
        REFERENCES apg(id_apg)
);

-- =====================================================
-- 7. INDICADOR PUBLICO
-- Indicadores extraidos de fontes municipais
-- =====================================================

CREATE TABLE indicador_publico (
    id_indicador_publico BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    chave_indicador VARCHAR(32) UNIQUE NOT NULL,
    chave_servico VARCHAR(32),
    id_apg INTEGER,

    origem VARCHAR(30) NOT NULL,
    numero_meta VARCHAR(30),

    nome_indicador VARCHAR(200) NOT NULL,
    descricao TEXT,

    valor NUMERIC(20,6) NOT NULL,
    unidade VARCHAR(50) NOT NULL,

    ano_referencia SMALLINT,
    periodo_referencia VARCHAR(50),

    fonte VARCHAR(200) NOT NULL,
    pagina_fonte VARCHAR(60),
    observacao TEXT,

    review_required BOOLEAN NOT NULL,

    CONSTRAINT fk_indicador_servico
        FOREIGN KEY (chave_servico)
        REFERENCES servico_publico(chave_servico),

    CONSTRAINT fk_indicador_apg
        FOREIGN KEY (id_apg)
        REFERENCES apg(id_apg)
);

-- =====================================================
-- 8. INDICADOR TERRITORIAL
-- Resultados calculados pelo TechCare
-- =====================================================

CREATE TABLE indicador_territorial (
    id_indicador_territorial BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    nivel_territorial VARCHAR(20) NOT NULL,
    id_apg INTEGER,

    ano SMALLINT NOT NULL,
    nome_indicador VARCHAR(100) NOT NULL,

    valor NUMERIC(20,6) NOT NULL,
    unidade VARCHAR(40) NOT NULL,

    fonte_base VARCHAR(255) NOT NULL,
    natureza_valor VARCHAR(100) NOT NULL,
    metodologia TEXT NOT NULL,

    CONSTRAINT fk_indicador_territorial_apg
        FOREIGN KEY (id_apg)
        REFERENCES apg(id_apg),

    CONSTRAINT ck_nivel_territorial
        CHECK (
            (nivel_territorial = 'APG' AND id_apg IS NOT NULL)
            OR
            (nivel_territorial = 'MUNICIPIO' AND id_apg IS NULL)
        ),

    CONSTRAINT uq_indicador_territorial
        UNIQUE NULLS NOT DISTINCT
        (nivel_territorial, id_apg, ano, nome_indicador)
);

-- =====================================================
-- INDICES GEOGRAFICOS
-- Melhoram as consultas espaciais
-- =====================================================

CREATE INDEX idx_apg_geometria
    ON apg USING GIST (geometria);

CREATE INDEX idx_setor_geometria
    ON setor_censitario USING GIST (geometria);

COMMIT;

