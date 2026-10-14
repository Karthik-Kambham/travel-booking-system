
from fpdf import FPDF


def generate_booking_pdf(details: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. TITLE - TRAVEL BOOKING
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "TRAVEL BOOKING", 0, 1, "C")
    pdf.ln(2)

    # 2. BOOKING CONFIRMATION
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Booking Confirmation", 0, 1, "L")
    pdf.ln(3)

    # 3. TABLE HEADER
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)

    pdf.cell(60, 10, " DETAIL", 1, 0, "L", fill=True)
    pdf.cell(0, 10, " INFORMATION", 1, 1, "L", fill=True)

    # 4. BOOKING DETAILS
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)

    for key, value in details.items():
        safe_key = str(key).replace("_", " ").title()

        safe_value = (
            str(value)
            .replace("₹", "Rs. ")
            .replace("\u20b9", "Rs. ")
            .replace("’", "'")
            .replace("–", "-")
            .replace("—", "-")
        )

        pdf.set_fill_color(242, 242, 242)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, f" {safe_key}", 1, 0, "L", fill=True)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f" {safe_value}", 1, 1, "L", fill=True)

    # 5. FOOTER NOTE
    pdf.ln(15)
    pdf.set_font("Arial", "", 8)

    pdf.multi_cell(
        0,
        4,
        "Please check your travel details before departure. "
        "This is a booking summary, not a real transport ticket "
        "or proof of payment."
    )

    # 6. RETURN PDF AS BYTES
    pdf_output = pdf.output()
    return bytes(pdf_output)