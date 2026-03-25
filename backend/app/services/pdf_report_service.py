import os
import logging
from datetime import datetime
from pathlib import Path

from app.core.config import Settings
from app.models.candidate_model import Candidate
from app.models.job_model import CompatibilityResult

logger = logging.getLogger(__name__)

class PdfReportService:
    """
    Generates a professional PDF report for a candidate.
    Uses reportlab for PDF generation.
    """
    
    def __init__(self, settings: Settings):
        self._output_dir = Path(settings.REPORT_OUTPUT_DIR)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate(
        self, 
        candidate: Candidate,
        compatibility: CompatibilityResult | None = None,
    ) -> str:
        """Generate PDF and return file path."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table,
                TableStyle, HRFlowable
            )
        except ImportError:
            return await self._fallback_text_report(candidate)
        
        filename = f"report_{candidate.id}.pdf"
        filepath = str(self._output_dir / filename)
        
        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            rightMargin=20*mm, leftMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )  
        
        styles = getSampleStyleSheet()
        black = colors.HexColor("#18181b")
        gray  = colors.HexColor("#71717a")
        light = colors.HexColor("#f4f4f5")
        blue  = colors.HexColor("#185FA5")
        
        h1 = ParagraphStyle("h1", parent=styles["Normal"],
                             fontSize=22, fontName="Helvetica-Bold",
                             textColor=black, spaceAfter=4)
        h2 = ParagraphStyle("h2", parent=styles["Normal"],
                             fontSize=13, fontName="Helvetica-Bold",
                             textColor=black, spaceBefore=12, spaceAfter=4)
        body = ParagraphStyle("body", parent=styles["Normal"],
                               fontSize=10, textColor=black,
                               leading=16, spaceAfter=6)
        small = ParagraphStyle("small", parent=styles["Normal"],
                                fontSize=9, textColor=gray, spaceAfter=4)
        mono = ParagraphStyle("mono", parent=styles["Normal"],
                               fontSize=9, fontName="Courier",
                               textColor=blue, spaceAfter=4)
        
        r = candidate.parsed_resume
        gh = candidate.github_data
        profile = gh.get("profile", {}) if gh else {}
        
        story = []
        
        # Header
        story.append(Paragraph("Developer Intelligence Report", h1))
        story.append(Paragraph(
            f"Generated {datetime.utcnow().strftime('%B %d, %Y')}. . Recruiter Intelligence Platform",
            small
        ))
        story.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceAfter=12))
        
        
        # Candidate info
        story.append(Paragraph("Candidate Profile", h2))
        info_data = [
            ["Name", r.name or " "],
            ["Email", r.email or " "],
            ["Phone", r.phone or " "],
            ["GitHub", r.github_url or " "],
            ["LinkedIn", r.linkedin or " "],
            ["Experience", f"{r.years_of_experience or '?'} years"],
        ]
        info_table = Table(info_data, colWidths=[40*mm, 120*mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), gray),
            ("TEXTCOLOR", (1, 0), (1, -1), black),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, light]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        
        # Skills
        if r.skills:
            story.append(Paragraph("Skills", h2))
            story.append(Paragraph(", ".join(r.skills), mono))
            
        # Developer score
        story.append(Paragraph("Developer Score", h2))
        score_data = [
            ["Overall Score", f"{candidate.developer_score or 0}/100"],
            ["Grade", candidate.score_grade or "–"],
        ]
        score_table = Table(score_data, colWidths=[40*mm, 120*mm])
        score_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("TEXTCOLOR", (0, 0), (0, -1), gray),
            ("TEXTCOLOR", (1, 0), (1, -1), blue),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(score_table)

        # Github stats
        if gh:
            story.append(Paragraph("GitHub Activity", h2))
            gh_data = [
                ["Repositories", str(profile.get("public_repos", 0))],
                ["Followers", str(profile.get("followers", 0))],
                ["Total Stars", str(gh.get("total_stars", 0))],
                ["Total Forks", str(gh.get("total_forks", 0))],
                ["Top Languages", ", ".join(gh.get("top_languages", []))],
                ["Last Active", str(gh.get("last_active", " "))],
            ]
            gh_table = Table(gh_data, colWidths=[40*mm, 120*mm])
            gh_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), gray),
                ("TEXTCOLOR", (1, 0), (1, -1), black),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, light]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(gh_table)
            
        # AI Insight
        if candidate.ai_insight:
            story.append(Paragraph("AI-Generated Insight", h2))
            story.append(Paragraph(candidate.ai_insight, body))
            
        # Job compatibility
        if compatibility:
            story.append(HRFlowable(width="100%", thickness=0.5, color=gray, spaceBefore=10, spaceAfter=10))
            story.append(Paragraph(f"Job Compatibility: {compatibility.job_title}", h2))
            compat_data = [
                ["Compatibility Score", f"{compatibility.score}/100 ({compatibility.match_level})"],
                ["Skill Match", f"{compatibility.skill_match}%"],
                ["Experience Match", f"{compatibility.experience_match}%"],
                ["GitHub Relevance", f"{compatibility.github_relevance}%"],
                ["Language Match", f"{compatibility.language_match}%"],
                ["Matched Skills", ", ".join(compatibility.matched_skills[:8]) or " "],
                ["Missing Skills", ", ".join(compatibility.missing_skills[:8]) or " "],
            ]
            compat_table = Table(compat_data, colWidths=[45*mm, 115*mm])
            compat_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), gray),
                ("TEXTCOLOR", (1, 0), (1, -1), black),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, light]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(compat_table)
            story.append(Spacer(1, 6))
            story.append(Paragraph(compatibility.explanation, body))

        # Experience
        if r.experience:
            story.append(Paragraph("Work Experience", h2))
            for exp in r.experience:
                story.append(Paragraph(
                    f"<b>{exp.role or '?'}</b> at {exp.company or '?'} · {exp.duration or ''}",
                    body
                ))
                if exp.description:
                    story.append(Paragraph(exp.description, small))
                    
        # Footer
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=gray))
        story.append(Paragraph("Recruiter Intelligence Platform · Confidential", small))

        doc.build(story)
        logger.info(f"PDF generated: {filepath}")
        return filepath
         
    async def _fallback_text_report(self, candidate: Candidate) -> str:
        """Plain text fallback if reportlab not installed."""
        filename = f"report_{candidate.id}.txt"
        filepath = str(self._output_dir / filename)
        r = candidate.parsed_resume
        content = f"""DEVELOPER INTELLIGENCE REPORT
Generated: {datetime.utcnow().isoformat()}

CANDIDATE
Name: {r.name or "Unknow"}
Email: {r.email or "Unknown"}
Github: {r.github_url or "Unknown"}
Skills: {", ".join(r.skllis)}

DEVELOPER SCORE: {candidate.developer_score or 0}/100 ({candidate.score_grade or "Unknown"}) 

AI INSIGHT:
{candidate.ai_insight or ''}
"""
        with open(filepath, "w") as f:
            f.write(content)
        return filepath               