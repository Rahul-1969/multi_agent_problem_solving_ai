import io
import json
from abc import ABC, abstractmethod
from typing import Callable, Dict
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from backend.models.response_models import CollegeData, CareerRoadmapData, ResumeMatchData, ScholarshipData

class ExporterRegistry:
    def __init__(self):
        self._exporters: Dict[str, 'BaseExporter'] = {}
        
    def register(self, format_name: str, exporter: 'BaseExporter'):
        self._exporters[format_name] = exporter
        
    def get_exporter(self, format_name: str) -> 'BaseExporter':
        exporter = self._exporters.get(format_name.lower())
        if not exporter:
            raise ValueError(f"No exporter found for format: {format_name}")
        return exporter

# Global registry instance
export_registry = ExporterRegistry()

def register_exporter(format_name: str):
    def decorator(cls):
        export_registry.register(format_name, cls())
        return cls
    return decorator

class RendererRegistry:
    def __init__(self):
        self._renderers: Dict[str, Callable] = {}
        
    def register(self, export_type: str, renderer: Callable):
        self._renderers[export_type] = renderer
        
    def get_renderer(self, export_type: str) -> Callable | None:
        return self._renderers.get(export_type)

def export_renderer(export_type: str):
    def decorator(func):
        func._export_type = export_type
        return func
    return decorator

class BaseExporter(ABC):
    @abstractmethod
    def export(self, title: str, data_model: BaseModel, export_type: str) -> bytes:
        pass

@register_exporter("pdf")
class PDFExporter(BaseExporter):
    """Generic Framework for exporting Pydantic models to PDF."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = self.styles['Heading1']
        self.h2_style = self.styles['Heading2']
        self.h3_style = self.styles['Heading3']
        self.body_style = self.styles['Normal']
        self.registry = RendererRegistry()
        self._register_default_renderers()
        
    def _register_default_renderers(self):
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, "_export_type"):
                self.registry.register(method._export_type, method)
        
    def _create_document(self):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        return doc, buffer

    def export(self, title: str, data_model: BaseModel, export_type: str) -> bytes:
        doc, buffer = self._create_document()
        elements = []
        
        # Add Title
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 12))
        
        renderer = self.registry.get_renderer(export_type)
        if renderer:
            renderer(elements, data_model)
        else:
            # Generic fallback renderer
            self._render_generic(elements, data_model.model_dump())
            
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
        
    def _render_generic(self, elements, data_dict: dict, level=2):
        style = self.h2_style if level == 2 else self.h3_style
        for key, value in data_dict.items():
            elements.append(Paragraph(str(key).replace("_", " ").title(), style))
            elements.append(Spacer(1, 6))
            if isinstance(value, dict):
                self._render_generic(elements, value, level+1)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._render_generic(elements, item, level+1)
                    else:
                        elements.append(Paragraph(f"• {str(item)}", self.body_style))
            else:
                elements.append(Paragraph(str(value), self.body_style))
            elements.append(Spacer(1, 12))
            
    @export_renderer("college_comparison")
    def _render_college_comparison(self, elements, data: CollegeData):
        elements.append(Paragraph(f"College Matches for {data.branch or 'Any Branch'} ({data.category or 'Any'} / {data.gender or 'Any'})", self.body_style))
        elements.append(Spacer(1, 12))
        
        all_colleges = data.safe + data.moderate + data.dream
        if not all_colleges:
            elements.append(Paragraph("No colleges found.", self.body_style))
            return
            
        table_data = [["College", "Type", "Rank", "Probability"]]
        for c in all_colleges:
            table_data.append([
                c.college_name,
                c.college_type,
                str(c.closing_rank or "N/A"),
                c.admission_probability
            ])
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        
    @export_renderer("career_roadmap")
    def _render_career_roadmap(self, elements, data: CareerRoadmapData):
        for idx, step in enumerate(data.roadmap_steps):
            elements.append(Paragraph(f"Step {idx+1}: {step.title}", self.h2_style))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(step.description, self.body_style))
            elements.append(Spacer(1, 6))
            if step.skills:
                elements.append(Paragraph(f"Skills: {', '.join(step.skills)}", self.body_style))
            elements.append(Spacer(1, 12))
            
    @export_renderer("resume_match")
    def _render_resume_match(self, elements, data: ResumeMatchData):
        elements.append(Paragraph(f"Overall Match Score: {data.overall_match_score}%", self.h2_style))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Matched Skills", self.h3_style))
        elements.append(Paragraph(", ".join(data.matched_skills) if data.matched_skills else "None", self.body_style))
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Missing Skills", self.h3_style))
        elements.append(Paragraph(", ".join(data.missing_skills) if data.missing_skills else "None", self.body_style))
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Gap Analysis", self.h3_style))
        elements.append(Paragraph(f"Experience: {data.experience_gap or 'No Gap'}", self.body_style))
        elements.append(Paragraph(f"Education: {data.education_gap or 'No Gap'}", self.body_style))
        elements.append(Paragraph(f"Certifications: {data.certification_gap or 'No Gap'}", self.body_style))
        elements.append(Paragraph(f"Projects: {data.project_gap or 'No Gap'}", self.body_style))
        
        if data.gemini_suggestions:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("AI Recommendations", self.h3_style))
            elements.append(Paragraph(data.gemini_suggestions, self.body_style))
            
    @export_renderer("scholarships")
    def _render_scholarships(self, elements, data: ScholarshipData):
        for s in data.scholarships:
            elements.append(Paragraph(s.scholarship_name, self.h2_style))
            elements.append(Paragraph(f"Provider: {s.provider}", self.body_style))
            elements.append(Paragraph(f"Amount: {s.amount}", self.body_style))
            elements.append(Paragraph(f"Deadline: {s.deadline}", self.body_style))
            if s.eligibility_status:
                elements.append(Paragraph(f"Eligibility: {s.eligibility_status}", self.body_style))
            if s.summary:
                elements.append(Paragraph(f"Summary: {s.summary}", self.body_style))
            elements.append(Spacer(1, 12))

@register_exporter("docx")
class DOCXExporter(BaseExporter):
    """Stub for DOCX Exporter"""
    def export(self, title: str, data_model: BaseModel, export_type: str) -> bytes:
        raise NotImplementedError("DOCX export is not yet implemented.")

@register_exporter("csv")
class CSVExporter(BaseExporter):
    """Stub for CSV Exporter"""
    def export(self, title: str, data_model: BaseModel, export_type: str) -> bytes:
        raise NotImplementedError("CSV export is not yet implemented.")

@register_exporter("json")
class JSONExporter(BaseExporter):
    """Implementation for JSON Exporter"""
    def export(self, title: str, data_model: BaseModel, export_type: str) -> bytes:
        data_dict = data_model.model_dump()
        payload = {
            "title": title,
            "export_type": export_type,
            "data": data_dict
        }
        return json.dumps(payload, indent=2).encode('utf-8')

# For backward compatibility with existing codebase
export_service = export_registry.get_exporter("pdf")
