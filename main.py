import random

import flet as ft


def secret_santa_derangement(names, exclusions=None):
    if len(names) < 2:
        return {}
    exclusions = exclusions or {}
    receivers = list(names)
    assignments = {}
    randomized_givers = list(names)
    random.shuffle(randomized_givers)

    def assign(index, remaining):
        if index == len(randomized_givers):
            return True
        giver = randomized_givers[index]
        choices = [
            receiver
            for receiver in remaining
            if receiver != giver and receiver != exclusions.get(giver)
        ]
        random.shuffle(choices)
        for receiver in choices:
            assignments[giver] = receiver
            if assign(index + 1, [item for item in remaining if item != receiver]):
                return True
            del assignments[giver]
        return False

    return assignments if assign(0, receivers) else None


def main(page: ft.Page):
    page.title = "🎅 Babbo Natale Segreto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F4F7F2"

    participants = []
    exclusions = {}
    assignments = {}
    current_revealer_index = 0

    name_input = ft.TextField(
        label="Nome partecipante",
        hint_text="Es. Marco",
        autofocus=True,
        expand=True,
        on_submit=lambda e: add_participant(e),
    )
    list_column = ft.Column(spacing=8)
    error_banner = ft.Text(color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD)

    def make_header(eyebrow, title, subtitle, icon):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=38, color="#F8E7B0"),
                        bgcolor="#FFFFFF1A",
                        padding=15,
                        border_radius=18,
                    ),
                    ft.Column(
                        [
                            ft.Text(eyebrow.upper(), size=11, weight=ft.FontWeight.BOLD, color="#E9C879"),
                            ft.Text(title, size=27, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(subtitle, size=13, color="#E5E9E2"),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                ],
                spacing=16,
            ),
            padding=22,
            border_radius=24,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#123D35", "#17634C", "#24805B"],
            ),
            shadow=ft.BoxShadow(blur_radius=22, color="#173F3526", offset=ft.Offset(0, 8)),
        )

    reveal_title = ft.Text(
        "", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
    )
    target_card_content = ft.Text(
        "",
        size=26,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED_700,
        text_align=ft.TextAlign.CENTER,
    )
    reveal_box = ft.Container(
        content=target_card_content,
        bgcolor="#FFF8E8",
        padding=32,
        border_radius=24,
        border=ft.Border.all(1, "#F0D99B"),
        shadow=ft.BoxShadow(blur_radius=20, color="#6B4E1720", offset=ft.Offset(0, 6)),
        alignment=ft.Alignment.CENTER,
        visible=False,
    )
    show_button = ft.FilledButton(
        "🎁 Premi per scoprire a chi devi fare il regalo",
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600),
    )
    next_button = ft.FilledButton(
        "Fatto! Passa al prossimo ➡️",
        visible=False,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700),
    )

    def update_participant_list():
        list_column.controls.clear()
        for giver in participants:
            options = [
                ft.dropdown.Option(name)
                for name in participants
                if name != giver
            ]
            selected = exclusions.get(giver)
            list_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.RED_400),
                                    ft.Text(giver, size=16, expand=True),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Rimuovi partecipante",
                                        on_click=lambda e, person=giver: remove_participant(person),
                                    ),
                                ]
                            ),
                            ft.Dropdown(
                                label="Non voglio pescare",
                                hint_text="Nessuna esclusione",
                                options=options,
                                value=selected,
                                on_select=lambda e, person=giver: set_exclusion(person, e.control.value),
                                expand=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    padding=14,
                    border_radius=18,
                    border=ft.Border.all(1, "#E6ECE5"),
                    shadow=ft.BoxShadow(blur_radius=9, color="#163D3510", offset=ft.Offset(0, 3)),
                )
            )
        page.update()

    def set_exclusion(giver, receiver):
        exclusions[giver] = receiver
        error_banner.value = ""
        page.update()

    def add_participant(e):
        name = (name_input.value or "").strip()
        if not name:
            return
        if any(existing.casefold() == name.casefold() for existing in participants):
            error_banner.value = f"'{name}' è già nella lista!"
            page.update()
            return

        error_banner.value = ""
        participants.append(name)
        exclusions[name] = None
        name_input.value = ""
        update_participant_list()
        name_input.focus()

    def remove_participant(name):
        if name in participants:
            participants.remove(name)
            exclusions.pop(name, None)
            for giver, excluded in exclusions.items():
                if excluded == name:
                    exclusions[giver] = None
            error_banner.value = ""
            update_participant_list()

    def setup_reveal_step():
        giver = participants[current_revealer_index]
        reveal_title.value = f"📱 Passa il telefono a:\n🎅 {giver}"
        target_card_content.value = (
            f"Devi fare il regalo a:\n🎄 {assignments[giver]} 🎄"
        )
        reveal_box.visible = False
        show_button.visible = True
        next_button.visible = False
        page.update()

    def on_show_clicked(e):
        reveal_box.visible = True
        show_button.visible = False
        next_button.visible = True
        page.update()

    def on_next_clicked(e):
        nonlocal current_revealer_index
        current_revealer_index += 1
        if current_revealer_index < len(participants):
            setup_reveal_step()
        else:
            show_finish_screen()

    show_button.on_click = on_show_clicked
    next_button.on_click = on_next_clicked

    def start_drawing(e):
        nonlocal assignments, current_revealer_index
        if len(participants) < 3:
            error_banner.value = "Inserisci almeno 3 partecipanti!"
            page.update()
            return

        error_banner.value = ""
        assignments = secret_santa_derangement(participants, exclusions)
        if assignments is None:
            error_banner.value = "Le esclusioni impostate non permettono un'estrazione valida. Modifica una o più esclusioni."
            page.update()
            return
        current_revealer_index = 0
        setup_reveal_step()
        page.views.clear()
        page.views.append(
            ft.View(
                route="/reveal",
                appbar=ft.AppBar(
                    title=ft.Text("Estrazione Segreta"),
                    bgcolor="#123D35",
                    color=ft.Colors.WHITE,
                ),
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                    make_header("Estrazione in corso", "Babbo Segreto", "Passa il telefono e scopri il tuo abbinamento", ft.Icons.CARD_GIFTCARD),
                                reveal_title,
                                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                                show_button,
                                reveal_box,
                                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                                next_button,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                        padding=20,
                    )
                ],
            )
        )
        page.update()

    def show_finish_screen():
        page.views.clear()
        page.views.append(
            ft.View(
                route="/finish",
                appbar=ft.AppBar(
                    title=ft.Text("Finito!"),
                    bgcolor="#123D35",
                    color=ft.Colors.WHITE,
                ),
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    size=80,
                                    color=ft.Colors.GREEN_600,
                                ),
                                ft.Text(
                                    "Tutti hanno visto il proprio destinatario!",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "I segreti sono al sicuro. Buono scambio regali! 🎄✨",
                                    size=16,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Button(
                                    content="Ricomincia da capo",
                                    on_click=reset_app,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                        padding=20,
                    )
                ],
            )
        )
        page.update()

    def reset_app(e):
        nonlocal current_revealer_index
        participants.clear()
        exclusions.clear()
        assignments.clear()
        current_revealer_index = 0
        name_input.value = ""
        error_banner.value = ""
        render_home()

    def render_home():
        page.views.clear()
        page.views.append(
            ft.View(
                route="/",
                appbar=ft.AppBar(
                    title=ft.Text("🎅 Babbo Natale Segreto"),
                    bgcolor="#123D35",
                    color=ft.Colors.WHITE,
                ),
                controls=[
                    ft.Column(
                        [
                            make_header("Edizione Natale", "Babbo Segreto", "La magia dei regali comincia da qui.", ft.Icons.CARD_GIFTCARD),
                            ft.Text(
                                "Crea il tuo gruppo",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color="#183B32",
                            ),
                            ft.Text("Aggiungi tutti e imposta le eventuali esclusioni.", size=13, color="#68776D"),
                            ft.Row(
                                [
                                    name_input,
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_CIRCLE,
                                        icon_size=36,
                                        icon_color=ft.Colors.RED_600,
                                        tooltip="Aggiungi partecipante",
                                        on_click=add_participant,
                                    ),
                                ],
                            ),
                            error_banner,
                            ft.Divider(),
                            list_column,
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.Button(
                                content="🎁 Avvia Estrazione",
                                icon=ft.Icons.CASINO,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_600,
                                    color=ft.Colors.WHITE,
                                    padding=15,
                                ),
                                on_click=start_drawing,
                                width=400,
                            ),
                        ],
                        expand=True,
                        spacing=15,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
                bgcolor="#F4F7F2",
                padding=20,
            )
        )
        page.update()

    render_home()


if __name__ == "__main__":
    ft.run(main)
