import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from docx import Document

from .parser.customer_request import parse_customer_request
from .parser.supplier_card import parse_supplier_card
from .parser.commercial_terms import parse_commercial_terms
from .models.schemas import ExtractedData, ParsingReport, FieldStatus

app = FastAPI(title="DocParser API")

# Ключевые слова для классификации типа документа
CLASSIFIERS = {
    "customer_request": ["запрос технико-коммерческого предложения", "запрос ткп", "номер закупки"],
    "supplier_card":    ["карточка поставщика"],
    "commercial_terms": ["коммерческие условия и цены", "коммерческие условия"],
}


def classify_document(doc: Document) -> str | None:
    """Определяет тип документа по ключевым словам в первых параграфах."""
    text = " ".join(p.text.lower() for p in doc.paragraphs[:5])
    for doc_type, keywords in CLASSIFIERS.items():
        for kw in keywords:
            if kw in text:
                return doc_type
    return None


def build_report(data: ExtractedData, sources: dict[str, str]) -> ParsingReport:
    """Формирует отчёт: какие поля найдены, какие нет."""
    report = ParsingReport()

    def check(label: str, value, source_key: str):
        source = sources.get(source_key, "")
        if value:
            report.found.append(FieldStatus(field=label, found=True, value=str(value), source=source))
        else:
            report.warnings.append(FieldStatus(field=label, found=False, source=source))

    if data.customer_request:
        cr = data.customer_request
        src = "customer_request"
        check("purchase_name", cr.purchase_name, src)
        check("purchase_number", cr.purchase_number, src)
        check("customer_name", cr.customer_name, src)
        check("deadline", cr.deadline, src)
        check("delivery_place", cr.delivery_place, src)
        check("delivery_term", cr.delivery_term, src)
        check("payment_term", cr.payment_term, src)
        check("warranty", cr.warranty, src)

    if data.supplier_card:
        sc = data.supplier_card
        src = "supplier_card"
        check("supplier_full_name", sc.full_name, src)
        check("supplier_inn", sc.inn, src)
        check("supplier_kpp", sc.kpp, src)
        check("supplier_ogrn", sc.ogrn, src)
        check("supplier_legal_address", sc.legal_address, src)
        check("supplier_bank", sc.bank, src)
        check("supplier_checking_account", sc.checking_account, src)
        check("supplier_bik", sc.bik, src)
        check("supplier_signatory", sc.signatory, src)
        check("supplier_signatory_position", sc.signatory_position, src)

    if data.commercial_terms:
        ct = data.commercial_terms
        src = "commercial_terms"
        check("commercial_total_no_vat", ct.total_without_vat, src)
        check("commercial_total_with_vat", ct.total_with_vat, src)
        check("commercial_vat_rate", ct.vat_rate, src)
        check("commercial_items_count", str(len(ct.items)) if ct.items else None, src)

    return report


@app.get("/api/health")
def health_check():
    """Health-check эндпоинт."""
    return {"status": "ok"}


@app.post("/api/process")
async def process_documents(files: list[UploadFile] = File(...)):
    """
    Принимает DOCX-файлы, классифицирует и парсит их.
    Возвращает извлечённые данные и отчёт об обработке.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Файлы не загружены")

    extracted = ExtractedData()
    sources: dict[str, str] = {}
    errors: list[str] = []

    for upload in files:
        filename = upload.filename or ""

        # Валидация формата
        if not filename.lower().endswith(".docx"):
            raise HTTPException(
                status_code=400,
                detail=f"Файл '{filename}' не является DOCX"
            )

        content = await upload.read()
        try:
            doc = Document(io.BytesIO(content))
        except Exception as e:
            errors.append(f"Не удалось открыть '{filename}': {e}")
            continue

        doc_type = classify_document(doc)

        if doc_type == "customer_request":
            extracted.customer_request = parse_customer_request(doc, filename)
            sources["customer_request"] = filename
        elif doc_type == "supplier_card":
            extracted.supplier_card = parse_supplier_card(doc, filename)
            sources["supplier_card"] = filename
        elif doc_type == "commercial_terms":
            extracted.commercial_terms = parse_commercial_terms(doc, filename)
            sources["commercial_terms"] = filename
        else:
            # Шаблон или неизвестный документ — пропускаем парсинг
            pass

    report = build_report(extracted, sources)
    report.errors.extend(errors)

    return JSONResponse({
        "extracted": extracted.model_dump(),
        "report": report.model_dump(),
    })
