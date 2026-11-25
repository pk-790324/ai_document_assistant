
import fitz

class DocumentProcessingError(Exception):
    """Raised when document extraction fails."""


class DocumentExtractor:
    """
    Extract text from PDF and TXT documents.
    """

    def extract_text(
        self,
        content: bytes,
        file_type: str
    ) -> str:

        if file_type == ".pdf":
            return self._extract_pdf(content)

        if file_type == ".txt":
            return self._extract_txt(content)

        raise DocumentProcessingError(
            f"Unsupported file type: {file_type}"
        )

    def _extract_pdf(self, content: bytes) -> str:
        try:
            with fitz.open(
                stream=content,
                filetype="pdf"
            ) as pdf:

                if pdf.is_encrypted:
                    raise DocumentProcessingError(
                        "Password-protected PDFs are not supported."
                    )

                pages = []

                for page in pdf:
                    page_text = page.get_text("text").strip()

                    if page_text:
                        pages.append(page_text)

                extracted_text = "\n\n".join(pages)

                if not extracted_text.strip():
                    raise DocumentProcessingError(
                        "No extractable text found in PDF."
                    )

                return extracted_text

        except DocumentProcessingError:
            raise

        except Exception as exc:
            raise DocumentProcessingError(
                "Failed to extract text from PDF."
            ) from exc

    def _extract_txt(self, content: bytes) -> str:
        try:
            text = content.decode("utf-8-sig").strip()

            if not text:
                raise DocumentProcessingError(
                    "TXT document contains no text."
                )

            return text

        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                "Unable to decode TXT file. UTF-8 is required."
            ) from exc
