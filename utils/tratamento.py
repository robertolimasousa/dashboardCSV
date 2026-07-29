import pandas as pd


def ler_csv(arquivo):
    """Lê um CSV tentando diferentes codificações comuns."""
    for encoding in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
        try:
            arquivo.seek(0)
            return pd.read_csv(arquivo, sep=None, engine="python", encoding=encoding)
        except Exception:
            continue
    return None


def preparar_dataframe(df):
    """Normaliza colunas e cria campos derivados de data/hora e tempo."""
    df = df.copy()
    df.columns = df.columns.str.strip()

    unique_columns = []
    counts = {}
    for col in df.columns:
        if col in counts:
            counts[col] += 1
            unique_columns.append(f"{col}_{counts[col]}")
        else:
            counts[col] = 0
            unique_columns.append(col)
    df.columns = unique_columns

    lower_columns = {col.lower(): col for col in df.columns}
    has_data = "data" in lower_columns
    has_hora = "hora" in lower_columns
    has_tempo = "tempo" in lower_columns

    if has_data and has_hora:
        df["data_hora"] = pd.to_datetime(
            df[lower_columns["data"]].astype(str).str.strip()
            + " "
            + df[lower_columns["hora"]].astype(str).str.strip(),
            dayfirst=True,
            errors="coerce",
        )
    elif has_data:
        df["data_hora"] = pd.to_datetime(
            df[lower_columns["data"]].astype(str).str.strip(),
            dayfirst=True,
            errors="coerce",
        )
    elif has_hora:
        df["data_hora"] = pd.to_datetime(
            df[lower_columns["hora"]].astype(str).str.strip(),
            format="%H:%M:%S",
            errors="coerce",
        )

    if has_tempo:
        df[lower_columns["tempo"] + "_timedelta"] = pd.to_timedelta(
            df[lower_columns["tempo"]].astype(str).str.replace(",", "."),
            errors="coerce",
        )

    return df


def encontrar_coluna_por_chaves(df, chaves):
    """Busca a primeira coluna que contenha uma das chaves informadas."""
    for coluna in df.columns:
        coluna_lower = coluna.lower()
        if any(chave in coluna_lower for chave in chaves):
            return coluna
    return None


def converter_minutos(df, coluna):
    """Converte valores textuais ou numéricos de tempo para minutos."""
    if coluna is None:
        return None

    serie = (
        df[coluna]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")[0]
    )

    return pd.to_numeric(serie, errors="coerce")


def calcular_tempos(df):
    """Detecta colunas de tempo e retorna séries de estimado, realizado e total."""
    col_estimativa_tempo = encontrar_coluna_por_chaves(
        df, ["estim", "estimate", "previs"]
    )
    col_tempo_realizado = encontrar_coluna_por_chaves(
        df, ["realiz", "realizado", "real", "efetiv"]
    )
    col_tempo_total = encontrar_coluna_por_chaves(
        df, ["total", "soma", "sum", "durac", "tempo"]
    )

    tempo_estimado = converter_minutos(df, col_estimativa_tempo)
    tempo_realizado = converter_minutos(df, col_tempo_realizado)
    tempo_total = converter_minutos(df, col_tempo_total)

    if tempo_total is None or tempo_total.isna().all():
        if tempo_estimado is not None and tempo_realizado is not None:
            tempo_total = tempo_estimado.add(tempo_realizado, fill_value=0)

    return tempo_estimado, tempo_realizado, tempo_total


def selecionar_colunas_por_categoria(df, categorias):
    colunas = []
    for nome, chaves in categorias.items():
        coluna = encontrar_coluna_por_chaves(df, chaves)
        if coluna is not None and coluna not in colunas:
            colunas.append(coluna)
    return colunas
