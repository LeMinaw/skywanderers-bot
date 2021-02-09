from discord import Embed, Colour
from discord.ext.commands import Cog, command
from datetime import datetime
from steamapi import SteamAPIClient, EPublishedFileQueryType, POST
from embeds import ErrorEmbed
import re
import settings


class StarshipEvoClient(SteamAPIClient):
    app_id = settings.STARSHIP_EVO_APPID

    async def search_blueprints(self, query, num=10, verbose=True):
        params = {
            'appid': self.app_id,
            'creator_appid': self.app_id,
            'query_type': EPublishedFileQueryType.RANKED_BY_TEXT_SEARCH.value,
            'cursor': '*',
            'numperpage': num,
            'requiredtags': 'Blueprint',
            'match_all_tags': False,
            'search_text': query,
            'return_vote_data': verbose,
            'return_tags': True,
            'return_kv_tags': verbose,
            'return_previews': verbose,
            'return_children': False,
            'return_short_description': True,
            'return_for_sale_data': False,
            'return_metadata': verbose,
            'return_playtime_stats': verbose,
        }
        return await self.request('IPublishedFileService/QueryFiles/v1/', params)
    
    async def get_blueprint(self, blueprint_id):
        params = {
            'itemcount': 1,
            'publishedfileids[0]': blueprint_id,
            'includevotes': True,
            'short_description': True
        }
        return await self.request('IPublishedFileService/GetDetails/v1', params)

    async def get_profile(self, profile_id):
        params = {'steamids': profile_id}
        response = await self.request('ISteamUser/GetPlayerSummaries/v0002/', params)
        return response['players'][0]


class WorkshopCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.steam_client = StarshipEvoClient(settings.STEAM_API_KEY)

    async def make_blueprint_embed(self, blueprint):
        author = await self.steam_client.get_profile(blueprint['creator'])
        url = ("https://steamcommunity.com/sharedfiles/filedetails/?id=%s"
                % blueprint['publishedfileid'])
        tags = [d['tag'] for d in blueprint['tags']]
        tags.remove('Blueprint')
        votes_up = blueprint['vote_data']['votes_up']
        votes_down = blueprint['vote_data']['votes_down']

        embed = Embed(
            type = 'rich',
            colour = Colour.blue(),
            title = blueprint['title'],
            description = blueprint['short_description'],
            url = url,
            timestamp = datetime.fromtimestamp(blueprint['time_updated'])
        )
        embed.set_author(
            name = author['personaname'],
            url = author['profileurl'],
            icon_url = author['avatar']
        )
        embed.set_image(url=blueprint['preview_url'])
        embed.add_field(
            name = "🏷 Tags",
            value = ', '.join(tags)
        )
        embed.add_field(
            name = "🗳 Votes",
            value = f"{votes_up}🔺 / {votes_down}🔻"
        )
        embed.add_field(
            name = "🔔 Subscriptions",
            value = blueprint['subscriptions']
        )
        embed.add_field(
            name = "🌟 Favorited",
            value = blueprint['favorited']
        )
        embed.set_footer(text="Workshop item")
        
        return embed
    
    @command(name='blueprint', aliases=['bp'])
    async def blueprint(self, ctx, *, name: str):
        """Display a nice card depicting a workshop blueprint."""
        response = await self.steam_client.search_blueprints(name, num=1)
        results = response['total']

        if not results:
            embed = ErrorEmbed(f"Blueprint {name} not found.")
        
        else:
            blueprint = response['publishedfiledetails'][0]
            embed = await self.make_blueprint_embed(blueprint)

            if results > 1:
                embed.set_footer(text=f"Warning: {results-1} other blueprint(s) matched your query.")

        await ctx.send(embed=embed)

    @command(name='blueprints', aliases=['bps', 'bpsearch', 'blueprintsearch'])
    async def blueprints(self, ctx, *, query: str):
        """Search a blueprint in the workshop and display most relevant results.
        It is also possible to set the number of results: `!bps eden scooter 15`.
        """
        last_arg = query.split(' ')[-1]
        try:
            num = int(last_arg)
        except ValueError:
            num = 5

        response = await self.steam_client.search_blueprints(query, num=min(num, 15))
        results = response['total']

        if results == 0:
            embed = ErrorEmbed("No blueprint matched your query.")
        
        else:
            blueprints = response['publishedfiledetails']
            entries = []
            for bp in blueprints:
                title = bp ['title']
                author = await self.steam_client.get_profile(bp['creator'])
                author = author['personaname']
                url = ("https://steamcommunity.com/sharedfiles/filedetails/?id=%s"
                        % bp['publishedfileid'])
                tags = [d['tag'] for d in bp['tags']]
                tags.remove('Blueprint')
                tags = ', '.join(tags)
                entries.append(f"⦿ **[{title}]({url})** by **{author}** (*{tags}*)")
            
            others = results - len(entries)
            if others > 0:
                entries.append(f"*...and {others} more*")

            embed = Embed(
                type = 'rich',
                colour = Colour.blue(),
                title = f"Search results: {query}",
                description = '\n'.join(entries)
            )
            embed.set_footer(text=f"{results} blueprint(s) matched your query.")
        
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_message(self, msg):
        match = re.search(
            r'https://steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)',
            msg.content
        )
        
        if match is not None:
            blueprint_id = int(match.group(1))
            response = await self.steam_client.get_blueprint(blueprint_id)
            blueprint = response['publishedfiledetails'][0]
            embed = await self.make_blueprint_embed(blueprint)
            await msg.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(WorkshopCog(bot))
