"""
schemas/
Canonical label definitions for each domain.

This package centralized all section labels used by pipelines and formatters,
eliminating duplicate label definitions and ensuring single source of truth.

Modules:
    education_schema: Labels for education pipeline (definition, key_points, etc.)
    medical_schema: Labels for medical pipeline (conditions, treatments, etc.)
    coding_schema: Labels for coding pipeline (explanation, complexity, etc.)
    general_schema: Labels for general pipeline (answer)

Usage:
    from schemas.education_schema import EDUCATION_LABELS
    sections = parse_sections(text, EDUCATION_LABELS)
"""
