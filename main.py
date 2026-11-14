import flet as ft
import random


def secret_santa_derangement(names):
    """
    Genera un'estrazione casuale garantendo che
    nessuno estragga se stesso (disarrangiamento / derangement).
    """
    if len(names) < 2:
        return {}
    
    givers = list(names)
    receivers = list(names)
    
    # Tentativi di mescolamento finché nessuno pesca se stesso
    while True:
        random.shuffle(receivers)
        if all(givers[i] != receivers[i] for i in range(len(givers))):
            return dict(zip(givers, receivers))


def main(page: ft.Page):
    page.title = "🎅 Babbo Natale Segreto"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window.width = 400
    page.window.height = 700
    page.scroll = ft.ScrollMode.AUTO

    participants = []
    assignments = {}
    current_revealer_index = 0

    # UI Components - Screen 1 (Inserimento)
    name_input = ft.TextField(
        label="Nome partecipante",
        hint_text="Es. Marco",
        autofocus=True,
        expand=True,
    )
    
    list_column = ft.Column(spacing=8)
    error_banner = ft.Text(color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD)

    def update_participant_list():
        list_column.controls.clear()
        for idx, name in enumerate(participants):
            def make_delete_handler(index):
                return lambda _: remove_participant(index)

            list_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON, color=ft.Colors.RED_400),
                            ft.Text(name, size=16, weight=ft.FontWeight.W_500, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                on_click=make_delete_handler(idx),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ft.Colors.RED_50,
                    padding=10,
                    border_radius=10,
                )
            )
        page.update()

    def add_participant(e):
        name = name_input.value.strip()
        if not name:
            return
        if name in participants:
            error_banner.value = f"'{name}' è già nella lista!"
            page.update()
            return

        error_banner.value = ""
        participants.append(name)
        name_input.value = ""
        update_participant_list()
        name_input.focus()

    def remove_participant(idx):
        if 0 <= idx < len(participants):
            participants.pop(idx)
            update_participant_list()

    # Logica Estrazione e Modalità "Passa il telefono"
    reveal_title = ft.Text("", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    target_card_content = ft.Text("", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700, text_align=ft.TextAlign.CENTER)
    
    reveal_box = ft.Container(
        content=target_card_content,
        bgcolor=ft.Colors.RED_100,
        padding=30,
        border_radius=15,
        alignment=ft.alignment.center,
        visible=False,
    )
    
    show_button = ft.ElevatedButton("🎁 Premi per scoprire a chi devi fare il regalo", style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600))
    next_button = ft.ElevatedButton("Fatto! Passa al prossimo ➡️", visible=False, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700))

    def setup_reveal_step():
        nonlocal current_revealer_index
        giver = participants[current_revealer_index]
        reveal_title.value = f"📱 Passa il telefono a:\n🎅 {giver}"
        target_card_content.value = f"Devi fare il regalo a:\n🎄 {assignments[giver]} 🎄"
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
        
        assignments = secret_santa_derangement(participants)
        current_revealer_index = 0
        setup_reveal_step()
        
        page.views.append(
            ft.View(
                "/reveal",
                [
                    ft.AppBar(title=ft.Text("Estrazione Segreta"), bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.CARD_GIFTCARD, size=60, color=ft.Colors.RED_600),
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
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=20,
                    ),
                ],
            )
        )
        page.update()

    def show_finish_screen():
        page.views.clear()
        page.views.append(
            ft.View(
                "/finish",
                [
                    ft.AppBar(title=ft.Text("Finito!"), bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.CHECK_CIRCLE, size=80, color=ft.Colors.GREEN_600),
                                ft.Text("Tutti hanno visto il proprio destinatario!", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                ft.Text("I segreti sono al sicuro. Buono scambio regali! 🎄✨", size=16, text_align=ft.TextAlign.CENTER),
                                ft.ElevatedButton("Ricomincia da capo", on_click=reset_app),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=15,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                        padding=20,
                    ),
                ],
            )
        )
        page.update()

    def reset_app(e):
        nonlocal participants, assignments, current_revealer_index
        participants.clear()
        assignments.clear()
        current_revealer_index = 0
        page.views.clear()
        render_home()

    def render_home():
        update_participant_list()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(
                        title=ft.Text("🎅 Babbo Natale Segreto"),
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Column(
                        [
                            ft.Text("Partecipanti", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    name_input,
                                    ft.IconButton(
                                        icon=ft.Icons.ADD_CIRCLE,
                                        icon_size=36,
                                        icon_color=ft.Colors.RED_600,
                                        on_click=add_participant,
                                    ),
                                ],
                            ),
                            error_banner,
                            ft.Divider(),
                            list_column,
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.ElevatedButton(
                                "🎁 Avvia Estrazione",
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
                    ),
                ],
            )
        )
        page.update()

    render_home()


if __name__ == "__main__":
    # Nelle versioni recenti di flet (1.x+) si usa ft.run anziché ft.app
    ft.run(main)
