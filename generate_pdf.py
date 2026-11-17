import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
import pymupdf

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Running header on pages 2, 3, 4
        if self._pageNumber > 1:
            self.drawString(42, 755, "VEHICLE MONITOR & FUEL MANAGEMENT SYSTEM")
            self.drawRightString(612 - 42, 755, "SYSTEM ARCHITECTURE & PRODUCT SPECIFICATION")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.7)
            self.line(42, 747, 612 - 42, 747)
            
        # Running footer on all pages
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.7)
        self.line(42, 38, 612 - 42, 38)
        
        self.setFont("Helvetica", 8)
        self.drawString(42, 26, "Confidential — Personal Vehicle Fleet & Precision Fuel Management System")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 42, 26, page_str)
        self.restoreState()

def generate_pdf(filename="Vehicle_Monitor_Specification.pdf"):
    # Page dimensions: letter = 612 x 792 pt
    # Margins: 42 pt left/right, 42 pt top/bottom
    # Usable width: 612 - 84 = 528 pt
    # Usable height: 792 - 84 = 708 pt
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=42,
        rightMargin=42,
        topMargin=42,
        bottomMargin=42
    )
    
    styles = getSampleStyleSheet()
    
    # Premium Palette
    c_primary   = colors.HexColor("#0F172A")  # Deep Navy / Slate 900
    c_secondary = colors.HexColor("#0284C7")  # Sky Blue 600
    c_accent    = colors.HexColor("#0F766E")  # Teal 700
    c_dark      = colors.HexColor("#1E293B")  # Slate 800
    c_muted     = colors.HexColor("#64748B")  # Slate 500
    c_border    = colors.HexColor("#CBD5E1")  # Slate 300
    c_bg_subtle = colors.HexColor("#F8FAFC")  # Slate 50
    c_bg_card   = colors.HexColor("#F1F5F9")  # Slate 100
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=c_primary,
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=8
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=c_muted
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.8,
        leading=13.5,
        textColor=c_accent,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=c_dark,
        spaceAfter=5
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=12,
        textColor=c_dark,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )
    
    table_cell = ParagraphStyle(
        'TCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=c_dark
    )
    
    table_cell_bold = ParagraphStyle(
        'TCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11.2,
        textColor=c_dark
    )
    
    table_hdr = ParagraphStyle(
        'THdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=12,
        textColor=c_dark
    )
    
    story = []
    
    # =========================================================================
    # PAGE 1: TITLE BANNER, CORE PHILOSOPHY, SECTION 1 (REFUELLING STATUSES)
    # =========================================================================
    story.append(Paragraph("VEHICLE MONITOR & FUEL MANAGEMENT SYSTEM", title_style))
    story.append(Paragraph("Product Architecture, Functional Specifications & Relational Data Model", subtitle_style))
    
    meta_text = (
        "<b>Platform:</b> Offline-First React/IndexedDB + On-Device Vision AI + Django REST &nbsp;|&nbsp; "
        "<b>Methodology:</b> Full-Tank Pump Precision &nbsp;|&nbsp; "
        "<b>Architecture Scope:</b> Multi-Vehicle Fleet Management & Data Portability &nbsp;|&nbsp; "
        "<b>Date:</b> November 2026"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=2, spaceAfter=8))
    
    exec_summary_html = (
        "<b>Core Architectural Principle & Recommendation:</b><br/>"
        "Keep <b>fuel monitoring and petrol pump accountability</b> as the primary core purpose of the application. "
        "Treat vehicle documents, scheduled maintenance, and non-fuel operating expenses as integrated supporting modules. "
        "This ensures the system matures into a comprehensive personal fleet management platform without compromising "
        "its rigorous ground-truth tracking of fuel consumption (KM/L), station pump calibration, and trip computer bias."
    )
    exec_table = Table([[Paragraph(exec_summary_html, callout_style)]], colWidths=[528])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('LINELEFT', (0,0), (0,0), 3.5, c_secondary),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 10))
    
    # SECTION 1
    story.append(Paragraph("1. Refuelling Entry Statuses & Verification Workflow", h1_style))
    story.append(Paragraph(
        "A receipt must <b>never be compulsory</b>. The owner must always be able to save a refuelling log even if "
        "they paid cash, misplaced the paper receipt, or simply didn't take a photo. Each entry tracks five independent "
        "verification statuses alongside an automated overall classification.",
        body_style
    ))
    
    status_table_data = [
        [Paragraph("Status Flag", table_hdr), Paragraph("Meaning & Operational Role", table_hdr), Paragraph("System Verification Rule", table_hdr)],
        [
            Paragraph("<b>Receipt attached</b>", table_cell_bold),
            Paragraph("Receipt photo or document has been uploaded.", table_cell),
            Paragraph("<b>Optional.</b> Never blocks saving or calculating consumption.", table_cell)
        ],
        [
            Paragraph("<b>Payment verified</b>", table_cell_bold),
            Paragraph("Payment amount and transaction confirmed.", table_cell),
            Paragraph("Verified automatically (card/SMS/API) or manually checked.", table_cell)
        ],
        [
            Paragraph("<b>Pump info recorded</b>", table_cell_bold),
            Paragraph("Petrol station, branch, and pump nozzle recorded.", table_cell),
            Paragraph("Can be marked <i>unavailable</i> if specific pump number is unknown.", table_cell)
        ],
        [
            Paragraph("<b>Vehicle readings recorded</b>", table_cell_bold),
            Paragraph("Trip KM and instrument cluster indicated KM/L entered.", table_cell),
            Paragraph("Essential for pump vs. cluster accuracy analysis; partial logs permitted.", table_cell)
        ],
        [
            Paragraph("<b>Pending review</b>", table_cell_bold),
            Paragraph("Entry flagged for unresolved data anomalies or review.", table_cell),
            Paragraph("Triggered strictly by <b>actual issues</b> (payment mismatch, math conflict, outlier readings), <i>never</i> just because a receipt is missing.", table_cell)
        ]
    ]
    t_status = Table(status_table_data, colWidths=[120, 204, 204])
    t_status.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_status)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Overall Status Classification & Offline AI Ingestion:", h2_style))
    story.append(Paragraph(
        "• <font color='#16A34A'><b>Complete:</b></font> Trip KM, Litres, Total Ksh, and Vehicle readings entered without computational conflicts. Receipt presence is purely supplementary.<br/>"
        "• <font color='#D97706'><b>Incomplete:</b></font> Missing non-critical telemetry (e.g., pump nozzle number marked unavailable or cluster KM/L unrecorded). Calculated pump economy remains valid.<br/>"
        "• <font color='#DC2626'><b>Needs Review:</b></font> Activated exclusively by telemetry conflicts: total Ksh &ne; Litres &times; Price/L, odometer rollback detected, or calculated KM/L deviates &gt;35% from benchmark.<br/>"
        "• <font color='#0284C7'><b>100% Offline AI Ingestion:</b></font> Instant phone-side canvas vision analyzer for dispenser displays and M-Pesa/Bank SMS parser populate verification flags with zero cloud latency.",
        bullet_style
    ))
    
    # End of Page 1
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: SECTION 2 (MULTIPLE VEHICLES) & SECTION 3 (DOCUMENTS TRACKER)
    # =========================================================================
    story.append(Paragraph("2. Multiple Vehicle Fleet Management", h1_style))
    story.append(Paragraph(
        "The owner can register and manage multiple vehicles under a single user profile. Every fuel entry, service record, "
        "document, and expense belongs to a specific vehicle foreign key. <b>Switching vehicles dynamically swaps the UI context "
        "and must never mix calculations, averages, or history.</b>",
        body_style
    ))
    
    veh_table_data = [
        [Paragraph("Vehicle Property", table_hdr), Paragraph("Description & Role", table_hdr), Paragraph("Vehicle Property", table_hdr), Paragraph("Description & Role", table_hdr)],
        [
            Paragraph("<b>Registration No.</b>", table_cell_bold), Paragraph("Unique plate (e.g., KCX 123A)", table_cell),
            Paragraph("<b>Fuel Benchmark</b>", table_cell_bold), Paragraph("Baseline KM/L for anomaly detection", table_cell)
        ],
        [
            Paragraph("<b>Make & Model</b>", table_cell_bold), Paragraph("e.g., Toyota Axio, Mazda Demio", table_cell),
            Paragraph("<b>Fuel History</b>", table_cell_bold), Paragraph("Independent chronological logs", table_cell)
        ],
        [
            Paragraph("<b>Year of Manufacture</b>", table_cell_bold), Paragraph("Vehicle production year", table_cell),
            Paragraph("<b>Station Comparison</b>", table_cell_bold), Paragraph("Brand & nozzle rankings per car", table_cell)
        ],
        [
            Paragraph("<b>Fuel Type</b>", table_cell_bold), Paragraph("Petrol, Diesel, Hybrid, Electric", table_cell),
            Paragraph("<b>Service History</b>", table_cell_bold), Paragraph("Scoped maintenance records", table_cell)
        ],
        [
            Paragraph("<b>Engine Capacity</b>", table_cell_bold), Paragraph("Displacement (e.g., 1500cc)", table_cell),
            Paragraph("<b>Document Vault</b>", table_cell_bold), Paragraph("Vehicle compliance certificates", table_cell)
        ],
        [
            Paragraph("<b>Current Odometer</b>", table_cell_bold), Paragraph("Latest verified mileage (KM)", table_cell),
            Paragraph("<b>Active Context</b>", table_cell_bold), Paragraph("Persisted selection across sessions", table_cell)
        ]
    ]
    t_veh = Table(veh_table_data, colWidths=[105, 159, 105, 159])
    t_veh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_veh)
    story.append(Spacer(1, 6))
    
    # Switcher representation
    switcher_html = (
        "<b>SIDEBAR & DASHBOARD VEHICLE SELECTOR</b><br/>"
        "<b>Currently Active:</b> &nbsp; <font color='#16A34A'><b>[ ACTIVE ]</b></font> "
        "<b>Toyota Axio — KCX 123A</b> &nbsp;|&nbsp; Petrol &middot; 1500cc &nbsp;|&nbsp; Odo: 158,891 KM &nbsp;|&nbsp; Benchmark: 17.5 KM/L<br/>"
        "<font color='#0284C7'><b>[ SWITCH VEHICLE ]</b></font> &nbsp;&bull;&nbsp; "
        "Toyota Fielder — KDA 456B (1800cc) &nbsp;&bull;&nbsp; Mazda Demio — KCB 789C (1300cc) &nbsp;&bull;&nbsp; <i>+ Register New Vehicle</i><br/>"
        "<font color='#64748B' size=7.5><i>Architecture Mandate: Selection changes state globally across all modules (Dashboard, Fuel Logs, Service, Documents, Expenses).</i></font>"
    )
    sel_table = Table([[Paragraph(switcher_html, callout_style)]], colWidths=[528])
    sel_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_card),
        ('BOX', (0,0), (-1,-1), 0.8, c_secondary),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sel_table)
    story.append(Spacer(1, 10))
    
    # SECTION 3
    story.append(Paragraph("3. Licence, Insurance & Vehicle Document Tracker", h1_style))
    story.append(Paragraph(
        "A strict boundary is maintained between <b>Owner-level credentials</b> and <b>Vehicle-level compliance documents</b>. "
        "The driving licence attaches to the owner account, whereas insurance and vehicle inspection certificates link directly to the specific vehicle.",
        body_style
    ))
    
    doc_table_data = [
        [Paragraph("Document Type", table_hdr), Paragraph("Scope & Ownership", table_hdr), Paragraph("Information Captured & Artifacts", table_hdr)],
        [
            Paragraph("<b>Driving Licence</b>", table_cell_bold),
            Paragraph("Owner / Account Level", table_cell),
            Paragraph("Licence number, issue date, expiry date, driver photo/PDF scan upload.", table_cell)
        ],
        [
            Paragraph("<b>Insurance Policy</b>", table_cell_bold),
            Paragraph("Vehicle Specific", table_cell),
            Paragraph("Underwriter/provider, policy number, start date, expiry date, digital certificate.", table_cell)
        ],
        [
            Paragraph("<b>Inspection Certificate</b>", table_cell_bold),
            Paragraph("Vehicle Specific", table_cell),
            Paragraph("Inspection center, certificate number, test date, expiry date, inspection sticker/doc.", table_cell)
        ],
        [
            Paragraph("<b>Other Compliance Docs</b>", table_cell_bold),
            Paragraph("Owner or Vehicle Specific", table_cell),
            Paragraph("Logbook/title copy, commercial PSV badge, parking permits, road-toll passes, dates.", table_cell)
        ]
    ]
    t_doc = Table(doc_table_data, colWidths=[120, 120, 288])
    t_doc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_doc)
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("Automated Expiry Countdown & Notification Cadence:", h2_style))
    story.append(Paragraph(
        "• <b>30 Days Before:</b> Advance renewal planning alert (permits booking inspection test or securing insurance renewal quotes).<br/>"
        "• <b>14 Days Before:</b> Priority renewal warning; prompt to verify paperwork and initiate payment.<br/>"
        "• <b>7 Days Before:</b> Critical countdown alert prominently pinned to the top of the vehicle dashboard.<br/>"
        "• <b>On Expiry Date:</b> Urgent action notification; flags vehicle as legally unroadworthy.<br/>"
        "• <b>Overdue Notifications:</b> Persistent red banner and daily escalation notifications until updated document is recorded.<br/>"
        "• <i>Notification Engine:</i> Executes offline via browser Service Worker and local alerts; syncs via push when online.",
        bullet_style
    ))
    
    # End of Page 2
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: SECTION 4 (MAINTENANCE TRACKER) & SECTION 5 (EXPENSES & TCO)
    # =========================================================================
    story.append(Paragraph("4. Vehicle Service & Maintenance Tracker", h1_style))
    story.append(Paragraph(
        "Each vehicle maintains an independent, chronological service history. The maintenance engine tracks component longevity, "
        "separates labour from parts expenditure, and calculates accurate maintenance cost per kilometer.",
        body_style
    ))
    
    maint_table_data = [
        [Paragraph("Service Attribute", table_hdr), Paragraph("Purpose & Format", table_hdr), Paragraph("Service Attribute", table_hdr), Paragraph("Purpose & Format", table_hdr)],
        [
            Paragraph("<b>Service Date</b>", table_cell_bold), Paragraph("Date maintenance performed", table_cell),
            Paragraph("<b>Parts Replaced</b>", table_cell_bold), Paragraph("Detailed component & part numbers", table_cell)
        ],
        [
            Paragraph("<b>Odometer Reading</b>", table_cell_bold), Paragraph("Exact mileage at service (KM)", table_cell),
            Paragraph("<b>Labour Cost</b>", table_cell_bold), Paragraph("Mechanic / technician labour (Ksh)", table_cell)
        ],
        [
            Paragraph("<b>Service Type</b>", table_cell_bold), Paragraph("Scheduled, preventative, repair", table_cell),
            Paragraph("<b>Parts Cost</b>", table_cell_bold), Paragraph("Total spares expenditure (Ksh)", table_cell)
        ],
        [
            Paragraph("<b>Garage / Mechanic</b>", table_cell_bold), Paragraph("Workshop name and location", table_cell),
            Paragraph("<b>Total Cost & Invoice</b>", table_cell_bold), Paragraph("Computed total + receipt image (opt)", table_cell)
        ]
    ]
    t_maint = Table(maint_table_data, colWidths=[105, 159, 105, 159])
    t_maint.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_maint)
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("<b>Standard Service Categories:</b>", h2_style))
    cats_text = (
        "1. Engine oil & filter &nbsp;|&nbsp; 2. Air filter &nbsp;|&nbsp; 3. Fuel filter &nbsp;|&nbsp; "
        "4. Brake pads & discs &nbsp;|&nbsp; 5. Tyres & wheel alignment &nbsp;|&nbsp; 6. Battery &nbsp;|&nbsp; "
        "7. Engine coolant &nbsp;|&nbsp; 8. Transmission fluid (CVT/ATF) &nbsp;|&nbsp; 9. Spark plugs &nbsp;|&nbsp; "
        "10. Suspension & steering &nbsp;|&nbsp; 11. General inspection & other repairs."
    )
    story.append(Paragraph(cats_text, body_style))
    
    story.append(Paragraph("Intelligent Dual-Threshold Reminders (Mileage vs. Calendar):", h2_style))
    story.append(Paragraph(
        "Reminders trigger dynamically based on <b>mileage threshold OR elapsed calendar date</b>, whichever occurs first:<br/>"
        "• <i>Dynamic Distance Evaluation:</i> When a new fuel log updates the odometer, future service due points (e.g., Oil change at 85,000 KM) are recalculated automatically.<br/>"
        "• <i>Calendar Failsafe:</i> Low-mileage vehicles trigger scheduled service warnings based on elapsed months (e.g., 6 months elapsed since last service), regardless of mileage.<br/>"
        "• <i>Vehicle-Specific OEM Rules:</i> Threshold intervals are fully configurable per vehicle to match manufacturer service manuals.",
        bullet_style
    ))
    story.append(Spacer(1, 8))
    
    # SECTION 5
    story.append(Paragraph("5. Vehicle Expenses & Total Cost of Ownership (TCO)", h1_style))
    story.append(Paragraph(
        "Non-fuel operating expenditures are logged independently from fuel receipts. This isolation ensures that fuel economy (KM/L) "
        "remains mathematically pure while giving the owner complete visibility into the true cost of operating each vehicle.",
        body_style
    ))
    
    exp_table_data = [
        [Paragraph("Cost Pillar", table_hdr), Paragraph("Tracked Items & Examples", table_hdr), Paragraph("Calculated Financial & Efficiency Metrics", table_hdr)],
        [
            Paragraph("<b>Fuel Expenditure</b>", table_cell_bold),
            Paragraph("Full-tank pump refuellings (Fuel Module)", table_cell),
            Paragraph("<b>Fuel Cost / KM:</b> Total Fuel Spend &divide; Tracked Distance (Ksh/KM)", table_cell)
        ],
        [
            Paragraph("<b>Service & Repairs</b>", table_cell_bold),
            Paragraph("Routine maintenance, spares, fluids, labour", table_cell),
            Paragraph("<b>Maintenance Cost / KM:</b> Total Service Spend &divide; Distance (Ksh/KM)", table_cell)
        ],
        [
            Paragraph("<b>Fixed Ownership Costs</b>", table_cell_bold),
            Paragraph("Annual comprehensive insurance, inspection", table_cell),
            Paragraph("<b>Monthly Fixed OpEx:</b> (Annual Policy & Compliance Fees &divide; 12)", table_cell)
        ],
        [
            Paragraph("<b>Incidental Operational Costs</b>", table_cell_bold),
            Paragraph("Parking fees, highway tolls, car washing", table_cell),
            Paragraph("<b>Monthly Incidentals:</b> Sum of all daily operational receipts", table_cell)
        ],
        [
            Paragraph("<b>Total Cost of Ownership</b>", table_cell_bold),
            Paragraph("Holistic aggregate of all 4 cost pillars above", table_cell),
            Paragraph("<b>True Cost / KM:</b> Total Cumulative Expenditure &divide; Total Distance", table_cell)
        ]
    ]
    t_exp = Table(exp_table_data, colWidths=[120, 180, 228])
    t_exp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_exp)
    
    # End of Page 3
    story.append(PageBreak())
    
    # =========================================================================
    # PAGE 4: SECTION 6 (APP STRUCTURE) & SECTION 7 (DATABASE & ARCHITECTURE)
    # =========================================================================
    story.append(Paragraph("6. Recommended Application Information Architecture", h1_style))
    story.append(Paragraph(
        "The application is structured into 8 modular views designed for high-contrast mobile readability and rapid pump-side data entry.",
        body_style
    ))
    
    nav_table_data = [
        [Paragraph("Module View", table_hdr), Paragraph("Primary Operational Scope & Screen Responsibility", table_hdr)],
        [
            Paragraph("<b>1. Dashboard</b>", table_cell_bold),
            Paragraph("Active vehicle summary, real-time KPI cards (Latest KM/L, Monthly Spend, Service countdown, Document status).", table_cell)
        ],
        [
            Paragraph("<b>2. Fuel Monitoring</b>", table_cell_bold),
            Paragraph("Core refuel logging, full-tank pump calculations, cluster vs. pump accuracy metrics, station/pump performance comparisons.", table_cell)
        ],
        [
            Paragraph("<b>3. My Vehicles</b>", table_cell_bold),
            Paragraph("Vehicle garage: register new cars, edit specifications (engine cc, fuel type, benchmark), switch active vehicle context.", table_cell)
        ],
        [
            Paragraph("<b>4. Maintenance</b>", table_cell_bold),
            Paragraph("Chronological service history, parts/labour cost breakdown, intelligent dual-threshold reminders (mileage/time).", table_cell)
        ],
        [
            Paragraph("<b>5. Documents</b>", table_cell_bold),
            Paragraph("Licence and vehicle compliance vault, automated expiration countdowns, urgent renewal banners, document uploads.", table_cell)
        ],
        [
            Paragraph("<b>6. Expenses</b>", table_cell_bold),
            Paragraph("Non-fuel operating costs (parking, tolls, washing, fines), monthly spending trends, True Cost of Ownership (TCO) analytics.", table_cell)
        ],
        [
            Paragraph("<b>7. Analytics</b>", table_cell_bold),
            Paragraph("Long-term consumption trends, petrol brand efficiency rankings (e.g., Shell vs. Rubis vs. TotalEnergies), cluster optimism rate.", table_cell)
        ],
        [
            Paragraph("<b>8. Backup & Settings</b>", table_cell_bold),
            Paragraph("IndexedDB offline cache management, cloud sync triggers, CSV/Excel export (compatible with legacy sheets), notification preferences.", table_cell)
        ]
    ]
    t_nav = Table(nav_table_data, colWidths=[118, 410])
    t_nav.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_nav)
    story.append(Spacer(1, 6))
    
    # SECTION 7
    story.append(Paragraph("7. Relational Database Entities & System Architecture", h1_style))
    story.append(Paragraph(
        "The system employs an offline-first architecture utilizing <b>React + IndexedDB</b> on the client (ensuring instant "
        "logging at petrol pumps without cellular coverage) syncing seamlessly with a <b>Django REST Framework + PostgreSQL</b> backend.",
        body_style
    ))
    
    db_table_data = [
        [Paragraph("Entity", table_hdr), Paragraph("Scope / Relationship", table_hdr), Paragraph("Core Purpose & Key Attributes", table_hdr)],
        [
            Paragraph("<b>Owner</b>", table_cell_bold), Paragraph("Root Account", table_cell),
            Paragraph("User profile capable of owning multiple registered vehicles and personal documents.", table_cell)
        ],
        [
            Paragraph("<b>Vehicle</b>", table_cell_bold), Paragraph("Belongs to Owner (FK)", table_cell),
            Paragraph("Plate, make, model, year, fuel type, engine cc, benchmark KM/L, current odometer.", table_cell)
        ],
        [
            Paragraph("<b>FuelEntry</b>", table_cell_bold), Paragraph("Belongs to Vehicle (FK)", table_cell),
            Paragraph("Litres, price/L, total Ksh, trip distance, car cluster KM/L, calculated KM/L, cost/KM.", table_cell)
        ],
        [
            Paragraph("<b>FuelEntryStatus</b>", table_cell_bold), Paragraph("1:1 with FuelEntry (FK)", table_cell),
            Paragraph("receipt_attached, payment_verified, pump_info_recorded, review_reason, overall_status.", table_cell)
        ],
        [
            Paragraph("<b>Station & Pump</b>", table_cell_bold), Paragraph("Global / Station FK", table_cell),
            Paragraph("Brand (Shell, Rubis, Total), branch location, pump nozzle historical accuracy index.", table_cell)
        ],
        [
            Paragraph("<b>VehicleService</b>", table_cell_bold), Paragraph("Belongs to Vehicle (FK)", table_cell),
            Paragraph("Service date, odometer reading, service category, labour/parts cost, notes.", table_cell)
        ],
        [
            Paragraph("<b>ServiceReminder</b>", table_cell_bold), Paragraph("Belongs to Vehicle (FK)", table_cell),
            Paragraph("Configured interval rules (due_mileage, due_date, recurring boolean, active state).", table_cell)
        ],
        [
            Paragraph("<b>OwnerDocument</b>", table_cell_bold), Paragraph("Belongs to Owner (FK)", table_cell),
            Paragraph("Driver-specific credentials (e.g., Driving Licence number, dates, photo upload).", table_cell)
        ],
        [
            Paragraph("<b>VehicleDocument</b>", table_cell_bold), Paragraph("Belongs to Vehicle (FK)", table_cell),
            Paragraph("Vehicle-specific compliance (Insurance policy, Inspection certificate, Logbook).", table_cell)
        ],
        [
            Paragraph("<b>VehicleExpense</b>", table_cell_bold), Paragraph("Belongs to Vehicle (FK)", table_cell),
            Paragraph("Non-fuel operating costs (parking, tolls, washing, accessories, fines).", table_cell)
        ],
        [
            Paragraph("<b>Attachment</b>", table_cell_bold), Paragraph("Polymorphic FK", table_cell),
            Paragraph("Optional photos and documents for receipts, service invoices, or policy certificates.", table_cell)
        ],
        [
            Paragraph("<b>Notification</b>", table_cell_bold), Paragraph("Belongs to Owner (FK)", table_cell),
            Paragraph("Scheduled alert queue for document expiries and service intervals.", table_cell)
        ]
    ]
    t_db = Table(db_table_data, colWidths=[100, 118, 310])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_subtle]),
        ('TOPPADDING', (0,0), (-1,-1), 2.4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 6))
    
    rec_html = (
        "<b>Strategic Architecture & Offline AI Integration:</b><br/>"
        "• <b>100% On-Device AI Vision & SMS Engine:</b> Built-in HTML5 Canvas OCR and local regex NLP parse dispenser numbers and M-Pesa receipts on smartphones without network or API costs.<br/>"
        "• <b>Full Data Portability:</b> Download complete vehicle audit reports, digital refuel slips, or raw CSVs at any time.<br/>"
        "• <b>Frictionless Logging:</b> 5-status verification decouples optional receipts from core math, preserving the owner's 158,000+ KM benchmark."
    )
    rec_table = Table([[Paragraph(rec_html, callout_style)]], colWidths=[528])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('LINELEFT', (0,0), (0,0), 3.5, colors.HexColor("#16A34A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(rec_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {filename}")

if __name__ == '__main__':
    generate_pdf()
