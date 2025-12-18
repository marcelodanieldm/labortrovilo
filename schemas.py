"""
Esquemas Pydantic para validación de datos / Pydantic-skemoj por validigo de datumoj
Valida datos antes de insertar en la base de datos / Validigas datumojn antaŭ enmeti en la datumbazon
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class CompanySchema(BaseModel):
    """Esquema para validar datos de Empresa / Skemo por validigi datumojn de Kompanio"""
    # Nombre de la empresa (1-255 caracteres) / Nomo de kompanio (1-255 signoj)
    name: str = Field(..., min_length=1, max_length=255)
    # Puntuación de crecimiento (0-100) / Kreska poentaro (0-100)
    growth_score: Optional[float] = Field(None, ge=0, le=100)
    # Industria / Industrio
    industry: Optional[str] = Field(None, max_length=100)
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Valida que el nombre no esté vacío / Validigas ke la nomo ne estas malplena"""
        if not v or v.strip() == "":
            raise ValueError('Company name cannot be empty')
        return v.strip()
    
    class Config:
        from_attributes = True


class JobSchema(BaseModel):
    """Esquema para validar datos de Trabajo / Skemo por validigi datumojn de Laboro"""
    # Título del trabajo / Titolo de la laboro
    title: str = Field(..., min_length=1, max_length=255)
    # Nombre de la empresa / Nomo de la kompanio
    company_name: str = Field(..., min_length=1, max_length=255)
    # Descripción original / Originala priskribo
    raw_description: Optional[str] = None
    # Stack tecnológico limpio / Purigita teknologia stako
    cleaned_stack: Optional[str] = None
    # Salario mínimo / Minimuma salajro
    salary_min: Optional[float] = Field(None, ge=0)
    # Salario máximo / Maksimuma salajro
    salary_max: Optional[float] = Field(None, ge=0)
    # URL de origen / Fonta URL
    source_url: str = Field(..., min_length=1, max_length=500)
    # Fecha de publicación / Dato de publikigo
    posted_date: Optional[datetime] = None
    
    @field_validator('title', 'company_name')
    @classmethod
    def string_must_not_be_empty(cls, v: str) -> str:
        """Valida que los campos de texto no estén vacíos / Validigas ke tekstaj kampoj ne estas malplenaj"""
        if not v or v.strip() == "":
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @field_validator('source_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Valida que la URL sea correcta / Validigas ke la URL estas ĝusta"""
        if not v or v.strip() == "":
            raise ValueError('URL cannot be empty')
        # Validación básica de URL / Baza validigo de URL
        v = v.strip()
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @field_validator('salary_max')
    @classmethod
    def salary_max_greater_than_min(cls, v: Optional[float], info) -> Optional[float]:
        """Valida que el salario máximo sea mayor que el mínimo / Validigas ke maksimuma salajro estas pli granda ol minimuma"""
        if v is not None and 'salary_min' in info.data:
            salary_min = info.data['salary_min']
            if salary_min is not None and v < salary_min:
                raise ValueError('salary_max must be greater than or equal to salary_min')
        return v
    
    class Config:
        from_attributes = True


class JobCreateSchema(JobSchema):
    """Schema for creating a new job"""
    pass


class CompanyCreateSchema(CompanySchema):
    """Schema for creating a new company"""
    pass
