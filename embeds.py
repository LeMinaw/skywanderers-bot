from discord import Embed, Colour


class ErrorEmbed(Embed):
    def __init__(self, error_message=None):
        super().__init__(
            type = 'rich',
            colour = Colour.red(),
            title = "Error :(",
            description = error_message or "No further information."
        )
