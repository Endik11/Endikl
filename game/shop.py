from __future__ import annotations

from dataclasses import dataclass

import pygame

from .debug import log_error, log_event
from .menu import draw_background, draw_text
from .settings import COLORS, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from pathlib import Path
import json
from .economy import Catalog, EconomyManager, Wallet
from .platform_paths import data_path


@dataclass(frozen=True)
class ShopItem:
    id: str
    name: str
    category: str
    rarity: str
    description: str
    cost: int
    preview: str
    accent: tuple[int, int, int]


def build_shop_catalog() -> list[ShopItem]:
    return [
        ShopItem(
            id="ember_skin",
            name="Пепельный облик",
            category="skin",
            rarity="rare",
            description="Сильный кожаный скин с огненными акцентами.",
            cost=220,
            preview="Пепельный скин",
            accent=COLORS["red"],
        ),
        ShopItem(
            id="night_costume",
            name="Ночной костюм",
            category="costume",
            rarity="epic",
            description="Плотный костюм с тёмным силуэтом и золотыми вставками.",
            cost=360,
            preview="Тёмный костюм",
            accent=COLORS["violet"],
        ),
        ShopItem(
            id="crimson_color",
            name="Багряный оттенок",
            category="color",
            rarity="common",
            description="Мягкий алый оттенок для дополняющего стиля.",
            cost=140,
            preview="Багряный цвет",
            accent=COLORS["red"],
        ),
        ShopItem(
            id="ember_burst",
            name="Пепельный всплеск",
            category="hit_effect",
            rarity="epic",
            description="Эффект удара с коротким пламенным следом.",
            cost=320,
            preview="Эффект удара",
            accent=COLORS["gold"],
        ),
        ShopItem(
            id="flare_finish",
            name="Финал вспышки",
            category="victory_effect",
            rarity="legendary",
            description="Красивый эффект победы с лучами и искрами.",
            cost=520,
            preview="Эффект победы",
            accent=COLORS["gold"],
        ),
        ShopItem(
            id="storm_arena",
            name="Штормовая арена",
            category="arena",
            rarity="rare",
            description="Дополнительная арена с электрическим ритмом.",
            cost=280,
            preview="Новая арена",
            accent=COLORS["cyan"],
        ),
        ShopItem(
            id="midnight_theme",
            name="Тема полуночи",
            category="theme",
            rarity="rare",
            description="Музыкальная тема с глубоким и атмосферным тембром.",
            cost=260,
            preview="Музыкальная тема",
            accent=COLORS["blue"],
        ),
        ShopItem(
            id="combo_guide",
            name="Комбо-подсказка",
            category="misc",
            rarity="common",
            description="Полезный набор подсказок для обучения и тренировки.",
            cost=100,
            preview="Дополнительный предмет",
            accent=COLORS["cyan"],
        ),
    ]


_compatibility_shop_catalog = build_shop_catalog


def build_shop_catalog() -> list[ShopItem]:
    catalog = Catalog.load(data_path("shop_catalog.json"))
    strings = json.loads((root / "data/localization_ru.json").read_text(encoding="utf-8"))["strings"]
    items = []
    legacy_categories = {"palettes":"color","emblems":"misc","trails":"hit_effect","profile_frames":"theme","arena_variants":"arena","gallery_entries":"misc"}
    for item in catalog.items.values():
        color = tuple(item.preview.get("color") or item.preview.get("colors") or (79, 150, 214))
        items.append(ShopItem(item.id, strings.get(item.name_key, item.name_key), legacy_categories[item.category], "cosmetic", strings.get(item.description_key, item.description_key), item.price, str(item.preview), color))
    return items


