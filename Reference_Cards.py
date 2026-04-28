"""Generate poker hand rank reference cards as card-sized images.

Output images are 2.5in x 3.5in at 300 DPI:
- hand_ranks_card_1.png
- hand_ranks_card_2.png
- hand_ranks_card_3.png
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont


DPI = 300
CARD_WIDTH_IN = 2.5
CARD_HEIGHT_IN = 3.5
IMG_W = int(CARD_WIDTH_IN * DPI)
IMG_H = int(CARD_HEIGHT_IN * DPI)

TITLE_TEXT = "Hand Ranks"
SECOND_CARD_TITLE_TEXT = "Tiny Straights"
THIRD_CARD_TITLE_TEXT = "6-Card Hand Ranks"
SUIT_SYMBOLS = {
	"H": "\u2665",
	"D": "\u2666",
	"C": "\u2663",
	"S": "\u2660",
}


@dataclass
class ExampleCard:
	value: str
	suit: str  # H, S, C, D, N
	greyed: bool


@dataclass
class HandRow:
	example: List[ExampleCard]
	name: str
	highlight: bool = False


PROBABILITIES: Dict[str, str] = {
	"High Card": "100%",
	"Pair": "79.0%",
	"Tiny Straight": "54.7%",
	"Two Pair": "26.6%",
	"Tiny Straight House": "23.0%",
	"Small Flush": "22.6%",
	"Small Straight": "18.6%",
	"Three of a Kind": "7.70%",
	"Tiny Straight Flush": "7.02%",
	"Straight": "4.83%",
	"Flush": "3.04%",
	"Full House": "2.63%",
	"Tiny Straight Flush House": "2.05%",
	"Three Pair": "1.90%",
	"Long Straight": "0.93%",
	"Small Straight Flush": "0.56%",
	"Big Flush": "0.20%",
	"Four of a Kind": "0.17%",
	"Longest Straight": "0.10%",
	"Double Triples": "0.04%",
	"Full Hotel": "0.03%",
	"Straight Flush": "0.03%",
	"Five of a Kind": "?.??%",
	"Huge Flush": "0.000%",
	"Long Straight Flush": "0.00%",
	"Fullest House": "0.00%",
	"Longest Straight Flush": "0.00%",
	"Six of a Kind": "?.??%",
}


CARD_1_RAW: Sequence[Tuple[str, str, bool]] = [
	("7N, 7N, 7N, 7N, 7N", "Five of a Kind", False),
	("2S, 3S, 4S, 5S, 6S", "Straight Flush", False),
	("5N, 5N, 5N, 5N, (JN)", "Four of a Kind", False),
	("AN, AN, AN, 7N, 7N", "Full House", False),
	("NH, NH, NH, NH, NH", "Flush", False),
	("2N, 3N, 4N, 5N, 6N", "Straight", False),
	("7N, 7N, 7N, (JN), (2N)", "Three of a Kind", False),
	("KN, KN, 3N, 3N, (JN)", "Two Pair", False),
	("QN, QN, (8N), (7N), (4N)", "Pair", False),
	("AN, (QN), (9N), (5N), (2N)", "High Card", False),
]


CARD_2_RAW: Sequence[Tuple[str, str, bool]] = [
	("7N, 7N, 7N, 7N, 7N", "Five of a Kind", False),
	("2S, 3S, 4S, 5S, 6S", "Straight Flush", False),
	("5N, 5N, 5N, 5N, (JN)", "Four of a Kind", False),
	("4D, 5D, 6D, JN, JN", "Tiny Straight Flush House", True),
	("AN, AN, AN, 7N, 7N", "Full House", False),
	("NH, NH, NH, NH, NH", "Flush", False),
	("2N, 3N, 4N, 5N, 6N", "Straight", False),
	("4D, 5D, 6D, (9C), (JH)", "Tiny Straight Flush", True),
	("7N, 7N, 7N, (JN), (2N)", "Three of a Kind", False),
	("4N, 5N, 6N, QN, QN", "Tiny Straight House", True),
	("KN, KN, 3N, 3N, (JN)", "Two Pair", False),
	("4N, 5N, 6N, (QN), (8N)", "Tiny Straight", True),
	("QN, QN, (8N), (7N), (4N)", "Pair", False),
	("AN, (QN), (9N), (5N), (2N)", "High Card", False),
]

CARD_3_RAW: Sequence[Tuple[str, str, bool]] = [
	("4N, 4N, 4N, 4N, 4N, 4N", "Six of a Kind", True),
	("7N, 7N, 7N, 7N, 7N, (QN)", "Five of a Kind", False),
	("2S, 3S, 4S, 5S, 6S, (9N)", "Straight Flush", False),
	("AN, AN, AN, AN, 3N, 3N", "Full Hotel", True),
	("4N, 4N, 4N, 8N, 8N, 8N", "Double Triples", True),
	("5N, 5N, 5N, 5N, (JN), (2N)", "Four of a Kind", False),
	("ND, ND, ND, ND, ND, ND", "Big Flush", True),
	("AN, 2N, 3N, 4N, 5N, 6N", "Long Straight", True),
	("QN, QN, 7N, 7N, 4N, 4N", "Three Pair", True),
	("AN, AN, AN, 7N, 7N, (KN)", "Full House", False),
	("NH, NH, NH, NH, NH, (NN)", "Flush", False),
	("2N, 3N, 4N, 5N, 6N, (JN)", "Straight", False),
	("7N, 7N, 7N, (JN), (3N), (2N)", "Three of a Kind", False),
	("KN, KN, 3N, 3N, (JN), (4N)", "Two Pair", False),
	("QN, QN, (8N), (7N), (5N), (4N)", "Pair", False),
	("AN, (QN), (9N), (5N), (3N), (2N)", "High Card", False),
]

def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
	candidates = [
		"DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
		"Arial Bold.ttf" if bold else "Arial.ttf",
		"Helvetica.ttc",
	]
	for name in candidates:
		try:
			return ImageFont.truetype(name, size=size)
		except OSError:
			continue
	return ImageFont.load_default()


def parse_example_card(token: str) -> ExampleCard:
	token = token.strip()
	greyed = token.startswith("(") and token.endswith(")")
	if greyed:
		token = token[1:-1].strip()
	if len(token) < 2:
		raise ValueError(f"Invalid card token: {token}")
	value = token[:-1]
	suit = token[-1]
	if suit not in {"H", "S", "C", "D", "N"}:
		raise ValueError(f"Invalid suit in token: {token}")
	return ExampleCard(value=value, suit=suit, greyed=greyed)


def parse_row(example_raw: str, hand_name: str, highlight: bool) -> HandRow:
	cards = [parse_example_card(piece) for piece in example_raw.split(",")]
	return HandRow(example=cards, name=hand_name, highlight=highlight)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
	bbox = draw.textbbox((0, 0), text, font=font)
	return bbox[2] - bbox[0], bbox[3] - bbox[1]


def suit_color(suit: str, greyed: bool) -> Tuple[int, int, int]:
	if greyed:
		return (165, 165, 165)
	if suit in {"H", "D"}:
		return (188, 28, 28)
	if suit in {"S", "C"}:
		return (35, 35, 35)
	return (90, 90, 90)


def draw_example_card(
	draw: ImageDraw.ImageDraw,
	x: int,
	y: int,
	w: int,
	h: int,
	card: ExampleCard,
	value_font: ImageFont.ImageFont,
	suit_font: ImageFont.ImageFont,
	center_suit_font: ImageFont.ImageFont,
	center_value_font: ImageFont.ImageFont,
) -> None:
	if card.greyed:
		face = (242, 242, 242)
		border = (185, 185, 185)
	else:
		face = (255, 255, 255)
		border = (110, 110, 110)

	draw.rounded_rectangle((x, y, x + w, y + h), radius=max(2, w // 8), fill=face, outline=border, width=1)

	color = suit_color(card.suit, card.greyed)
	value_text = "" if card.value == "N" else card.value
	if card.suit == "N" and value_text != "":
		center_value_bbox = draw.textbbox((0, 0), value_text, font=center_value_font)
		center_value_w = center_value_bbox[2] - center_value_bbox[0]
		tx = x + (w - center_value_w) // 2
		ty = y + (h - (center_value_bbox[3] - center_value_bbox[1])) // 2 - center_value_bbox[1]
		draw.text((tx, ty), value_text, font=center_value_font, fill=color)
		return

	value_bbox = draw.textbbox((0, 0), value_text, font=value_font)
	tw = value_bbox[2] - value_bbox[0]
	tx = x + (w - tw) // 2
	content_top = y + 2
	content_bottom = y + h - 3
	ty = content_top
	draw.text((tx, ty), value_text, font=value_font, fill=color)

	if card.suit != "N":
		symbol = SUIT_SYMBOLS[card.suit]
		if value_text == "":
			bbox = draw.textbbox((0, 0), symbol, font=center_suit_font)
			sw = bbox[2] - bbox[0]
			sx = x + (w - sw) // 2
			sy = y + (h - (bbox[3] - bbox[1])) // 2 - bbox[1]
			draw.text((sx, sy), symbol, font=center_suit_font, fill=color)
			return

		bbox = draw.textbbox((0, 0), symbol, font=suit_font)
		sw = bbox[2] - bbox[0]
		sx = x + (w - sw) // 2
		sy = content_top
		value_bottom = ty + value_bbox[3]
		min_gap = 10
		sy = value_bottom + min_gap - bbox[1]
		max_sy = content_bottom - bbox[3]
		if sy > max_sy:
			sy = max_sy
		draw.text((sx, sy), symbol, font=suit_font, fill=color)


def build_rows(raw_rows: Sequence[Tuple[str, str, bool]]) -> List[HandRow]:
	return [parse_row(example, name, highlight) for example, name, highlight in raw_rows]


def draw_reference_card(rows: Sequence[HandRow], output_path: Path, title_text: str) -> None:
	image = Image.new("RGB", (IMG_W, IMG_H), color=(255, 255, 255))
	draw = ImageDraw.Draw(image)

	title_font = load_font(44, bold=True)

	outer_margin = 22
	title_h = 62
	gap_after_title = 8
	bottom_margin = 18

	max_cards = max(len(row.example) for row in rows)

	table_x0 = outer_margin
	table_x1 = IMG_W - outer_margin
	table_w = table_x1 - table_x0

	col_gap = 8
	card_gap = 3
	inner_pad_x = 4

	title_w, title_text_h = text_size(draw, title_text, title_font)
	title_x = (IMG_W - title_w) // 2
	title_y = outer_margin
	draw.text((title_x, title_y), title_text, font=title_font, fill=(20, 20, 20))

	table_y0 = title_y + max(title_h, title_text_h + 4) + gap_after_title
	table_y1 = IMG_H - bottom_margin
	table_h = table_y1 - table_y0
	row_count = len(rows)
	row_gap = 4
	row_h = max(18, (table_h - (row_count - 1) * row_gap) // row_count)

	def widest_text(items: Sequence[str], font: ImageFont.ImageFont) -> int:
		width = 0
		for item in items:
			w, _ = text_size(draw, item, font)
			if w > width:
				width = w
		return width

	name_items = [row.name for row in rows]
	prob_items = [PROBABILITIES.get(row.name, "") for row in rows]

	desired_card_h = max(16, row_h - 6)
	desired_card_w = max(14, int(desired_card_h * 0.62))
	required_example_w = max_cards * desired_card_w + (max_cards - 1) * card_gap + 8

	# Find the largest body font that still allows maximum card size from row height.
	text_font = load_font(14, bold=False)
	suit_font = load_font(14, bold=False)
	best_layout: Tuple[int, int, int] | None = None
	for font_size in range(40, 13, -1):
		candidate = load_font(font_size, bold=False)
		name_col_w = widest_text(name_items, candidate) + 10
		prob_col_w = widest_text(prob_items, candidate) + 10
		example_col_w = table_w - name_col_w - prob_col_w - 2 * col_gap
		if example_col_w < required_example_w:
			continue
		_, text_h = text_size(draw, "Full House", candidate)
		if text_h + 6 > row_h:
			continue
		best_layout = (font_size, name_col_w, prob_col_w)
		break

	if best_layout is None:
		for font_size in range(40, 13, -1):
			candidate = load_font(font_size, bold=False)
			name_col_w = widest_text(name_items, candidate) + 10
			prob_col_w = widest_text(prob_items, candidate) + 10
			example_col_w = table_w - name_col_w - prob_col_w - 2 * col_gap
			if example_col_w < 90:
				continue
			_, text_h = text_size(draw, "Full House", candidate)
			if text_h + 6 > row_h:
				continue
			best_layout = (font_size, name_col_w, prob_col_w)
			break

	if best_layout is None:
		best_layout = (14, 130, 80)

	body_font_size, name_col_w, prob_col_w = best_layout
	text_font = load_font(body_font_size, bold=False)
	suit_font = load_font(max(14, body_font_size + 2), bold=False)
	center_suit_font = load_font(max(16, body_font_size + 5), bold=False)
	center_value_font = load_font(max(16, body_font_size + 5), bold=False)

	example_col_w = table_w - name_col_w - prob_col_w - 2 * col_gap
	card_w_by_width = max(14, (example_col_w - 8 - (max_cards - 1) * card_gap) // max_cards)
	row_card_h = max(16, row_h - 6)
	row_card_w = max(14, min(card_w_by_width, int(row_card_h * 0.62)))

	col1_x0 = table_x0
	col1_x1 = col1_x0 + example_col_w
	col2_x0 = col1_x1 + col_gap
	col2_x1 = col2_x0 + name_col_w
	col3_x0 = col2_x1 + col_gap
	col3_x1 = table_x1

	body_y0 = table_y0

	for i, row in enumerate(rows):
		ry0 = int(body_y0 + i * (row_h + row_gap))
		ry1 = int(ry0 + row_h)
		if ry1 > table_y1:
			break

		if row.highlight:
			draw.rectangle((table_x0 + 1, ry0 + 1, table_x1 - 1, ry1 - 1), fill=(255, 249, 206))

		ex_start_x = col1_x0 + inner_pad_x
		ex_y = ry0 + (ry1 - ry0 - row_card_h) // 2

		for j, card in enumerate(row.example):
			cx = ex_start_x + j * (row_card_w + card_gap)
			draw_example_card(
				draw,
				cx,
				ex_y,
				row_card_w,
				row_card_h,
				card,
				text_font,
				suit_font,
				center_suit_font,
				center_value_font,
			)

		name_text = row.name
		ntw, nth = text_size(draw, name_text, text_font)
		ny = ry0 + (ry1 - ry0 - nth) // 2
		draw.text((col2_x0 + 4, ny), name_text, font=text_font, fill=(20, 20, 20))

		prob_text = PROBABILITIES.get(row.name, "")
		ptw, pth = text_size(draw, prob_text, text_font)
		px = col3_x1 - 4 - ptw
		py = ry0 + (ry1 - ry0 - pth) // 2
		draw.text((px, py), prob_text, font=text_font, fill=(20, 20, 20))

	# Outer border around the full card image.
	draw.rectangle((0, 0, IMG_W - 1, IMG_H - 1), outline=(0, 0, 0), width=8)

	image.save(output_path, dpi=(DPI, DPI))


def main() -> None:
	rows_card_1 = build_rows(CARD_1_RAW)
	rows_card_2 = build_rows(CARD_2_RAW)
	rows_card_3 = build_rows(CARD_3_RAW)

	out1 = Path("hand_ranks_card_1.png")
	out2 = Path("hand_ranks_card_2.png")
	out3 = Path("hand_ranks_card_3.png")

	draw_reference_card(rows_card_1, out1, TITLE_TEXT)
	draw_reference_card(rows_card_2, out2, SECOND_CARD_TITLE_TEXT)
	draw_reference_card(rows_card_3, out3, THIRD_CARD_TITLE_TEXT)

	print(f"Created {out1}")
	print(f"Created {out2}")
	print(f"Created {out3}")


if __name__ == "__main__":
	main()
