import os
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
LOCAL_DRONEFLY_DISCORD = HERE.parent / "dronefly-discord"
if LOCAL_DRONEFLY_DISCORD.exists() and str(LOCAL_DRONEFLY_DISCORD) not in sys.path:
    sys.path.insert(0, str(LOCAL_DRONEFLY_DISCORD))

import discord
from discord import app_commands
from types import SimpleNamespace
from dronefly.core.parsers.natural import NaturalParser
from dronefly.core.query import prepare_query_for_taxon
from dronefly.core.clients.inat import iNatClient
from dronefly.core.commands import get_query_taxon_formatter
from dronefly.discord.commands import InteractionContext
from dronefly.discord.menus import TaxonMenu, TaxonSource
from dronefly.core.models.config import Config
from dronefly.core.models.context import Context


class BombusTaxonMenu(TaxonMenu):
    def __init__(
        self,
        inat_client: iNatClient,
        source: TaxonSource,
        cog: SimpleNamespace,
        **kwargs,
    ):
        super().__init__(inat_client, source, cog=cog, **kwargs)

    async def start(self, interaction: discord.Interaction) -> None:
        ctx = InteractionContext(interaction)
        self.ctx = ctx
        self.bot = self.cog.bot
        self.author = ctx.author
        self.message = await self.send_initial_message(ctx)
        if hasattr(self.bot, 'active_views'):
            self.bot.active_views.add(self)

    async def cleanup(self):
        if hasattr(self.bot, 'active_views'):
            self.bot.active_views.discard(self)

    async def on_timeout(self):
        await super().on_timeout()
        await self.cleanup()


taxon = app_commands.Group(name="taxon", description="Taxon commands")


@taxon.command(name="show", description="Show a taxon")
@app_commands.describe(query="Search query for a taxon")
async def taxon_show(interaction: discord.Interaction, query: str) -> None:
    if not interaction.response.is_done():
        await interaction.response.defer()

    parsed_query = interaction.client.natural_parser.parse(query)
    query_response = await prepare_query_for_taxon(
        interaction.client.inat_client, parsed_query
    )
    taxon_formatter = await get_query_taxon_formatter(
        interaction.client.inat_client,
        query_response,
        with_url=False,
    )
    taxon_source = TaxonSource(taxon_formatter)
    taxon_menu = BombusTaxonMenu(
        interaction.client.inat_client,
        taxon_source,
        cog=SimpleNamespace(bot=interaction.client),
    )
    await taxon_menu.start(interaction=interaction)


@taxon.command(name="image", description="Show a taxon image")
@app_commands.describe(
    query="Search query for a taxon",
    number="Image number to show",
)
async def taxon_image(
    interaction: discord.Interaction,
    query: str | None = None,
    number: Optional[int] = 1,
) -> None:
    if query is None:
        await interaction.response.send_message(
            "Please provide a query for the taxon image.",
            ephemeral=False,
        )
        return

    if not interaction.response.is_done():
        await interaction.response.defer()

    parsed_query = interaction.client.natural_parser.parse(query)
    query_response = await prepare_query_for_taxon(
        interaction.client.inat_client, parsed_query
    )
    taxon_formatter = await get_query_taxon_formatter(
        interaction.client.inat_client,
        query_response,
        with_url=False,
        image_number=number,
        image_description="",
    )
    taxon_source = TaxonSource(taxon_formatter)
    taxon_menu = BombusTaxonMenu(
        interaction.client.inat_client,
        taxon_source,
        cog=SimpleNamespace(bot=interaction.client),
        image_number=number,
    )
    await taxon_menu.start(interaction=interaction)


class Bombus(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.inat_client = None
        self.natural_parser = NaturalParser()
        self.owner_ids = set()
        self.active_views: set[discord.ui.View] = set()

    async def setup_hook(self):
        self.inat_client = iNatClient(loop=self.loop)
        self.inat_client.ctx = Context(config=Config())
        self.tree.add_command(taxon)
        should_sync = os.getenv("BOMBUS_SYNC_COMMANDS", "true").lower() in (
            "1",
            "true",
            "yes",
        )
        if should_sync:
            await self.tree.sync()
        else:
            print("BOMBUS_SYNC_COMMANDS is false; app commands will not be synced.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Bot is ready.")


if __name__ == "__main__":
    TOKEN = os.getenv("BOMBUS_BOT_TOKEN")
    if not TOKEN:
        raise SystemExit("Please set the BOMBUS_BOT_TOKEN environment variable.")

    bot = Bombus()
    bot.run(TOKEN)
