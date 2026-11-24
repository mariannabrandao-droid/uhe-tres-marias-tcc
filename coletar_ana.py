"""Coleta pública ANA ServiceANA. Requer Python 3.10+, sem pacotes adicionais.

Inventário e coordenadas:
    python coletar_ana.py
Todas as séries convencionais das estações encontradas:
    python coletar_ana.py --baixar-series --inicio 1931-01-01
Estações específicas (códigos separados por espaço):
    python coletar_ana.py --codigos 41020002 01845009 --baixar-series

Saídas em dados_ana. O inventário conserva todos os campos fornecidos pela ANA,
incluindo coordenadas quando preenchidas no cadastro. As séries são preservadas
em XML e CSV no formato de registros da API, que pode conter colunas por dia
dentro de cada mês. A conversão em série diária é uma etapa posterior.

Fonte e contrato de parâmetros consultados em 06/11/2026:
https://www.ana.gov.br/telemetria1ws/ServiceANA.asmx?op=HidroInventario
https://www.ana.gov.br/telemetria1ws/ServiceANA.asmx?op=HidroSerieHistorica
"""

import argparse
import csv
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


BASE = "https://www.ana.gov.br/telemetria1ws/ServiceANA.asmx/"
INV_FIELDS = "codEstDE codEstATE tpEst nmEst nmRio codSubBacia codBacia nmMunicipio nmEstado sgResp sgOper telemetrica".split()
KINDS = {"1": "cotas", "2": "chuvas", "3": "vazoes"}


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).casefold()


def local_tag(tag):
    return tag.rsplit("}", 1)[-1]


def records(payload):
    """Reconhece linhas DataSet/DataTable e conteúdo XML escapado."""
    root = ET.fromstring(payload)
    if local_tag(root.tag).lower() == "html":
        raise ValueError("O serviço devolveu HTML, em vez de XML de dados.")
    output = []
    for node in root.iter():
        children = list(node)
        if children and all(not list(c) for c in children):
            values = {local_tag(c.tag): c.text or "" for c in children}
            keys = [normalized(k) for k in values]
            if any(k in keys for k in ("codigo", "codestacao", "estacaocodigo")):
                output.append(values)
    if not output and root.text and root.text.strip().startswith("<"):
        return records(root.text.encode("utf-8"))
    faults = [n for n in root.iter() if local_tag(n.tag) in ("Fault", "faultstring")]
    if faults:
        raise ValueError("Falha devolvida pelo serviço ANA.")
    # Esquema vazio do DataSet é uma resposta válida sem registros.
    tags = {local_tag(n.tag) for n in root.iter()}
    if not output and not tags.intersection({"DataSet", "DataTable", "NewDataSet", "diffgram", "DocumentElement"}):
        raise ValueError("XML sem estrutura de dados reconhecida. Consulte o arquivo de resposta.")
    return output


