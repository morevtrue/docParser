import { useState, useRef, useCallback } from "react";
import JSZip from "jszip";
import { Upload, X, FileText, Download, RotateCcw, Loader2, CheckCircle, AlertTriangle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// --- Типы ---

interface FieldLog {
  placeholder: string;
  source?: string;
  field?: string;
  value?: string;
}

interface ProcessReport {
  found: FieldLog[];
  warnings: FieldLog[];
  unmapped: string[];
  errors: string[];
}

interface ProcessResult {
  report: ProcessReport;
  zipBlob: Blob;
}

type AppState = "empty" | "loading" | "success" | "error";

// --- Утилиты ---

function isDocx(file: File): boolean {
  return (
    file.name.toLowerCase().endsWith(".docx") ||
    file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  );
}

// --- Компонент зоны загрузки ---

interface DropZoneProps {
  label: string;
  files: File[];
  onAdd: (files: File[]) => void;
  onRemove: (index: number) => void;
  onInvalidFile: () => void;
}

function DropZone({ label, files, onAdd, onRemove, onInvalidFile }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = useCallback(
    (incoming: FileList | null) => {
      if (!incoming) return;
      const valid: File[] = [];
      let hasInvalid = false;
      Array.from(incoming).forEach((f) => {
        if (isDocx(f)) valid.push(f);
        else hasInvalid = true;
      });
      if (hasInvalid) onInvalidFile();
      if (valid.length) onAdd(valid);
    },
    [onAdd, onInvalidFile]
  );

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-foreground">{label}</p>
      <div
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          dragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
        }`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <Upload className="mx-auto h-6 w-6 text-muted-foreground mb-1" />
        <p className="text-xs text-muted-foreground">Перетащите DOCX или нажмите для выбора</p>
        <input
          ref={inputRef}
          type="file"
          accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          multiple
          className="hidden"
          onChange={(e) => { handleFiles(e.target.files); e.target.value = ""; }}
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-1">
          {files.map((f, i) => (
            <li key={i} className="flex items-center justify-between rounded-md border px-3 py-1.5 text-sm">
              <span className="flex items-center gap-2 truncate">
                <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                <span className="truncate">{f.name}</span>
              </span>
              <button
                onClick={(e) => { e.stopPropagation(); onRemove(i); }}
                className="ml-2 shrink-0 text-muted-foreground hover:text-destructive"
                aria-label="Удалить файл"
              >
                <X className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// --- Компонент отчёта ---

function ReportView({ report }: { report: ProcessReport }) {
  return (
    <div className="space-y-4">
      {report.errors.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Ошибки обработки</AlertTitle>
          <AlertDescription>
            <ul className="mt-1 space-y-0.5">
              {report.errors.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {report.warnings.length > 0 && (
        <Alert variant="warning">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Не найдено ({report.warnings.length})</AlertTitle>
          <AlertDescription>
            <ul className="mt-1 space-y-0.5">
              {report.warnings.map((w, i) => (
                <li key={i} className="font-mono text-xs">{w.placeholder}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {report.unmapped.length > 0 && (
        <Alert variant="warning">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Без маппинга ({report.unmapped.length})</AlertTitle>
          <AlertDescription>
            <ul className="mt-1 space-y-0.5">
              {report.unmapped.map((u, i) => (
                <li key={i} className="font-mono text-xs">{u}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {report.found.length > 0 && (
        <Alert variant="success">
          <CheckCircle className="h-4 w-4" />
          <AlertTitle>Заполнено ({report.found.length})</AlertTitle>
          <AlertDescription>
            <ul className="mt-1 space-y-0.5">
              {report.found.map((f, i) => (
                <li key={i} className="flex items-center gap-2 text-xs">
                  <span className="font-mono">{f.placeholder}</span>
                  <span className="text-muted-foreground">←</span>
                  <span>{f.source}{f.field ? `/${f.field}` : ""}</span>
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

// --- Главный компонент ---

export default function App() {
  const [customerFiles, setCustomerFiles] = useState<File[]>([]);
  const [supplierFiles, setSupplierFiles] = useState<File[]>([]);
  const [templateFiles, setTemplateFiles] = useState<File[]>([]);

  const [state, setState] = useState<AppState>("empty");
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [serverError, setServerError] = useState<string>("");
  const [invalidFileDialog, setInvalidFileDialog] = useState(false);

  const totalFiles = customerFiles.length + supplierFiles.length + templateFiles.length;

  const handleProcess = async () => {
    setState("loading");
    setServerError("");

    const formData = new FormData();
    customerFiles.forEach((f) => formData.append("files", f));
    supplierFiles.forEach((f) => formData.append("files", f));
    templateFiles.forEach((f) => formData.append("files", f));

    try {
      const res = await fetch("/api/process", { method: "POST", body: formData });

      if (!res.ok) {
        let msg = `Ошибка сервера: ${res.status}`;
        try {
          const json = await res.json();
          msg = json.detail || json.message || msg;
        } catch {}
        setServerError(msg);
        setState("error");
        return;
      }

      // Ответ — ZIP-архив, report.json внутри архива
      const zipBlob = await res.blob();

      let report: ProcessReport = { found: [], warnings: [], unmapped: [], errors: [] };
      try {
        const zip = await JSZip.loadAsync(zipBlob);
        const reportFile = zip.file("report.json");
        if (reportFile) {
          const text = await reportFile.async("text");
          const raw = JSON.parse(text);
          // Нормализуем формат бэкенда в наш ProcessReport
          report = {
            found: (raw.found || []).map((f: { field: string; value?: string; source?: string }) => ({
              placeholder: f.field,
              value: f.value,
              source: f.source,
            })),
            warnings: (raw.warnings || []).map((w: { field: string; source?: string }) => ({
              placeholder: w.field,
              source: w.source,
            })),
            unmapped: raw.unmapped || [],
            errors: raw.errors || [],
          };
        }
      } catch {
        // Не удалось прочитать отчёт — показываем успех без деталей
      }

      setResult({ report, zipBlob });
      setState("success");
    } catch (e) {
      setServerError("Не удалось подключиться к серверу. Проверьте, что бэкенд запущен.");
      setState("error");
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const url = URL.createObjectURL(result.zipBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "result.zip";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    setCustomerFiles([]);
    setSupplierFiles([]);
    setTemplateFiles([]);
    setResult(null);
    setServerError("");
    setState("empty");
  };

  // --- Рендер ---

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-start py-10 px-4">
      <div className="w-full max-w-2xl space-y-6">
        {/* Заголовок */}
        <div className="text-center space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">DocParser</h1>
          <p className="text-sm text-muted-foreground">Автозаполнение тендерных документов</p>
        </div>

        {/* Форма загрузки */}
        {(state === "empty" || state === "error") && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Загрузка документов</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <DropZone
                label="Документы от заказчика"
                files={customerFiles}
                onAdd={(f) => setCustomerFiles((prev) => [...prev, ...f])}
                onRemove={(i) => setCustomerFiles((prev) => prev.filter((_, idx) => idx !== i))}
                onInvalidFile={() => setInvalidFileDialog(true)}
              />
              <Separator />
              <DropZone
                label="Документы поставщика"
                files={supplierFiles}
                onAdd={(f) => setSupplierFiles((prev) => [...prev, ...f])}
                onRemove={(i) => setSupplierFiles((prev) => prev.filter((_, idx) => idx !== i))}
                onInvalidFile={() => setInvalidFileDialog(true)}
              />
              <Separator />
              <DropZone
                label="Шаблоны"
                files={templateFiles}
                onAdd={(f) => setTemplateFiles((prev) => [...prev, ...f])}
                onRemove={(i) => setTemplateFiles((prev) => prev.filter((_, idx) => idx !== i))}
                onInvalidFile={() => setInvalidFileDialog(true)}
              />

              {state === "error" && serverError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Ошибка</AlertTitle>
                  <AlertDescription>{serverError}</AlertDescription>
                </Alert>
              )}

              <Button
                className="w-full"
                disabled={totalFiles === 0}
                onClick={handleProcess}
              >
                Обработать
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Loading */}
        {state === "loading" && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Обрабатываем документы...</p>
            </CardContent>
          </Card>
        )}

        {/* Success */}
        {state === "success" && result && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Обработка завершена
                </CardTitle>
                <div className="flex gap-2">
                  {result.report.found.length > 0 && (
                    <Badge variant="success">{result.report.found.length} заполнено</Badge>
                  )}
                  {result.report.warnings.length > 0 && (
                    <Badge variant="warning">{result.report.warnings.length} не найдено</Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ReportView report={result.report} />
              <Separator />
              <div className="flex gap-3">
                <Button className="flex-1" onClick={handleDownload}>
                  <Download className="h-4 w-4" />
                  Скачать результат
                </Button>
                <Button variant="outline" onClick={handleReset}>
                  <RotateCcw className="h-4 w-4" />
                  Обработать другие
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Модалка: неверный формат */}
      <Dialog open={invalidFileDialog} onOpenChange={setInvalidFileDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Неправильный формат документа</DialogTitle>
            <DialogDescription>
              Требуется файл в формате DOCX. Пожалуйста, загрузите документ с расширением .docx.
            </DialogDescription>
          </DialogHeader>
          <Button onClick={() => setInvalidFileDialog(false)} className="w-full">
            Загрузить другой документ
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
