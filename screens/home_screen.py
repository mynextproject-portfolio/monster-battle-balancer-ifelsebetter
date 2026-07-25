import flet as ft
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_LG, BUTTON_WIDTH_LG,
    TEXT_SIZE_LG, TEXT_SIZE_XL
)
from translations import t, get_lang, set_lang


def home_screen(page: ft.Page, on_start, rebuild):
    """Render the home screen.

    Args:
        page: The Flet page object
        on_start: Callback function to navigate to monster selection
        rebuild: Callback to rebuild the current screen (for language toggle)
    """

    def toggle_language(e):
        """Switch between Japanese and English and rebuild the screen."""
        current = get_lang(page)
        set_lang(page, "en" if current == "ja" else "ja")
        rebuild()

    return ft.Container(
        content=ft.Column(
            [
                # Language toggle button in top-right
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            t(page, "language_label"),
                            icon=ft.Icons.TRANSLATE,
                            on_click=toggle_language,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_800,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Container(height=SPACING_XL),  # Spacer
                ft.Icon(
                    name=ft.Icons.CASTLE,
                    size=120,
                    color=ft.Colors.RED_400,
                ),
                ft.Container(height=SPACING_LG),
                ft.Text(
                    t(page, "app_title"),
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_400,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=SPACING_SM),
                ft.Text(
                    t(page, "app_subtitle"),
                    size=TEXT_SIZE_LG,
                    color=ft.Colors.RED_300,
                    text_align=ft.TextAlign.CENTER,
                    italic=True,
                ),
                ft.Container(height=SPACING_XL),
                ft.Container(
                    content=ft.Text(
                        t(page, "app_description"),
                        size=TEXT_SIZE_XL,
                        color=ft.Colors.GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=600,
                ),
                ft.Container(height=SPACING_XL * 2),
                ft.ElevatedButton(
                    t(page, "view_monsters"),
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                    on_click=on_start,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        padding=SPACING_SM,
    )
