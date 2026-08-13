import io
import base64
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import uuid


app = Flask(__name__)


# =========================================================
# FOLDERS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH = os.path.join(
    BASE_DIR,
    "static",
    "hh-goa-template.png"
)


# =========================================================
# FONT
# =========================================================

def get_font(size, bold=False):
    filename = "ARIALBD.TTF" if bold else "ARIAL.TTF"
    font_path = os.path.join(BASE_DIR, "static", "fonts", filename)

    if not os.path.exists(font_path):
        fonts_dir = os.path.join(BASE_DIR, "static", "fonts")
        listing = os.listdir(fonts_dir) if os.path.exists(fonts_dir) else "fonts dir missing"
        raise FileNotFoundError(f"Font not found at {font_path}. Fonts dir contents: {listing}")

    return ImageFont.truetype(font_path, size)
# =========================================================
# CENTER TEXT
# =========================================================

def center_text(draw, text, y, font, fill):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    x = (1024 - text_width) // 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        page="home"
    )


# =========================================================
# GENERATE
# =========================================================

@app.route("/generate", methods=["POST"])
def generate():

    # =====================================================
    # FORM DATA
    # =====================================================

    name = request.form.get(
        "name",
        "BUILDER"
    ).strip()

    role = request.form.get(
        "role",
        "FULL STACK"
    ).strip()

    vibe = request.form.get(
        "vibe",
        "BUILT DIFFERENT"
    ).strip()


    if not name:
        name = "BUILDER"

    if not role:
        role = "FULL STACK"

    if not vibe:
        vibe = "BUILT DIFFERENT"


    # =====================================================
    # PHOTO
    # =====================================================

    photo = request.files.get("photo")

    if not photo or photo.filename == "":
        return "Please upload a photo.", 400


    # =====================================================
    # SAVE UPLOADED PHOTO
    # =====================================================

    try:
        uploaded_image = Image.open(photo.stream).convert("RGB")
    except Exception as e:
        return f"Invalid image file: {e}", 400


    # =====================================================
    # CHECK TEMPLATE
    # =====================================================

    if not os.path.exists(TEMPLATE_PATH):

        return (
            "Template not found. "
            "Put hh-goa-template.png inside static folder."
        ), 500


    # =====================================================
    # LOAD TEMPLATE
    # =====================================================

    card = Image.open(
        TEMPLATE_PATH
    ).convert("RGBA")

    card = card.resize(
        (1024, 1536),
        Image.Resampling.LANCZOS
    )

# =====================================================
# QR CODE
# =====================================================
    
    QR_PATH = os.path.join(
        BASE_DIR,
        "static",
        "qr.png"
    )
    
    if os.path.exists(QR_PATH):
    
        qr = Image.open(QR_PATH).convert("RGBA")
    
        # Size of QR inside square
        qr_size = 180
    
        qr = ImageOps.contain(
            qr,
            (qr_size, qr_size),
            method=Image.Resampling.LANCZOS
        )
    
        # Position of QR square
        # Adjust these if needed
        QR_X = 80
        QR_Y = 1120
    
        card.alpha_composite(
            qr,
            (
                QR_X,
                QR_Y
            )
        )

    # =====================================================
    # PHOTO POSITION
    # =====================================================
    #
    # Large circle below HACKER GOA HOUSE
    #
    # =====================================================

    PHOTO_CENTER_X = 512
    PHOTO_CENTER_Y = 690
    PHOTO_RADIUS = 275


    # =====================================================
    # LOAD USER PHOTO
    # =====================================================

    user_photo = uploaded_image 


    # =====================================================
    # CROP PHOTO
    # =====================================================

    photo_diameter = PHOTO_RADIUS * 2

    user_photo = ImageOps.fit(
        user_photo,
        (
            photo_diameter,
            photo_diameter
        ),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )


    # =====================================================
    # CIRCLE MASK
    # =====================================================

    mask = Image.new(
        "L",
        (
            photo_diameter,
            photo_diameter
        ),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.ellipse(
        (
            0,
            0,
            photo_diameter,
            photo_diameter
        ),
        fill=255
    )


    # =====================================================
    # PHOTO LAYER
    # =====================================================

    photo_layer = Image.new(
        "RGBA",
        card.size,
        (0, 0, 0, 0)
    )

    photo_layer.paste(
        user_photo,
        (
            PHOTO_CENTER_X - PHOTO_RADIUS,
            PHOTO_CENTER_Y - PHOTO_RADIUS
        ),
        mask
    )


    # =====================================================
    # PINK PHOTO BORDER
    # =====================================================

    photo_draw = ImageDraw.Draw(
        photo_layer
    )

    BORDER = 7

    photo_draw.ellipse(
        (
            PHOTO_CENTER_X - PHOTO_RADIUS,
            PHOTO_CENTER_Y - PHOTO_RADIUS,

            PHOTO_CENTER_X + PHOTO_RADIUS,
            PHOTO_CENTER_Y + PHOTO_RADIUS
        ),
        outline="#c91f55",
        width=BORDER
    )


    # =====================================================
    # ADD PHOTO TO CARD
    # =====================================================

    card = Image.alpha_composite(
        card,
        photo_layer
    )


    # =====================================================
    # DRAW TEXT
    # =====================================================

    draw = ImageDraw.Draw(card)


    # =====================================================
    # VIBE
    # =====================================================

    vibe_font = get_font(
        30,
        bold=True
    )

    vibe_text = vibe.upper()

    center_text(
        draw,
        vibe_text,
        997,
        vibe_font,
        "#f5b400"
    )


    # =====================================================
    # NAME
    # =====================================================

    name_font = get_font(
        58,
        bold=True
    )

    name_text = name.upper()

    center_text(
        draw,
        name_text,
        1040,
        name_font,
        "#f5ebd8"
    )


    # =====================================================
    # ROLE LABEL
    # =====================================================

    role_label_font = get_font(
        18,
        bold=True
    )

    draw.text(
        (
            520,
            1150
        ),
        "STACK / ROLE",
        font=role_label_font,
        fill="#008f73"
    )


    # =====================================================
    # ROLE
    # =====================================================

    role_font = get_font(
        18,
        bold=True
    )

    draw.text(
        (
            520,
            1175
        ),
        role,
        font=role_font,
        fill="#f5ebd8"
    )


    # =====================================================
    # QR
    # =====================================================
    #
    # QR intentionally disabled.
    #
    # We will add QR after Vercel deployment.
    #
    # =====================================================


    # =====================================================
    # SAVE FINAL CARD
    # =====================================================

    # ... after card = card.convert("RGB")
    buf = io.BytesIO()
    card.save(buf, "PNG")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")

    return render_template(
        "index.html",
        page="result",
        image_data=img_base64,   # use <img src="data:image/png;base64,{{ image_data }}">
        name=name,
        role=role,
        vibe=vibe
    )

# =========================================================
# GENERATED IMAGE
# =========================================================


