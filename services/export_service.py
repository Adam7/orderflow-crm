"""
Генерация PDF-отчёта по клиентам, заказам и статистике пользователя.

Используется reportlab. Для корректного отображения кириллицы
в проект добавлен шрифт DejaVu Sans (resources/fonts), который
регистрируется при первом вызове генерации отчёта.
"""
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models import Order, ORDER_STATUS_LABELS
from services.stats_service import Stats

BASE_DIR = Path(__file__).resolve().parent.parent
FONT_REGULAR_PATH = BASE_DIR / "resources" / "fonts" / "DejaVuSans.ttf"
FONT_BOLD_PATH = BASE_DIR / "resources" / "fonts" / "DejaVuSans-Bold.ttf"

_FONTS_REGISTERED = False


def _register_fonts() -> tuple[str, str]:
    """Регистрирует шрифты с поддержкой кириллицы. Возвращает имена шрифтов."""
    global _FONTS_REGISTERED
    if FONT_REGULAR_PATH.exists() and FONT_BOLD_PATH.exists():
        if not _FONTS_REGISTERED:
            pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONT_REGULAR_PATH)))
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONT_BOLD_PATH)))
            _FONTS_REGISTERED = True
        return "DejaVuSans", "DejaVuSans-Bold"
    # Фоллбэк: без файлов шрифтов кириллица отображаться не будет
    return "Helvetica", "Helvetica-Bold"


def generate_report_pdf(
    output_path: str,
    business_name: str,
    stats: Stats,
    orders: list[Order],
) -> str:
    """Формирует PDF-файл отчёта и возвращает путь к нему."""
    font_regular, font_bold = _register_fonts()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    title_style = ParagraphStyle(
        "Title", fontName=font_bold, fontSize=18, spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", fontName=font_regular, fontSize=10, textColor=colors.grey, spaceAfter=16
    )
    heading_style = ParagraphStyle(
        "Heading", fontName=font_bold, fontSize=13, spaceBefore=14, spaceAfter=8
    )
    normal_style = ParagraphStyle("Normal", fontName=font_regular, fontSize=10)

    elements = [
        Paragraph(f"Отчёт: {business_name}", title_style),
        Paragraph(
            f"Сформирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style
        ),
        Paragraph("Общая статистика", heading_style),
    ]

    stats_data = [
        ["Всего клиентов", str(stats.total_clients)],
        ["Всего заказов", str(stats.total_orders)],
        ["Выполнено", str(stats.done)],
        ["В работе", str(stats.in_progress)],
        ["Новых", str(stats.new)],
        ["Отменено", str(stats.cancelled)],
        ["Общая сумма", f"{stats.total_amount:,.2f} ₽".replace(",", " ")],
    ]
    stats_table = Table(stats_data, colWidths=[6 * cm, 6 * cm])
    stats_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font_regular),
                ("FONTNAME", (0, 0), (0, -1), font_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(stats_table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Список заказов", heading_style))

    if orders:
        order_rows = [["№", "Клиент", "Заказ", "Статус", "Сумма", "Дата"]]
        for o in orders:
            order_rows.append(
                [
                    str(o.id),
                    o.client.name if o.client else "—",
                    o.title,
                    ORDER_STATUS_LABELS[o.status],
                    f"{o.price:.2f} ₽",
                    o.order_date.strftime("%d.%m.%Y"),
                ]
            )
        orders_table = Table(
            order_rows, colWidths=[1.2 * cm, 3.5 * cm, 5 * cm, 3 * cm, 2.5 * cm, 2.3 * cm]
        )
        orders_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_regular),
                    ("FONTNAME", (0, 0), (-1, 0), font_bold),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(orders_table)
    else:
        elements.append(Paragraph("Заказов пока нет.", normal_style))

    doc.build(elements)
    return output_path
