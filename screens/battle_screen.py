import flet as ft
from dnd_api import get_monster_details
from battle import simulate_battle
from ui_constants import (
    SPACING_SM, SPACING_LG, SPACING_XL,
    BUTTON_HEIGHT_LG, BUTTON_WIDTH_LG,
    TEXT_SIZE_MD, TEXT_SIZE_LG, TEXT_SIZE_XL,
)
from translations import t, get_lang, set_lang


def battle_screen(page: ft.Page, monster1_index: str, monster2_index: str, on_back, rebuild):
    """Render the battle screen showing combat result between two monsters.

    Args:
        page: The Flet page object
        monster1_index: Index of first monster
        monster2_index: Index of second monster
        on_back: Callback function to navigate back to cards screen
        rebuild: Callback to rebuild the current screen (for language toggle)
    """

    def toggle_language(e):
        """Switch between Japanese and English and rebuild the screen."""
        current = get_lang(page)
        set_lang(page, "en" if current == "ja" else "ja")
        rebuild()

    monster1 = get_monster_details(monster1_index)
    monster2 = get_monster_details(monster2_index)

    if not monster1 or not monster2:
        return ft.Column(
            [
                ft.Container(height=SPACING_XL),
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                ft.Container(height=SPACING_LG),
                ft.Text(t(page, "failed_to_load_details"), size=TEXT_SIZE_XL, color=ft.Colors.RED_400),
                ft.Text(t(page, "check_connection"), size=TEXT_SIZE_LG, color=ft.Colors.GREY_400),
                ft.Container(height=SPACING_XL),
                ft.ElevatedButton(
                    t(page, "back"),
                    on_click=on_back,
                    width=BUTTON_WIDTH_LG,
                    height=BUTTON_HEIGHT_LG,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    # Run fight using existing battle engine (simulate_battle)
    winner = simulate_battle(monster1, monster2)

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(height=SPACING_SM),
                # Header row
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=on_back,
                            tooltip=t(page, "back_to_cards"),
                        ),
                        ft.Text(
                            t(page, "battle_screen_title"),
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
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
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=SPACING_LG),

                # Winner Announcement Banner
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                t(page, "winner_label"),
                                size=TEXT_SIZE_LG,
                                color=ft.Colors.AMBER_300,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                winner.name,
                                size=36,
                                color=ft.Colors.AMBER_400,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=SPACING_LG,
                    border=ft.border.all(3, ft.Colors.AMBER_400),
                    border_radius=15,
                    bgcolor=ft.Colors.GREY_800,
                ),
                ft.Container(height=SPACING_XL),

                # Rematch / Back Buttons
                ft.Row(
                    [
                        ft.ElevatedButton(
                            t(page, "rematch_button"),
                            width=200,
                            height=BUTTON_HEIGHT_LG,
                            on_click=lambda e: rebuild(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.AMBER_700,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.ElevatedButton(
                            t(page, "back_to_cards"),
                            width=200,
                            height=BUTTON_HEIGHT_LG,
                            on_click=on_back,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.GREY_700,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=SPACING_LG,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        padding=SPACING_SM,
    )