class ShopScreen:
    def __init__(self) -> None:
        self.items = build_shop_catalog()
        self.category_index = 0
        self.selected_index = 0
        self.message = "Добро пожаловать в витрину предметов"
        log_event("Shop catalog loaded items=%s", len(self.items))
        self.categories = [
            ("skin", "Скины"),
            ("costume", "Костюмы"),
            ("color", "Цвета"),
            ("hit_effect", "Удары"),
            ("victory_effect", "Победа"),
            ("arena", "Арены"),
            ("theme", "Темы"),
            ("misc", "Предметы"),
        ]

        self.categories = [(category, category.replace("_", " ").title()) for category in sorted({item.category for item in self.items})]

    @property
    def category(self) -> str:
        return self.categories[self.category_index][0]

    def current_items(self) -> list[ShopItem]:
        return [item for item in self.items if item.category == self.category]

    def update(self, pressed: dict[str, bool], profile, save_manager, events: list[pygame.event.Event] | None = None) -> str | None:
        if events is None:
            events = []
        items = self.current_items()
        if items:
            if pressed.get("down"):
                self.selected_index = (self.selected_index + 1) % len(items)
            if pressed.get("up"):
                self.selected_index = (self.selected_index - 1) % len(items)
        if pressed.get("right"):
            self.category_index = (self.category_index + 1) % len(self.categories)
            self.selected_index = 0
        if pressed.get("left"):
            self.category_index = (self.category_index - 1) % len(self.categories)
            self.selected_index = 0
        if pressed.get("pause") or pressed.get("block"):
            return "back"
        if pressed.get("light_punch") or pressed.get("heavy_punch") or pressed.get("energy"):
            self._handle_action(profile, save_manager)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos, profile, save_manager)
        return None

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float, profile) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Магазин", (96, 72), COLORS["white"])
        draw_text(surface, fonts["small"], f"Монеты: {profile.currency}", (96, 152), COLORS["gold"])

        categories_panel = pygame.Rect(84, 214, 320, 340)
        pygame.draw.rect(surface, (24, 28, 34), categories_panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["gold"], categories_panel, 2, border_radius=10)
        for index, (_, label) in enumerate(self.categories):
            y = 244 + index * 34
            color = COLORS["gold"] if index == self.category_index else COLORS["white"]
            draw_text(surface, fonts["small"], label, (112, y), color)

        items = self.current_items()
        list_rect = pygame.Rect(440, 214, 320, 340)
        pygame.draw.rect(surface, (24, 28, 34), list_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["cyan"], list_rect, 2, border_radius=10)
        if items:
            for index, item in enumerate(items):
                y = 244 + index * 40
                selected = index == self.selected_index
                body_color = COLORS["gold"] if selected else COLORS["white"]
                status = "Куплено" if item.id in profile.purchased_items else "Доступно"
                draw_text(surface, fonts["small"], f"{item.name} [{status}]", (462, y), body_color)
        else:
            draw_text(surface, fonts["small"], "Нет товаров в этой категории", (462, 244), COLORS["muted"])

        preview_rect = pygame.Rect(790, 214, 380, 340)
        pygame.draw.rect(surface, (24, 28, 34), preview_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["gold"], preview_rect, 2, border_radius=10)
        item = items[self.selected_index] if items else None
        if item is not None:
            accent = item.accent
            pygame.draw.rect(surface, accent, pygame.Rect(814, 242, 332, 140), border_radius=8)
            draw_text(surface, fonts["menu"], item.name, (814, 400), COLORS["white"])
            draw_text(surface, fonts["body"], item.description, (814, 446), COLORS["muted"])
            draw_text(surface, fonts["body"], f"Редкость: {item.rarity}", (814, 490), COLORS["gold"])
            draw_text(surface, fonts["body"], f"Стоимость: {item.cost} монет", (814, 528), COLORS["gold"])
            if item.id in profile.purchased_items:
                draw_text(surface, fonts["small"], "Куплено и доступно к экипировке", (814, 564), COLORS["cyan"])
            else:
                draw_text(surface, fonts["small"], "Нажмите атаку, чтобы купить", (814, 564), COLORS["white"])

        draw_text(surface, fonts["body"], self.message, (96, 610), COLORS["white"])

    def _handle_action(self, profile, save_manager) -> None:
        items = self.current_items()
        if not items:
            return
        item = items[self.selected_index]
        if item.id in profile.purchased_items:
            save_manager.equip_item(item.category, item.id)
            self.message = f"{item.name} экипирован"
            return
        if profile.currency >= item.cost:
            try:
                save_manager.purchase_item(item.id, item.category, item.cost)
                self.message = f"{item.name} куплен"
            except Exception as exc:  # pragma: no cover - defensive fallback
                log_error("Failed to purchase shop item", exc)
                self.message = "Ошибка покупки"
        else:
            self.message = f"Нужно ещё {item.cost - profile.currency} монет"

    def _handle_action(self, profile, save_manager) -> None:
        items = self.current_items()
        if not items:
            return
        item = items[self.selected_index]
        if item.id in profile.purchased_items:
            save_manager.equip_item(item.category, item.id)
            self.message = "Equipped"
            return
        catalog = Catalog.load(data_path("shop_catalog.json"))
        transactions = set(getattr(profile, "economy_transactions", []))
        unlocks = set(profile.unlocked_fighters) | set(profile.unlocked_arenas) | set(getattr(profile, "received_reward_ids", []))
        economy = EconomyManager(Wallet(profile.currency), catalog, profile.purchased_items, transactions, unlocks=unlocks)
        result = economy.purchase(item.id, f"shop:{item.id}")
        if not result.success:
            self.message = result.code
            return
        before = (profile.currency, list(profile.purchased_items), list(getattr(profile, "economy_transactions", [])))
        profile.currency = economy.wallet.points
        profile.purchased_items = sorted(economy.inventory)
        profile.economy_transactions = sorted(economy.transactions)
        try:
            save_manager.save()
            self.message = "Purchased"
        except Exception as exc:
            profile.currency, profile.purchased_items, profile.economy_transactions = before
            log_error("Failed to persist shop transaction", exc)
            self.message = "Purchase failed"

    def _handle_mouse_click(self, pos: tuple[int, int], profile, save_manager) -> None:
        items = self.current_items()
        if not items:
            return
        catalog_rect = pygame.Rect(440, 214, 320, 340)
        if catalog_rect.collidepoint(pos):
            index = (pos[1] - 244) // 40
            if 0 <= index < len(items):
                self.selected_index = index
                self._handle_action(profile, save_manager)
        preview_rect = pygame.Rect(790, 214, 380, 340)
        if preview_rect.collidepoint(pos):
            self._handle_action(profile, save_manager)
