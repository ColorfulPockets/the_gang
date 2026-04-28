"""Generate a rules summary reference card image.

Output image is 2.5in x 3.5in at 300 DPI:
- rules_card.png
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont


DPI = 300
CARD_WIDTH_IN = 2.5
CARD_HEIGHT_IN = 3.5
IMG_W = int(CARD_WIDTH_IN * DPI)
IMG_H = int(CARD_HEIGHT_IN * DPI)


TITLE_TEXT = "Terms and Rules Clarifications"
RULES: List[str] = [
	"Cards are discarded face-down by default.",
	"If a chip is on its black side, it cannot be taken from a player.",
	"Wildcards can have any suit and value, and must be used to make the best hand possible unless otherwise specified.",
	"Kicker cards are cards that are part of your 5-card hand, but do nothing to determine the rank of your hand (i.e., they are used only as tiebreakers).",
	'"Sharing" means giving information to all players.',
	"Beneficial modifiers are optional and can be used at any point in the hand, unless otherwise specified.",
	"If a modifier could affect multiple cards and gives no way to distinguish them, the player chooses which card it affects.  If in the community, decide collectively.",
]

BOLD_TERMS = ["discarded", "black side", "Wildcards", "Sharing", "Kicker"]
BOLD_PATTERN = re.compile("|".join(re.escape(term) for term in sorted(BOLD_TERMS, key=len, reverse=True)))


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


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
	bbox = draw.textbbox((0, 0), text, font=font)
	return bbox[2] - bbox[0], bbox[3] - bbox[1]


def styled_segments(text: str) -> List[Tuple[str, bool]]:
	segments: List[Tuple[str, bool]] = []
	pos = 0
	for match in BOLD_PATTERN.finditer(text):
		if match.start() > pos:
			segments.append((text[pos:match.start()], False))
		segments.append((match.group(0), True))
		pos = match.end()
	if pos < len(text):
		segments.append((text[pos:], False))
	if not segments:
		segments.append((text, False))
	return segments


def styled_text_width(
	draw: ImageDraw.ImageDraw,
	text: str,
	normal_font: ImageFont.ImageFont,
	bold_font: ImageFont.ImageFont,
) -> int:
	total = 0
	for segment_text, is_bold in styled_segments(text):
		font = bold_font if is_bold else normal_font
		w, _ = text_size(draw, segment_text, font)
		total += w
	return total


def draw_styled_text(
	draw: ImageDraw.ImageDraw,
	x: int,
	y: int,
	text: str,
	normal_font: ImageFont.ImageFont,
	bold_font: ImageFont.ImageFont,
	fill: Tuple[int, int, int],
) -> None:
	cursor_x = x
	for segment_text, is_bold in styled_segments(text):
		font = bold_font if is_bold else normal_font
		draw.text((cursor_x, y), segment_text, font=font, fill=fill)
		w, _ = text_size(draw, segment_text, font)
		cursor_x += w


def wrap_text(
	draw: ImageDraw.ImageDraw,
	text: str,
	normal_font: ImageFont.ImageFont,
	bold_font: ImageFont.ImageFont,
	max_width: int,
) -> List[str]:
	words = text.split()
	if not words:
		return [""]

	lines: List[str] = []
	line = words[0]
	for word in words[1:]:
		candidate = f"{line} {word}"
		w = styled_text_width(draw, candidate, normal_font, bold_font)
		if w <= max_width:
			line = candidate
		else:
			lines.append(line)
			line = word
	lines.append(line)
	return lines


def layout_rules(
	draw: ImageDraw.ImageDraw,
	rules: List[str],
	normal_font: ImageFont.ImageFont,
	bold_font: ImageFont.ImageFont,
	text_col_width: int,
) -> List[List[str]]:
	"""Return wrapped lines grouped per rule."""
	groups: List[List[str]] = []
	for rule in rules:
		wrapped = wrap_text(draw, rule, normal_font, bold_font, text_col_width)
		groups.append(wrapped)
	return groups


def main() -> None:
	image = Image.new("RGB", (IMG_W, IMG_H), color=(255, 255, 255))
	draw = ImageDraw.Draw(image)

	margin = 28
	title_gap = 40
	line_gap = 3
	row_gap = 12
	row_pad_y = 7
	row_pad_x = 8

	content_x0 = margin
	content_x1 = IMG_W - margin
	content_w = content_x1 - content_x0
	text_col_w = content_w - row_pad_x * 2

	# Pick the largest readable font that still fits all content.
	selected_title_font = load_font(42, bold=True)
	selected_body_font = load_font(18, bold=False)
	selected_body_bold_font = load_font(18, bold=True)
	selected_groups: List[List[str]] = []
	selected_title_y = margin

	for body_size in range(36, 11, -1):
		body_font = load_font(body_size, bold=False)
		body_bold_font = load_font(body_size, bold=True)
		title_font = load_font(min(42, body_size + 16), bold=True)

		title_w, title_h = text_size(draw, TITLE_TEXT, title_font)
		title_x = (IMG_W - title_w) // 2
		title_y = margin
		_ = title_x  # suppress unused variable warning in static checks

		groups = layout_rules(draw, RULES, body_font, body_bold_font, text_col_w)
		_, line_h_normal = text_size(draw, "Ag", body_font)
		_, line_h_bold = text_size(draw, "Ag", body_bold_font)
		line_h = max(line_h_normal, line_h_bold)

		total_h = title_h + title_gap
		for group_index, group in enumerate(groups):
			row_h = len(group) * line_h + max(0, len(group) - 1) * line_gap + row_pad_y * 2
			total_h += row_h
			if group_index < len(groups) - 1:
				total_h += row_gap

		if title_y + total_h <= IMG_H - margin:
			selected_title_font = title_font
			selected_body_font = body_font
			selected_body_bold_font = body_bold_font
			selected_groups = groups
			selected_title_y = title_y
			break

	title_w, title_h = text_size(draw, TITLE_TEXT, selected_title_font)
	title_x = (IMG_W - title_w) // 2
	draw.text((title_x, selected_title_y), TITLE_TEXT, font=selected_title_font, fill=(20, 20, 20))

	text_x = content_x0 + row_pad_x
	y = selected_title_y + title_h + title_gap
	_, line_h_normal = text_size(draw, "Ag", selected_body_font)
	_, line_h_bold = text_size(draw, "Ag", selected_body_bold_font)
	line_h = max(line_h_normal, line_h_bold)

	for group_index, group in enumerate(selected_groups):
		row_h = len(group) * line_h + max(0, len(group) - 1) * line_gap + row_pad_y * 2
		row_y0 = y
		row_y1 = y + row_h
		draw.rounded_rectangle(
			(content_x0, row_y0, content_x1, row_y1),
			radius=8,
			fill=(247, 247, 247),
			outline=(210, 210, 210),
			width=1,
		)

		line_y = row_y0 + row_pad_y
		for line_index, line in enumerate(group):
			draw_styled_text(
				draw,
				text_x,
				line_y,
				line,
				selected_body_font,
				selected_body_bold_font,
				(20, 20, 20),
			)
			line_y += line_h
			if line_index < len(group) - 1:
				line_y += line_gap

		y = row_y1
		if group_index < len(selected_groups) - 1:
			y += row_gap

	# Match outer border style used in Reference_Cards.py.
	draw.rectangle((0, 0, IMG_W - 1, IMG_H - 1), outline=(0, 0, 0), width=8)

	out_path = Path("rules_card.png")
	image.save(out_path, dpi=(DPI, DPI))
	print(f"Created {out_path}")


if __name__ == "__main__":
	main()