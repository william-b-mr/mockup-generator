class CatalogException(Exception):
    def __init__(self, message: str, status_code: int = 400, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

class TemplateNotFoundException(CatalogException):
    def __init__(self, item: str, color: str):
        super().__init__(
            message=f"Template not found for {item} - {color}",
            status_code=404,
            detail="Please check if the template exists in the database"
        )

class LogoProcessingException(CatalogException):
    def __init__(self, detail: str):
        super().__init__(
            message="Failed to process logo",
            status_code=500,
            detail=detail
        )

class N8NWorkflowException(CatalogException):
    def __init__(self, workflow_name: str, detail: str):
        super().__init__(
            message=f"n8n workflow '{workflow_name}' failed",
            status_code=500,
            detail=detail
        )