def atomic_write(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def fetch(operation, params, destination, refresh=False):
    if destination.exists() and not refresh:
        content = destination.read_bytes()
        records(content)
        return content
    url = BASE + operation + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "PesquisaAcademica-ANA/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                content = response.read()
            # Guarda respostas inesperadas para diagnóstico sem substituir o cache válido.
            try:
                records(content)
            except (ValueError, ET.ParseError):
                atomic_write(destination.with_suffix(".resposta_invalida.xml"), content)
                raise
            atomic_write(destination, content)
            time.sleep(0.5)
            return content
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def save_csv(path, rows):
    columns = list(dict.fromkeys(k for row in rows for k in row))
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def station_code(row):
    for key, value in row.items():
        if normalized(key) in ("codigo", "codestacao", "estacaocodigo"):
            return str(value).strip().zfill(8)
    raise ValueError("Código da estação ausente no inventário.")


def periods(start, end):
    """Blocos por ano civil, com no máximo 366 dias por chamada."""
    while start <= end:
        finish = min(date(start.year, 12, 31), end)
        yield start, finish
        start = date(start.year + 1, 1, 1)


def run(args):
    if args.inicio > args.fim:
        raise ValueError("A data inicial precisa ser anterior à final.")
    directory = Path(args.saida)
    raw = directory / "xml"
    raw.mkdir(parents=True, exist_ok=True)
    inventory = []
    # As duas grafias evitam depender do tratamento de acentos do servidor.
    queries = args.codigos or ["Três Marias", "Tres Marias"]
    for query in queries:
        params = dict.fromkeys(INV_FIELDS, "")
        if args.codigos:
            params.update(codEstDE=query.zfill(8), codEstATE=query.zfill(8))
        else:
            params["nmEst"] = query
        signature = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]
        content = fetch("HidroInventario", params, raw / f"inventario_{signature}.xml", refresh=True)
        inventory.extend(records(content))
        if not args.codigos and inventory:
            break
    unique = {}
    for row in inventory:
        unique[station_code(row)] = row
    if not unique:
        raise ValueError("Inventário retornou zero estações. Confira as respostas em xml e o serviço ANA.")
    save_csv(directory / "inventario_estacoes.csv", list(unique.values()))
    print(f"Inventário salvo com {len(unique)} estações e todos os campos retornados.")
    if not args.baixar_series:
        print("Para baixar séries, execute novamente com --baixar-series.")
        return
    outcomes = []
    log_path = directory / "situacao_downloads.csv"
    for code in sorted(unique):
        for kind in args.tipos:
            for level in ("1", "2"):
                for start, end in periods(args.inicio, args.fim):
                    filename = f"{code}_{KINDS[kind]}_nivel{level}_{start}_{end}"
                    target = raw / (filename + ".xml")
                    params = {"codEstacao": code, "dataInicio": start.strftime("%d/%m/%Y"), "dataFim": end.strftime("%d/%m/%Y"), "tipoDados": kind, "nivelConsistencia": level}
                    outcome = {"codigo": code, "variavel": KINDS[kind], "nivel": level, "inicio": start.isoformat(), "fim": end.isoformat()}
                    try:
                        content = fetch("HidroSerieHistorica", params, target, refresh=args.atualizar or end.year == date.today().year)
                        rows = records(content)
                        save_csv(directory / (filename + ".csv"), rows)
                        outcome.update(situacao="ok" if rows else "sem_registros", registros=len(rows), erro="")
                    except (urllib.error.URLError, TimeoutError, OSError, ValueError, ET.ParseError) as error:
                        outcome.update(situacao="falha", registros="", erro=str(error))
                    outcomes.append(outcome)
                    save_csv(log_path, outcomes)
                    print(code, KINDS[kind], level, start, outcome["situacao"], flush=True)
    failures = sum(row["situacao"] == "falha" for row in outcomes)
    print(f"Concluído. {failures} requisições com falha. Consulte situacao_downloads.csv.")
    if failures:
        raise SystemExit(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--codigos", nargs="+", help="Códigos ANA. Sem essa opção, pesquisa por nome Três Marias.")
    parser.add_argument("--baixar-series", action="store_true")
    parser.add_argument("--tipos", choices=list(KINDS), nargs="+", default=list(KINDS), help="1 cotas, 2 chuvas, 3 vazões")
    parser.add_argument("--inicio", type=date.fromisoformat, default=date(2020, 1, 1))
    parser.add_argument("--fim", type=date.fromisoformat, default=date.today())
    parser.add_argument("--saida", default="dados_ana")
    parser.add_argument("--atualizar", action="store_true", help="Reconsulta também os arquivos de anos anteriores já baixados.")
    args = parser.parse_args()
    if args.codigos and any(not c.isdecimal() or len(c) > 8 for c in args.codigos):
        parser.error("Use códigos numéricos de até oito dígitos.")
    run(args)


if __name__ == "__main__":
    main()