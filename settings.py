from dataclasses import dataclass
from enum import Enum
from typing import Dict

from dotenv import dotenv_values

from util import load, flush

values = dotenv_values()

token = values.get("DISCORD_TOKEN")
base_url = values.get("BASE_URL", "http://127.0.0.1:7860")
settings_path = "../data/settings.json"


class SamplerIndices(Enum):
    euler = "Euler"


@dataclass
class GuildSettings:
    guild_id: str
    neg_prompt: str = "blurry, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, artist name, bad eyes"
    steps: int = 20
    cfg_scale: int = 7
    denoising_strength: float = 0
    sampler_index: SamplerIndices = "Euler"
    width: int = 512
    height: int = 512

    def to_json(self):
        return self.__dict__


@dataclass
class SettingsCache:
    populated: bool = False
    by_guild: Dict[str, GuildSettings] = None

    @classmethod
    async def populate(cls) -> None:
        data = await load(path=settings_path)
        cls.by_guild = {}
        for guild in list(data.keys()):
            guild_data = data[guild]
            cls.by_guild[guild] = GuildSettings(
                guild_id=guild,
                neg_prompt=guild_data["neg_prompt"],
                steps=guild_data["steps"],
                cfg_scale=guild_data["cfg_scale"],
                denoising_strength=guild_data["denoising_strength"],
                sampler_index=guild_data["sampler_index"],
                width=guild_data["width"],
                height=guild_data["height"]
            )
        cls.populated = True

    @classmethod
    async def reset(cls) -> None:
        cls.populated = False
        cls.by_guild = None

    @classmethod
    async def write(cls):
        write_data = {
            guild_id: settings.to_json()
            for guild_id, settings in cls.by_guild.items()
        }
        await flush(path=settings_path, data=write_data)

    @classmethod
    async def find_by_guild_id(cls, guild_id: str) -> GuildSettings:
        if not cls.populated:
            await cls.populate()
        if guild_id not in cls.by_guild.keys():
            cls.by_guild[guild_id] = GuildSettings(guild_id=guild_id)
            await cls.write()
        return cls.by_guild[guild_id]

    @classmethod
    async def update(cls, settings: GuildSettings):
        cls.by_guild[settings.guild_id] = settings
        await cls.write()



