import io
import json
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from docx import Document

from .parser.customer_request import parse_customer_request
from .parser.supplier_card import parse_supplier_card
from .parser.commercial_terms import parse_commercial_terms
from .generator.filler import fill_template, fill_price_template
from .models.schemas import ExtractedData, ParsingReport, FieldStatus

app = FastAPI(title="DocParser API")

CLASSIFIERS = {
    "customer_request": ["запрос технико-коммерческого предложения", "запрос ткп", "номер закупки"],
    "supplier_card":    ["карточка поставщика"],
    "commercial_terms": ["коммерческие условия и цены", "коммерческие условия"],
}

TEMPLATE_CLASSIFIERS = {
    "anketa":  ["анкета участника"],
    "zayavka": ["заявка на участие в закупке"],
    "price":   ["предложение о цене договора"],
}

TEMPLATE_OUTPUT_NAMES = {
    "anketa":  "01_Анкета_участника_заполненная.docx",
    "zayavka": "02_Заявка_на_участие_заполненная.docx",
    "price":   "03_Предложение_о_цене_заполненное.docx",
}


def _classify(doc: Document, classifiers: dict[str, list[str]]) -> str | None:
    text = " ".join(p.text.lower() for p in doc.paragraphs[:5])
    for doc_type, keywords in classifiers.items():
        for kw in keywords:
            if kw in text:
                return doc_type
    return None


def _merge_logs(report: ParsingReport, log: dict, template_name: str):
    """Добавляет лог генерации одного шаблона в общий отчёт."""
    for item in log.get("found", []):
        report.found.append(FieldStatus(
            field=item["placeholder"],
            found=True,
            value=item.get("value"),
            source=f"{item['source']} → {template_name}",
        ))
    for item in log.get("warnings", []):
        report.warnings.append(FieldStatus(
            field=item["placeholder"],
            found=False,
            source=f"{item['source']} → {template_name}",
        ))
    for ph in log.get("unmapped", []):
        if ph not in report.unmapped:
            report.unmapped.append(ph)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/process")
async def process_documents(files: list[UploadFile] = File(...)):
    """
    Принимает DOCX-файлы (входные документы + шаблоны).
    Возвращает ZIP с заполненными документами и report.json.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Файлы не загружены")

    extracted = ExtractedData()
    templates: dict[str, tuple[str, bytes]] = {}
    report = ParsingReport()

    # --- Шаг 1: классификация и парсинг ---
    for upload in files:
        filename = upload.filename or ""
        if not filename.lower().endswith(".docx"):
            raise HTTPException(status_code=400, detail=f"Файл '{filename}' не является DOCX")

        content = await upload.read()
        try:
            doc = Document(io.BytesIO(content))
        except Exception as e:
            report.errors.append(f"Не удалось открыть '{filename}': {e}")
            continue

        doc_type = _classify(doc, CLASSIFIERS)
        if doc_type == "customer_request":
            extracted.customer_request = parse_customer_request(doc, filename)
        elif doc_type == "supplier_card":
            extracted.supplier_card = parse_supplier_card(doc, filename)
        elif doc_type == "commercial_terms":
            extracted.commercial_terms = parse_commercial_terms(doc, filename)
        else:
            tmpl_type = _classify(doc, TEMPLATE_CLASSIFIERS)
            if tmpl_type:
                templates[tmpl_type] = (filename, content)

    # --- Шаг 2: генерация ---
    filled: dict[str, bytes] = {}

    for tmpl_type, (orig_name, content) in templates.items():
        try:
            if tmpl_type == "price":
                filled_doc, log = fill_price_template(io.BytesIO(content), extracted)
            else:
                filled_doc, log = fill_template(io.BytesIO(content), extracted)

            _merge_logs(report, log, orig_name)

            buf = io.BytesIO()
            filled_doc.save(buf)
            buf.seek(0)
            filled[TEMPLATE_OUTPUT_NAMES.get(tmpl_type, orig_name)] = buf.read()
        except Exception as e:
            report.errors.append(f"Ошибка генерации '{orig_name}': {e}")

    # --- Шаг 3: ZIP ---
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in filled.items():
            zf.writestr(name, data)
        zf.writestr("report.json", json.dumps(report.model_dump(), ensure_ascii=False, indent=2))

    zip_buf.seek(0)
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=docparser_result.zip"},
    )
